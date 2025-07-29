import argparse
import datetime
import json
import logging
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

# Import shared configuration
from chATLAS_Scrape.gitlab.config import GitLabConfig, LoggingConfig
from chATLAS_Scrape.gitlab.rate_limiter import make_request_with_rate_limiting

# --- Configuration ---
config = GitLabConfig()
LoggingConfig.setup_basic_logging()

GET_FILE_CONTENTS = """
query GetMultipleRawBlobs($projectPath: ID!, $paths: [String!]!) {
  project(fullPath: $projectPath) {
    repository {
      blobs(paths: $paths) {
        nodes {
          path
          rawTextBlob
        }
      }
    }
  }
}
"""


def get_markdown_file_paths(project_id):
    """Search for Markdown files in a GitLab project."""
    headers = config.get_rest_headers()
    base_url = f"{config.REST_API_URL}/projects/{project_id}/search?scope=blobs&search=.md%20extension:md&per_page=100"

    markdown_files = set()
    page = 1

    while True:
        url = f"{base_url}&page={page}"
        response = make_request_with_rate_limiting(
            lambda current_url=url: requests.get(current_url, headers=headers, timeout=config.DEFAULT_TIMEOUT)
        )
        if not response:
            return []

        results = response.json()
        for item in results:
            path = item["path"]
            if path.lower().endswith(".md") and "changelog" not in path.lower():
                markdown_files.add(path)

        if not results or "X-Next-Page" not in response.headers:
            break
        page += 1

    return list(markdown_files)


def fetch_file_last_commit_date(project_id, file_path):
    """Fetch the date of the most recent commit for a file."""
    headers = config.get_rest_headers()
    encoded_path = urllib.parse.quote_plus(file_path)
    url = f"{config.REST_API_URL}/projects/{project_id}/repository/commits?path={encoded_path}&per_page=1"
    response = make_request_with_rate_limiting(
        lambda current_url=url: requests.get(current_url, headers=headers, timeout=config.DEFAULT_TIMEOUT)
    )
    if not response:
        return file_path, None

    try:
        commits = response.json()
        if commits:
            commit_date = str(datetime.datetime.fromisoformat(commits[0]["committed_date"]).date())
            return file_path, commit_date
    except (ValueError, KeyError) as e:
        logging.error(f"Failed to parse commit date for {file_path}: {e}")

    return file_path, None


def fetch_commit_dates_parallel(project_id, file_paths, max_workers=10):
    """Fetch commit dates for multiple files in parallel."""
    commit_dates = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {executor.submit(fetch_file_last_commit_date, project_id, path): path for path in file_paths}

        # Collect results
        for future, file_path in future_to_path.items():
            try:
                result_file_path, commit_date = future.result()
                commit_dates[result_file_path] = commit_date
            except Exception as e:
                logging.error(f"Failed to fetch commit date for {file_path}: {e}")
                commit_dates[file_path] = None

    return commit_dates


def get_file_contents_graphql(project_path, file_paths):
    """Fetch file contents using GraphQL API."""
    headers = config.get_graphql_headers()

    payload = {
        "query": GET_FILE_CONTENTS,
        "variables": {"projectPath": project_path, "paths": file_paths},
    }

    response = make_request_with_rate_limiting(
        lambda: requests.post(config.GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=config.GRAPHQL_TIMEOUT)
    )
    if not response:
        return None

    return response.json()


def get_file_contents_batched(project_path, file_paths, batch_size=100):
    """Fetch file contents in batches."""
    all_blobs = []
    for i in range(0, len(file_paths), batch_size):
        batch_paths = file_paths[i : i + batch_size]
        response = get_file_contents_graphql(project_path, batch_paths)
        if response and response.get("data"):
            all_blobs.extend(response["data"]["project"]["repository"]["blobs"]["nodes"])
    return all_blobs


def process_single_project(project_spec):
    """Process a single project - find and download markdown files."""
    project_id = project_spec.get("id")

    project_spec["markdown_files"] = []

    start_time = time.time()
    paths = get_markdown_file_paths(project_id)
    if not paths or len(paths) < GitLabConfig.MIN_NUM_MARKDOWN_FILES:
        return False

    files = get_file_contents_batched(project_spec["path"], paths)

    # Fetch commit dates in parallel (this is the slowest part)
    commit_dates = fetch_commit_dates_parallel(project_id, paths)

    for file in files:
        file_info = {
            "path": file["path"],
            "last_modified": commit_dates.get(file["path"]),
            "content": file["rawTextBlob"],
        }
        project_spec["markdown_files"].append(file_info)

    elapsed_time = time.time() - start_time
    logging.info(f"Processed {project_spec['path']}: {len(paths)} files in {elapsed_time:.2f}s")
    return project_spec


def parse_args(args):
    parser = argparse.ArgumentParser(description="Fetch markdown files from GitLab repositories")
    parser.add_argument("--input", type=str, help="Path to JSON file containing project data")
    parser.add_argument(
        "--output",
        type=str,
        default=f"gitlab_content_{datetime.datetime.now().strftime('%Y_%m_%d')}.json",
        help="Path where updated project data will be saved",
    )
    args = parser.parse_args(args)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return args


def main(args=None):
    """Main function to fetch and process markdown files from GitLab projects."""
    args = parse_args(args)

    with open(args.input) as f:
        projects_data = json.load(f)

    if not projects_data:
        raise ValueError("No projects provided in the input data.")

    logging.info(f"Processing {len(projects_data)} projects from {args.input}")

    start_time = time.time()
    processed_projects = []
    for project in projects_data:
        if (result := process_single_project(project)) is not False:
            processed_projects.append(result)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(processed_projects, f, indent=2)

    elapsed_time = time.time() - start_time
    logging.info(f"Processed {len(processed_projects)} projects in {elapsed_time:.2f}s")
    logging.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
