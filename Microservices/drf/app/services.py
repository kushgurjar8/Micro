import httpx
from django.conf import settings


class FastAPIError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class FastAPIClient:

    def __init__(self):
        self.client = httpx.Client(
            base_url=settings.FASTAPI_BASE_URL,
            timeout=5.0,
        )

    def request(self, method, path, **kwargs):
        try:
            response = self.client.request(method, path, **kwargs)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        except httpx.HTTPStatusError as e:
            raise FastAPIError(
                f"FastAPI returned status {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e

        except httpx.TimeoutException as e:
            raise FastAPIError("FastAPI service timed out", status_code=504) from e

        except httpx.RequestError as e:
            raise FastAPIError("Cannot connect to FastAPI service", status_code=503) from e

    def get(self, path, params=None, headers=None):
        return self.request("GET", path, params=params, headers=headers)

    def post(self, path, json=None, headers=None):
        return self.request("POST", path, json=json, headers=headers)


fastapi_client = FastAPIClient()