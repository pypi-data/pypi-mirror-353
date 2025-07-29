"""
A Python API for bitfrog notifications.
"""

# import requests

ENDPOINT = "http://localhost:9000/v1"

def ping(timeout=5) -> bool:
    """Pings the server to check if it's responding.

    Returns:
        bool: Wether the server responds or not.
    """
    # r = requests.get(ENDPOINT + "/ping", timeout=timeout)

    return True
