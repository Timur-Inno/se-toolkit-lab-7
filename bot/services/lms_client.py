import httpx
from config import settings

def get(path: str) -> dict | list:
    url = f"{settings.lms_api_base_url}{path}"
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}
    try:
        r = httpx.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError as e:
        raise RuntimeError(f"connection refused ({settings.lms_api_base_url}). Check that services are running.") from e
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP {e.response.status_code} {e.response.reason_phrase}.") from e
    except Exception as e:
        raise RuntimeError(str(e)) from e
