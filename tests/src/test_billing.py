import json

import pytest


@pytest.mark.asyncio
async def test_products(billing_client, client_tokens):
    response = await billing_client.post(f"/api/v1/products", headers={
        "Authorization": f"Bearer {client_tokens[0]}"
    })
    res = json.loads(response.text)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_customer_create(billing_client, client_tokens):
    response = await billing_client.post(f"/api/v1/customer", headers={
        "Authorization": f"Bearer {client_tokens[0]}"
    })
    print(client_tokens[0])
    res = json.loads(response.text)
    assert response.status_code == 200
    assert res['customer_id'] is not None
