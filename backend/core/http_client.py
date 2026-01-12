"""
Shared HTTP client utilities.

Provides consistent timeout, error handling, and retry logic
for external API calls.
"""
import httpx
from typing import Optional, Any
from contextlib import asynccontextmanager


# Default timeout settings
DEFAULT_TIMEOUT = 30.0
OPENAI_TIMEOUT = 30.0


@asynccontextmanager
async def get_async_client(timeout: float = DEFAULT_TIMEOUT):
    """
    Context manager for async HTTP client with standard configuration.
    
    Usage:
        async with get_async_client() as client:
            response = await client.get(url)
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        yield client


def get_sync_client(timeout: float = DEFAULT_TIMEOUT) -> httpx.Client:
    """
    Create a sync HTTP client with standard configuration.
    
    Note: Caller is responsible for closing the client.
    
    Usage:
        with get_sync_client() as client:
            response = client.get(url)
    """
    return httpx.Client(timeout=timeout)


async def post_json(
    url: str,
    json_data: dict,
    headers: Optional[dict] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> tuple[int, dict]:
    """
    Send async POST request with JSON body.
    
    Returns:
        Tuple of (status_code, response_json)
    
    Raises:
        httpx.TimeoutException: On timeout
        httpx.HTTPError: On other HTTP errors
    """
    async with get_async_client(timeout) as client:
        response = await client.post(url, json=json_data, headers=headers)
        return response.status_code, response.json()


def build_auth_header(api_key: str) -> dict[str, str]:
    """Build Authorization header for Bearer token auth."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
