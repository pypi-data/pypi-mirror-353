from pathlib import Path

from chATLAS_Scrape.gitlab import get_markdown, get_projects


def test_get_projects():
    get_projects.main(args=["--last-activity-days", "1", "--output", "test_gitlab_projects.json"])


def test_get_markdown():
    path = Path(__file__).parent / "test_projects.json"
    get_markdown.main(args=["--input", str(path), "--output", "test_gitlab_content.json"])
