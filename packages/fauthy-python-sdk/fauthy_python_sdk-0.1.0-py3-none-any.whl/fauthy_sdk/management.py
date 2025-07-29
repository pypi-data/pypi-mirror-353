from typing import Any, Dict, Optional

import requests


class ManagementMixin:
    """Mixin class for Fauthy management API endpoints."""

    def get_management_info(self) -> requests.Response:
        """
        Get management info, use as ping endpoint.

        Returns:
            requests.Response: The API response containing management information
        """
        return self._make_request("GET", "")
