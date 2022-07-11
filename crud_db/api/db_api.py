import logging.config
from typing import List
from aiohttp_jsonrpc import handler
from crud_db_lavrukhin.crud_db.db_people.init_db import set_user, add, delete, get_list, get_count, get, get_all

logger = logging.getLogger('crud_db')


class JsonrpcCrud(handler.JSONRPCView):
    @property
    def _engine(self):
        return self.request.app['engine']

    async def rpc_add(self, user: dict) -> str:
        return await add(self._engine, user)

    async def rpc_set_user(self, user: dict):
        await set_user(self._engine, user)
        return 'Success'

    async def rpc_delete(self, user_id: str):
        await delete(self._engine, user_id)
        return 'Success'

    async def rpc_get_list(self, user_filter: dict, order: List[dict], limit: int, offset: int):
        return await get_list(self._engine, user_filter, order, limit, offset)

    async def rpc_get_count(self, user_filter: dict):
        return await get_count(self._engine, user_filter)

    async def rpc_get(self, user_id: str):
        return await get(self._engine, user_id)

    async def rpc_get_all(self):
        return await get_all(self._engine)
