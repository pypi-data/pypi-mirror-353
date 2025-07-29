# src/babylai_auth_client/client.py

import requests
import uuid
from typing import Optional
from dataclasses import dataclass

@dataclass
class ClientTokenResponse:
    Token: str
    ExpiresIn: int


class BabylAiAuthClient:
    """
    A simple client that calls POST {base_url}/Auth/client/get-token
    with JSON {"TenantId": <UUID>, "ApiKey": "<string>"} to fetch a token.
    """

    def __init__(self,
                 tenant_id: uuid.UUID,
                 api_key: str,
                 base_url: str = "https://babylai.net/api/"):
        """
        :param tenant_id: UUID for the tenant.
        :param api_key:  API key string.
        :param base_url: Base URL of the BabylAI API (must end with '/').
        """
        if not str(base_url).endswith("/"):
            base_url = base_url + "/"
        self._base_url = base_url
        self._tenant_id = tenant_id
        self._api_key = api_key
        self._session = requests.Session()

    def get_client_token(self) -> ClientTokenResponse:
        """
        Calls POST {base_url}Auth/client/get-token
        with JSON {"TenantId": <GUID>, "ApiKey": "<string>"}.

        :raises RuntimeError on non-2xx or parsing errors.
        :returns ClientTokenResponse(Token=<str>, ExpiresIn=<int>)
        """
        url = f"{self._base_url}Auth/client/get-token"
        payload = {
            "TenantId": str(self._tenant_id),
            "ApiKey": self._api_key
        }

        resp = self._session.post(url, json=payload, timeout=10)
        # on non-2xx, include response body in the exception
        if not resp.ok:
            body_text = resp.text
            raise RuntimeError(f"Failed to fetch token. "
                               f"Status code: {resp.status_code}, "
                               f"Response body: {body_text!r}")

        # Attempt to parse JSON
        data = resp.json()  # may raise ValueError if invalid JSON
        # Expect data to have {"Token": "...", "ExpiresIn": 12345}
        token = data.get("token")
        expires_in = data.get("expiresIn")
        if token is None or expires_in is None:
            raise RuntimeError(f"Invalid response JSON: {data!r}")

        return ClientTokenResponse(Token=token, ExpiresIn=int(expires_in))
