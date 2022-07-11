
import logging.config
from typing import List
from aiopg.sa import engine, create_engine
from aiohttp_jsonrpc import handler
from crud_db_lavrukhin.crud_db.db_people.init_db import set, add, delete, get_list, get_count, get, get_all


logger = logging.getLogger('crud_db')

class JSONRPC_crud(handler.JSONRPCView):
    @property
    def _engine(self):
        return self.request.app['engine']


    async def rpc_add(self, person: dict) -> str:
        return await add(self._engine, person)

    async def rpc_set(self, person: dict):
        await set(self._engine, person)
        return 'Success'

    async def rpc_delete(self, id: str):
        await delete(self._engine, id)
        return 'Success'


    async def rpc_get_list(self,filter: dict, order: List[dict],limit: int, offset: int):
        return await get_list(self._engine, filter, order, limit, offset)


    async def rpc_get_count(self, filter: dict):
        return await get_count(self._engine, filter)

    async def rpc_get(self, id: str):
        return await get(self._engine, id)

    async def rpc_get_all(self):
        return await get_all(self._engine)
