from urllib.parse import urlunparse

REED_API_BASE_URL = "www.reed.co.uk"
DEFAULT_API_PATH = "api"
DEFAULT_VERSION_STRING = "1.0"
DEFAULT_PROTOCOL = "https"


def get_base_url(
    protocol=DEFAULT_PROTOCOL,
    netloc=REED_API_BASE_URL,
    port=None,
    api_path=DEFAULT_API_PATH,
    version=DEFAULT_VERSION_STRING,
):
    if port:
        netloc = f"{netloc}:{port}"
    path = f"/{api_path}/{version}"

    url = urlunparse((protocol, netloc, path, "", "", ""))

    return url
