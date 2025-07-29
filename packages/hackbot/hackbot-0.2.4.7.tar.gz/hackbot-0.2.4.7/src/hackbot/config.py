from os import getenv
from typing import Union

HACKBOT_PORT = int(getenv("HACKBOT_PORT", "443"))
HACKBOT_ADDRESS = getenv("HACKBOT_ADDRESS", "https://app.hackbot.co")

def url_format(address: str, port: Union[int, None]) -> str:
    """Format the URL for the hackbot service."""
    scheme = address.split(":")[0]
    if len(address.split(":")) > 1:
        rest = ":".join(address.split(":")[1:])
    else:
        # No protocol specified, assume by port number if exists
        rest = ""
        if port is not None:
            if port == 80:
                return f"http://{address}"
            else:
                return f"https://{address}:{port}"
        else:
            return f"http://{address}"
    assert scheme in ["http", "https"], "Invalid URI scheme"
    return f"{scheme}:{rest}:{port}" if (port is not None) else f"{scheme}:{rest}"


HACKBOT_URL_BASE = url_format(HACKBOT_ADDRESS, HACKBOT_PORT)

def set_local_mode():
    """Set the local mode for the hackbot service."""
    global HACKBOT_ADDRESS, HACKBOT_PORT, HACKBOT_URL_BASE
    HACKBOT_ADDRESS = "http://localhost"
    HACKBOT_PORT = 5000
    HACKBOT_URL_BASE = url_format(HACKBOT_ADDRESS, HACKBOT_PORT)
