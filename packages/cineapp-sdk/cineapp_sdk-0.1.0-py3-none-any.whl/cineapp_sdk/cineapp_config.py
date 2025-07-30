import os
from dotenv import load_dotenv

load_dotenv()

class CineConfig:
    """
    Configuration class for the CineAPP SDK client.

    Defines the base API URL and retry (backoff) behavior.
    """

    cine_base_url: str
    cine_backoff: bool
    cine_backoff_max_time: int

    def __init__(
        self,
        cine_base_url: str = None,
        backoff: bool = True,
        backoff_max_time: int = 60,
    ):
        """
        Initializes the CineConfig with optional overrides.

        Args:
            cine_base_url (str, optional): Base URL for the CineAPP API. Can be provided directly or via the CINE_API_BASE_URL environment variable.
            
            backoff (bool): Whether to enable retry logic with exponential backoff on failed API calls.
            
            backoff_max_time (int): Maximum duration (in seconds) to keep retrying a failed request before giving up.
        """

        self.cine_base_url = cine_base_url or os.getenv("CINE_API_BASE_URL")
        print(f"CINE_API_BASE_URL in CineConfig init: {self.cine_base_url}")

        if not self.cine_base_url:
            raise ValueError("Base URL is required !!! Please set the CINE_API_BASE_URL environment variable...")

        self.cine_backoff = backoff
        self.cine_backoff_max_time = backoff_max_time

    def __str__(self):
        """
        Returns a string representation of the config object,
        useful for debugging or logging.
        """
        return f"{self.cine_base_url} | Backoff: {self.cine_backoff} | Max Retry Time: {self.cine_backoff_max_time}s"
