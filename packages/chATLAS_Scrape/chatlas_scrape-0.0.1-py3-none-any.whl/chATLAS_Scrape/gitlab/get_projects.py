import argparse
import datetime
import json
import re
from pathlib import Path

import requests

# Import shared configuration
from chATLAS_Scrape.gitlab.config import GitLabConfig, LoggingConfig
from chATLAS_Scrape.gitlab.rate_limiter import make_request_with_rate_limiting

# --- Configuration ---
config = GitLabConfig()
logger = LoggingConfig.get_logger(__name__)

# Set up logging
LoggingConfig.setup_basic_logging()

# --- Pre-filter Configurations ---
PROJECT_PATH_BLACKLIST = config.get_blacklist_lowercase()

# --- GraphQL Query
GET_PROJECTS = """
query GetAccessibleProjects($first: Int = 20, $after: String) {
  projects(first: $first, after: $after, archived: EXCLUDE, sort: "latest_activity_desc") {
    nodes {
      id
      name
      path
      fullPath
      webUrl
      description
      forksCount
      starCount
      group {
        id
        name
      }
      lastActivityAt
      repository {
        empty
        exists
        tree {
          lastCommit {
            committedDate
          }
        }
      }
      forkedFrom: forkedFrom {
        id
        nameWithNamespace
        webUrl
      }
    }
    pageInfo {
      hasNextPage
      endCursor
      startCursor
      hasPreviousPage
    }
  }
}
"""


def make_api_request(url, json_payload=None, timeout=None):
    """Make GraphQL API request with error handling."""
    if timeout is None:
        timeout = config.DEFAULT_TIMEOUT

    headers = config.get_graphql_headers()
    response = make_request_with_rate_limiting(
        lambda: requests.post(url, headers=headers, json=json_payload, timeout=timeout)
    )
    if not response:
        return None

    return response.json()


def fetch_projects_page(variables=None):
    """Fetch a single page of projects using GraphQL."""
    payload = {"query": GET_PROJECTS}
    if variables:
        payload["variables"] = variables
    return make_api_request(config.GRAPHQL_ENDPOINT, json_payload=payload)


def fetch_all_projects_generator(items_per_page=100, last_activity_days=120):
    """Generator that fetches all accessible projects and yields each project."""
    has_next_page = True
    current_cursor = None
    page_num = 1
    total_yielded = 0

    logger.info("Starting project fetch...")

    while has_next_page:
        variables = {"first": items_per_page, "after": current_cursor}
        response = fetch_projects_page(variables)

        if not response or "data" not in response:
            if response and "errors" in response:
                for error in response["errors"]:
                    logger.error(f"GraphQL error: {error.get('message')}")
            break

        projects_data = response["data"].get("projects", {})
        nodes = projects_data.get("nodes", [])

        logger.info(f"Fetched {len(nodes)} projects on page {page_num}...")

        should_continue = True
        for project in nodes:
            project["isFork"] = project.get("forkedFrom") is not None
            project["lastActivityDate"] = datetime.datetime.fromisoformat(project["lastActivityAt"]).date()

            repo = project.get("repository", {})
            if not repo or not repo.get("exists", False) or repo.get("empty", False):
                continue

            tree = repo.get("tree", {})
            last_commit = tree.get("lastCommit", {}) if tree else {}
            if not last_commit or not last_commit.get("committedDate"):
                continue

            project["lastCommitDate"] = datetime.datetime.fromisoformat(last_commit["committedDate"]).date()

            if last_activity_days > 0:
                cutoff_date = datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(days=last_activity_days)
                if project["lastActivityDate"] < cutoff_date:
                    should_continue = False
                    break

            yield project
            total_yielded += 1

        if not should_continue:
            logger.info("Reached activity cutoff date")
            break

        page_info = projects_data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        current_cursor = page_info.get("endCursor")
        page_num += 1

    logger.info(f"Fetched {total_yielded} projects total")


