from __future__ import annotations

import logging
import os
from typing import Any

from crudclient.client import Client

from tripletex.core.config import TripletexConfig, TripletexTestConfig

log = logging.getLogger(__name__)


class TripletexClient(Client):
    """
    Custom HTTP client for interacting with the Tripletex API.

    Handles configuration loading (production or test) and overrides
    the base request method to potentially skip response handling for DELETE requests.
    Rate limiting is now handled automatically by the crudclient library.
    """

    def __init__(
        self,
        config: TripletexConfig | None = None,
    ) -> None:
        """
        Initialize the Tripletex client.

        Args:
            config: An optional configuration object. If None, loads
                   TripletexTestConfig if DEBUG env var is "1", otherwise TripletexConfig.
        """
        if config is None:
            config = TripletexTestConfig() if os.getenv("DEBUG", "") == "1" else TripletexConfig()

        super().__init__(config=config)

        log.info("TripletexClient initialized with crudclient rate limiting")

    def _request(self, method: str, endpoint: str | None = None, url: str | None = None, **kwargs: Any) -> Any:
        """
        Sends an HTTP request to the Tripletex API.

        Overrides the base method to conditionally skip response handling,
        specifically for DELETE requests where Tripletex might return an empty body.

        Args:
            method: The HTTP method (e.g., 'GET', 'POST', 'DELETE').
            endpoint: The API endpoint path (appended to base_url).
            url: An absolute URL to use instead of base_url + endpoint.
            **kwargs: Additional arguments passed to the underlying request library.

        Returns:
            The processed response data (usually a dict or list) or raw response object,
            depending on the base client's implementation and the handle_response flag.
        """
        # Original handle_response logic (specific to TripletexClient)
        original_handle_response = method != "DELETE"
        # Get handle_response from kwargs if provided, otherwise use default
        handle_response_arg = kwargs.pop("handle_response", original_handle_response)

        # Call the parent _request method with the handle_response argument
        # The crudclient library now handles all rate limiting automatically
        return super()._request(method, endpoint=endpoint, url=url, handle_response=handle_response_arg, **kwargs)
