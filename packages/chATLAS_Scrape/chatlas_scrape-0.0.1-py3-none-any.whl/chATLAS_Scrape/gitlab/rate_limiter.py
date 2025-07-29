import logging
import time
from collections.abc import Callable
from typing import Optional

import requests

from chATLAS_Scrape.gitlab.config import GitLabConfig

config = GitLabConfig()


def make_request_with_rate_limiting(request_func: Callable[[], requests.Response]) -> requests.Response | None:
    """
    Execute a request function with automatic rate limiting retry logic.

    Args:
        request_func: A callable that returns a requests.Response object

    Returns:
        The response object if successful, None if failed
    """
    while True:
        try:
            response = request_func()
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", str(config.RETRY_AFTER_DEFAULT)))
                logging.warning(f"Rate limited. Retrying in {retry_after}s")
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