def check_mirror_status(project_id):
    """Check if a project is a pull mirror using REST API."""
    rest_endpoint = f"{config.BASE_URL}/api/v4/projects/{project_id}"
    headers = {
        "Authorization": f"Bearer {config.PRIVATE_TOKEN}",
        "Content-Type": "application/json",
    }

    response = make_request_with_rate_limiting(
        lambda: requests.get(rest_endpoint, headers=headers, timeout=config.DEFAULT_TIMEOUT)
    )
    if not response:
        logger.warning(f"Failed to check mirror status for project {project_id}")
        return False

    try:
        project_data = response.json()
        import_url = project_data.get("import_url")
        mirror = project_data.get("mirror", False)
        return bool(import_url or mirror)
    except (ValueError, KeyError) as e:
        logger.warning(f"Failed to parse mirror status for project {project_id}: {e}")
        return False


def apply_pre_filters(project, last_activity_days_filter):
    """Apply pre-filters to a project. Returns True if project passes all filters."""
    if project.get("isFork"):
        return False

    if project.get("group") is None:
        return False

    repo = project.get("repository", {})
    if not repo or not repo.get("exists", False) or repo.get("empty", False):
        return False

    if last_activity_days_filter > 0:
        cutoff_date = datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(days=last_activity_days_filter)
        if project["lastCommitDate"] < cutoff_date:
            return False

    if PROJECT_PATH_BLACKLIST:
        full_path = project.get("fullPath", "").lower()
        for blacklist_item in PROJECT_PATH_BLACKLIST:
            if blacklist_item in full_path:
                return False

        forked_from = project.get("forkedFrom")
        if forked_from:
            forked_path = forked_from.get("nameWithNamespace", "").lower()
            for blacklist_item in PROJECT_PATH_BLACKLIST:
                if blacklist_item in forked_path:
                    return False

    # Check if project is a pull mirror
    project_id = extract_numeric_id(project["id"])
    if project_id and check_mirror_status(project_id):
        return False

    return True


def filter_projects_generator(projects_iterable, last_activity_days_filter):
    """Generator that yields projects passing pre-filters."""
    count_passed = 0
    count_checked = 0

    for project in projects_iterable:
        count_checked += 1
        if apply_pre_filters(project, last_activity_days_filter):
            yield project
            count_passed += 1

    logger.info(f"Filtered: {count_passed}/{count_checked} projects passed")


def extract_numeric_id(gid):
    """Extract numeric ID from GitLab GID string."""
    match = re.search(r"/(\d+)$", gid)
    return match.group(1) if match else None


def clean_project_data_generator(projects_iterable):
    """Generator that yields cleaned project data."""
    for project in projects_iterable:
        yield {
            "source": "gitlab",
            "id": extract_numeric_id(project["id"]),
            "name": project["path"],
            "path": project["fullPath"],
            "url": project["webUrl"],
            "last_modified": str(project["lastCommitDate"]),
            "description": (project["description"] or "").replace("\n", " ").replace("\r", " "),
            "forks": project["forksCount"],
            "stars": project["starCount"],
        }


def parse_args(args):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch and pre-filter GitLab projects.")
    parser.add_argument(
        "--last-activity-days",
        type=int,
        default=1,
        help="Only include projects active in the last X days. Set to 0 to disable",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"gitlab_projects_{datetime.datetime.now().strftime('%Y_%m_%d')}.json",
        help="Output file name for the filtered projects.",
    )
    args = parser.parse_args(args)
    if args.last_activity_days < 0:
        raise ValueError("last_activity_days must be a non-negative integer.")
    return args


def main(args=None):
    args = parse_args(args)

    logger.info("Starting GitLab project fetching and pre-filtering process...")
    logger.info("Active filters:")
    logger.info("\t- Excluding archived projects")
    logger.info("\t- Excluding forks")
    logger.info("\t- Excluding mirrored projects")
    logger.info("\t- Excluding personal projects")
    logger.info(f"\t- Last commit < {args.last_activity_days} days ago")
    logger.info(f"\t- Path blacklist: {PROJECT_PATH_BLACKLIST}")

    logger.info("Starting to fetch projects...")
    project_fetcher = fetch_all_projects_generator(items_per_page=100, last_activity_days=args.last_activity_days)
    filtered_projects = filter_projects_generator(project_fetcher, args.last_activity_days)
    cleaned_projects = list(clean_project_data_generator(filtered_projects))

    if not cleaned_projects:
        raise ValueError("No projects passed the filters.")

    output_path = Path(args.output)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(cleaned_projects, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(cleaned_projects)} projects to {output_path}")


if __name__ == "__main__":
    main()
