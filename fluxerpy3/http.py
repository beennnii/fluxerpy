"""
HTTP client for Fluxer API
"""

import aiohttp
from typing import Optional, Dict, Any
from .errors import AuthenticationError, NotFoundError, RateLimitError, APIError

try:
    from . import __version__
except ImportError:
    __version__ = "0.1.0"


class HTTPClient:
    """
    Handles HTTP requests to the Fluxer API
    """
    
    def __init__(self, base_url: str = "https://api.fluxer.app/v1", token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        """Initialize the HTTP session"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(family=2)  # force IPv4
            self.session = aiohttp.ClientSession(connector=connector)
            
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"fluxerpy3/{__version__}"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
        
    async def request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Make an HTTP request to the Fluxer API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to aiohttp
            
        Returns:
            Response data (JSON)
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If resource is not found
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        if self.session is None or self.session.closed:
            await self.start()
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))
        
        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                # Handle rate limiting
                if response.status == 429:
                    retry_after = response.headers.get("Retry-After")
                    raise RateLimitError(
                        "Rate limit exceeded",
                        retry_after=int(retry_after) if retry_after else None
                    )
                    
                # Handle authentication errors
                if response.status == 401:
                    raise AuthenticationError("Authentication failed")
                    
                # Handle not found
                if response.status == 404:
                    raise NotFoundError("Resource not found")
                    
                # Handle other errors
                if response.status >= 400:
                    error_data = await response.json() if response.content_type == "application/json" else {}
                    error_message = error_data.get("message", f"API error: {response.status}")
                    raise APIError(error_message, status_code=response.status)
                    
                # Return successful response
                if response.content_type == "application/json":
                    return await response.json()
                else:
                    return await response.text()
                    
        except aiohttp.ClientError as e:
            raise APIError(f"Request failed: {str(e)}")
            
    async def get(self, endpoint: str, **kwargs) -> Any:
        """Make a GET request"""
        return await self.request("GET", endpoint, **kwargs)
        
    async def post(self, endpoint: str, **kwargs) -> Any:
        """Make a POST request"""
        return await self.request("POST", endpoint, **kwargs)
        
    async def put(self, endpoint: str, **kwargs) -> Any:
        """Make a PUT request"""
        return await self.request("PUT", endpoint, **kwargs)
        
    async def delete(self, endpoint: str, **kwargs) -> Any:
        """Make a DELETE request"""
        return await self.request("DELETE", endpoint, **kwargs)
        
    async def patch(self, endpoint: str, **kwargs) -> Any:
        """Make a PATCH request"""
        return await self.request("PATCH", endpoint, **kwargs)
