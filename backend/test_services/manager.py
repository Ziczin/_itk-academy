from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import httpx
from test_services.endpoints import WALLETS, wallet_by_id, wallet_operation

JsonDict = dict[str, Any]
QueryDict = dict[str, Any]


@dataclass(frozen=True)
class WalletManager:
    client: httpx.AsyncClient

    async def get_wallets(
        self, *, params: Optional[QueryDict] = None
    ) -> httpx.Response:
        return await self.client.get(WALLETS, params=params)

    async def post_wallets(self, *, json: Optional[JsonDict] = None) -> httpx.Response:
        return await self.client.post(WALLETS, json=json if json is not None else {})

    async def get_wallet(
        self, wallet_id: str, *, params: Optional[QueryDict] = None
    ) -> httpx.Response:
        return await self.client.get(wallet_by_id(wallet_id), params=params)

    async def post_wallet_operation(
        self,
        wallet_id: str,
        *,
        json: JsonDict,
        params: Optional[QueryDict] = None,
    ) -> httpx.Response:
        return await self.client.post(
            wallet_operation(wallet_id), json=json, params=params
        )
