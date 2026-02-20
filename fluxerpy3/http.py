"""
HTTP client for Fluxer API
"""

import aiohttp
import json
import logging
import sys
from typing import Optional, Dict, Any
from .errors import AuthenticationError, NotFoundError, RateLimitError, APIError

# Debug logger – prints to stderr so it doesn't interfere with normal output
_log = logging.getLogger("fluxerpy3.http")
if not _log.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("[fluxerpy3] %(levelname)s %(message)s"))
    _log.addHandler(_handler)
_log.setLevel(logging.DEBUG)

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://fluxer.app",
            "Referer": "https://fluxer.app/",
        }
        if self.token:
            headers["Authorization"] = f"Bot {self.token}"
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

        # capture request body for debug logging (does not affect the actual request)
        _req_json = kwargs.get("json")
        _req_data = kwargs.get("data")
        if _req_json is not None:
            try:
                _req_body_display = json.dumps(_req_json, indent=2, ensure_ascii=False)
            except Exception:
                _req_body_display = str(_req_json)
        elif _req_data is not None:
            _req_body_display = str(_req_data)
        else:
            _req_body_display = "<no body>"
        
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
                    # --- detailed debug output ---
                    try:
                        body = await response.text()
                    except Exception as read_err:
                        body = f"<could not read response body: {read_err}>"

                    # try to pretty-print JSON body
                    try:
                        body_pretty = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
                    except Exception:
                        body_pretty = body

                    # mask token: show first 10 and last 4 chars
                    token_display = "None"
                    if self.token:
                        t = self.token
                        token_display = (
                            f"{t[:10]}...{t[-4:]}" if len(t) > 14 else "***"
                        )

                    sent_headers_display = {}
                    for k, v in headers.items():
                        if k == "Authorization":
                            t2 = v
                            sent_headers_display[k] = f"{t2[:10]}...{t2[-4:]}" if len(t2) > 14 else "***"
                        else:
                            sent_headers_display[k] = v

                    resp_headers_display = dict(response.headers)

                    _log.error(
                        "\n"
                        "══════════════════════════════════════════\n"
                        "  AUTHENTICATION FAILED (HTTP 401)\n"
                        "══════════════════════════════════════════\n"
                        "  REQUEST\n"
                        "  -------\n"
                        "  Method  : %s\n"
                        "  URL     : %s\n"
                        "  Token   : %s\n"
                        "  Headers : %s\n"
                        "\n"
                        "  RESPONSE\n"
                        "  --------\n"
                        "  Status  : %s\n"
                        "  Headers : %s\n"
                        "  Body    :\n%s\n"
                        "══════════════════════════════════════════",
                        method, url, token_display,
                        json.dumps(sent_headers_display, indent=4),
                        response.status,
                        json.dumps(resp_headers_display, indent=4),
                        body_pretty,
                    )
                    # --- end debug output ---
                    raise AuthenticationError(
                        f"Authentication failed (HTTP 401): {body}",
                        response_body=body,
                    )
                    
                # Handle not found
                if response.status == 404:
                    raise NotFoundError("Resource not found")
                    
                # Handle other errors
                if response.status >= 400:
                    try:
                        body = await response.text()
                    except Exception as read_err:
                        body = f"<could not read response body: {read_err}>"

                    try:
                        body_pretty = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
                    except Exception:
                        body_pretty = body

                    token_display = "None"
                    if self.token:
                        t = self.token
                        token_display = f"{t[:10]}...{t[-4:]}" if len(t) > 14 else "***"

                    sent_headers_display = {}
                    for k, v in headers.items():
                        if k == "Authorization":
                            t = v
                            sent_headers_display[k] = f"{t[:10]}...{t[-4:]}" if len(t) > 14 else "***"
                        else:
                            sent_headers_display[k] = v

                    _log.error(
                        "\n"
                        "══════════════════════════════════════════\n"
                        "  API ERROR (HTTP %s)\n"
                        "══════════════════════════════════════════\n"
                        "  REQUEST\n"
                        "  -------\n"
                        "  Method  : %s\n"
                        "  URL     : %s\n"
                        "  Headers : %s\n"
                        "  Body    :\n%s\n"
                        "\n"
                        "  RESPONSE\n"
                        "  --------\n"
                        "  Status  : %s\n"
                        "  Headers : %s\n"
                        "  Body    :\n%s\n"
                        "══════════════════════════════════════════",
                        response.status,
                        method, url,
                        json.dumps(sent_headers_display, indent=4),
                        _req_body_display,
                        response.status,
                        json.dumps(dict(response.headers), indent=4),
                        body_pretty,
                    )

                    try:
                        error_data = json.loads(body)
                    except Exception:
                        error_data = {}
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
