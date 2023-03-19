import json
from http import HTTPStatus

import httpx
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def billing_client() -> AsyncClient:
    async with httpx.AsyncClient(
            base_url="http://billing:8000",
            headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def auth_client() -> AsyncClient:
    async with httpx.AsyncClient(
            base_url="http://auth:5000",
            headers={"accept": "application/json"},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def client_tokens(auth_client):
    reg = await auth_client.post('/v1/auth/register?login=client&password=client&email=client@mail.com')
    assert reg.status_code == 200
    response = await auth_client.post('/v1/auth/login?login=client&password=client')
    res = json.loads(response.text)
    return res['access_token'], res['refresh_token']
