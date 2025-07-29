"""
Test the SDK endpoints.
"""

from unittest.mock import Mock


def test_get_management_info(mock_session, client):
    """Test get_management_info functionality."""
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    mock_session.request.return_value = mock_response

    # Make request
    response = client.get_management_info()

    # Verify request was made correctly
    mock_session.request.assert_called_once_with(
        method="GET",
        url="https://api.fauthy.com/v1/management/",
        json=None,
        params=None,
    )
    assert response == mock_response
