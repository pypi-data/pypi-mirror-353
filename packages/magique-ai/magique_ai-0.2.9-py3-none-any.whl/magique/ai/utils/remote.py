import asyncio
from magique.client import connect_to_server, ServiceProxy, MagiqueError

from ..constant import SERVER_URLS
from ..utils.log import logger


current_server_url = None


async def connect_remote(
        service_name_or_id: str,
        server_url: str | list[str] | None = None,
        server_timeout: float = 2.0,
        service_timeout: float = 1.0,
        time_delta: float = 0.5,
        try_direct_connection: bool = True,
        ) -> ServiceProxy:
    if server_url is None:
        server_urls = SERVER_URLS
    elif isinstance(server_url, str):
        server_urls = [server_url]
    else:
        server_urls = server_url

    server = None
    async def _get_server(url: str):
        nonlocal server
        while server is None:
            try:
                server = await connect_to_server(url)
            except Exception:
                await asyncio.sleep(time_delta)

    service = None

    async def _get_service():
        nonlocal service
        while service is None:
            try:
                service = await server.get_service(service_name_or_id, try_direct_connection=try_direct_connection)
            except MagiqueError:
                await asyncio.sleep(time_delta)

    async def _search_available_server_then_get_service():
        global current_server_url
        for url in server_urls:
            if url == current_server_url:
                continue
            try:
                logger.debug(f"Trying to connect to server {url}")
                await asyncio.wait_for(_get_server(url), server_timeout)
                if server is None:
                    continue
                current_server_url = url
                logger.debug(f"Connected to server {url}")
                await asyncio.wait_for(_get_service(), service_timeout)
                if service is None:
                    logger.debug(f"Service {service_name_or_id} is not available on server {url}")
                    continue
                logger.debug(f"Service {service_name_or_id} is available on server {url}")
                break
            except asyncio.TimeoutError:
                logger.debug(f"Server {url} is not available")
                continue
        if server is None or service is None:
            raise asyncio.TimeoutError(
                f"No server is available for {service_name_or_id} service in {server_urls}")

    if current_server_url is not None:
        try:
            await asyncio.wait_for(_get_server(current_server_url), server_timeout)
            await asyncio.wait_for(_get_service(), service_timeout)
        except asyncio.TimeoutError:
            logger.debug(f"Current server {current_server_url} is not available")
            await _search_available_server_then_get_service()
    else:
        await _search_available_server_then_get_service()

    return service


def toolset_cli(toolset_type, default_service_name: str):
    import fire

    async def main(service_name: str = default_service_name, **kwargs):
        toolset = toolset_type(service_name, **kwargs)
        await toolset.run()

    fire.Fire(main)
