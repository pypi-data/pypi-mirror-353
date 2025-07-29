from asyncio import get_event_loop
from io import BytesIO
from typing import Any, Dict, Optional

from aiohttp import ClientError, ClientSession, ClientTimeout, ContentTypeError
from aiohttp_client_cache import CachedSession, SQLiteBackend
from loguru import logger

from routinepy.consts import API_URL, ROUTINE_HTML_CACHE_TTL


async def make_post_request(
    endpoint: str,
    data: Dict[str, str],
    timeout: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Makes an async POST request with error handling.

    Args:
        endpoint: API endpoint path
        data: Payload to send in the request
        timeout: Request timeout in seconds

    Returns:
        Dict containing response data or None if request fails
    """

    default_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Referer": API_URL,
    }

    url = f"{API_URL}/{endpoint.strip('/')}"

    timeout_config = ClientTimeout(total=timeout)
    async with ClientSession(timeout=timeout_config) as session:
        try:
            logger.debug(f"Request payload: {data}")
            logger.debug(f"Making request to {url}")

            async with session.post(
                url=url, data=data, headers=default_headers
            ) as resp:
                if not resp.ok:
                    logger.error(f"HTTP Error {resp.status}: {await resp.text()}")
                    resp.raise_for_status()

                return await resp.json()
        except ContentTypeError:
            logger.error(f"Invalid JSON response: {await resp.text()}")
        except ClientError as e:
            logger.error(f"Client error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")


async def make_get_request(
    url: str, timeout: int = 10, is_file: bool = False
) -> Optional[str | BytesIO]:
    """
    Makes an async GET request with error handling and caching.

    Args
    ----
    url
        API endpoint path
    timeout
        Request timeout in seconds
    is_file
        To not return response in text

    Returns
    -------
    dict
        containing response data
    None
        if request fails
    """
    cache = SQLiteBackend(
        name="bubt_routinepy_cache", expire_after=ROUTINE_HTML_CACHE_TTL
    )
    timeout_config = ClientTimeout(total=timeout)

    async with CachedSession(cache=cache, timeout=timeout_config) as session:
        logger.debug(f"Starting request: {url}")
        req_start = get_event_loop().time()
        try:
            async with session.get(url=url) as resp:
                if not resp.ok:
                    logger.error(f"HTTP Error {resp.status}: {await resp.text()}")
                    resp.raise_for_status()

                if not is_file:
                    return await resp.text()

                buffer = BytesIO()
                buffer.write(await resp.read())
                buffer.seek(0)

                return buffer
        except ClientError as e:
            logger.error(f"Client error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        finally:
            elapsed = get_event_loop().time() - req_start
            logger.debug(f"Finished request ({elapsed:.3f}s): {url}")
