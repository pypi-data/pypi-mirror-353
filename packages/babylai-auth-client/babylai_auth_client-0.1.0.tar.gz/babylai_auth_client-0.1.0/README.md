# babylai_auth_client

A lightweight Python client for the BabylAI Auth API.  
With a single class (`BabylAiAuthClient`), you can fetch a client token—given a Tenant GUID and API Key—from `https://babylai.net/api/Auth/client/get-token`.  

## Table of Contents

1. [What Is This Package?](#what-is-this-package)  
2. [Installation](#installation)  
3. [Basic Usage (Standalone Python)](#basic-usage-standalone-python)  
4. [Django Integration](#django-integration)  
5. [Full Django Example (Code)](#full-django-example-code)  
6. [License](#license)  

## What Is This Package?

`babylai_auth_client` is a minimal Python wrapper around the BabylAI Auth endpoint:

```
POST https://babylai.net/api/Auth/client/get-token
Body: { "TenantId": "<GUID>", "ApiKey": "<string>" }
```

It returns JSON:
```json
{ "token": "<JWT-style string>", "expiresIn": <integer seconds> }
```

Under the hood, the package uses requests to handle HTTP and JSON parsing. On non-2xx responses, it raises a RuntimeError containing status code and response body. On success, it returns a small dataclass:

```python
@dataclass
class ClientTokenResponse:
    Token: str
    ExpiresIn: int
```

## Installation

### From PyPI (Recommended)
```bash
pip install babylai-auth-client
```
Note: The PyPI package name uses hyphens (babylai-auth-client). In code, you still import babylai_auth_client.client.

### From Source (Editable)
Clone or download the repository onto your machine:

```bash
git clone https://github.com/yourusername/babylai-auth-client-python.git
cd babylai-auth-client-python
```

Install in "editable" mode so that code changes are immediately available:

```bash
pip install -e .
```

Verify:

```bash
pip show babylai-auth-client
# Should report version, location: path/to/babylai-auth-client-python
```

## Basic Usage (Standalone Python)

Once installed, you can use BabylAiAuthClient in any Python script:

```python
import uuid
from babylai_auth_client.client import BabylAiAuthClient, ClientTokenResponse

def fetch_token():
    # 1) Specify your GUID and API key (replace with your real values)
    tenant_id = uuid.UUID("2176c188-8cb4-4fc3-8366-2d32e601f7e5")
    api_key = "I/22UK34I6xAhglfPXTwPAgUuVyJw8TdnG26ZLI5gYQ="
    base_url = "https://babylai.net/api/"

    # 2) Instantiate the client
    client = BabylAiAuthClient(
        tenant_id=tenant_id,
        api_key=api_key,
        base_url=base_url,  # optional if you want the default
    )

    try:
        # 3) Fetch the token
        resp: ClientTokenResponse = client.get_client_token()
        print("Token:", resp.Token)
        print("Expires In (seconds):", resp.ExpiresIn)
    except Exception as e:
        print("Failed to fetch token:", e)

if __name__ == "__main__":
    fetch_token()
```

What happens under the hood?

- A POST is sent to https://babylai.net/api/Auth/client/get-token.
- JSON payload:
  ```json
  {
    "TenantId": "<your GUID>",
    "ApiKey": "<your API key>"
  }
  ```
- On 200 OK, returns a ClientTokenResponse(Token=<str>, ExpiresIn=<int>).
- On non-2xx, raises RuntimeError("Failed to fetch token. Status code: XXX, Response body: …").

## Django Integration

Below is a step-by-step guide to exposing a GET /api/token endpoint in Django that uses babylai_auth_client to fetch the BabylAI token, mirroring the .NET TokenService we built earlier.

### 1. Install & Configure

Install the client (if you haven't already):

```bash
pip install babylai-auth-client
```

or, if you prefer your local copy:

```bash
cd path/to/babylai-auth-client-python
pip install -e .
```

Install Django + supporting packages (if not already):

```bash
pip install django djangorestframework django-cors-headers
```

Create a Django project & app (if starting from scratch):

```bash
django-admin startproject babylai_token_service
cd babylai_token_service
python manage.py startapp token_service
```

### 2. Define Settings

Open babylai_token_service/settings.py and make sure you have:

```python
import os
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "your-secret-key"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django defaults
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third‐party apps
    "corsheaders",             # for CORS
    "rest_framework",          # for APIView
    "token_service",           # our custom app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # ⚠️ Must come before CommonMiddleware:
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "babylai_token_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "babylai_token_service.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# International
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS: allow your front‐end origins (adjust as needed)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://localhost:3000",
    "http://localhost:5173",
]

# Disable automatic slash‐appending (so /api/Token works without redirect)
APPEND_SLASH = False

# ------------------------------------------------------------------
# BabylAI Credentials (replace with your own or load from env vars)
# ------------------------------------------------------------------
BABYLAI_TENANT_ID = uuid.UUID("2176c188-8cb4-4fc3-8366-2d32e601f7e5")
BABYLAI_API_KEY    = "I/22UK34I6xAhglfPXTwPAgUuVyJw8TdnG26ZLI5gYQ="
BABYLAI_BASE_URL   = "https://babylai.net/api/"
```

Tip: In production, load sensitive values from environment variables:

```python
import os, uuid

BABYLAI_TENANT_ID = uuid.UUID(os.getenv("BABYLAI_TENANT_ID"))
BABYLAI_API_KEY   = os.getenv("BABYLAI_API_KEY")
BABYLAI_BASE_URL  = os.getenv("BABYLAI_BASE_URL", "https://babylai.net/api/")
```

### 3. Write a Django View

Create or open token_service/views.py and insert:

```python
# token_service/views.py

import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from babylai_auth_client.client import BabylAiAuthClient, ClientTokenResponse
from requests.exceptions import RequestException


class TokenView(APIView):
    """
    GET /api/Token  →  { "token": "...", "expiresIn": ... }
    """

    def get(self, request, format=None):
        # Retrieve config from settings
        tenant_id: uuid.UUID = getattr(settings, "BABYLAI_TENANT_ID", None)
        api_key: str = getattr(settings, "BABYLAI_API_KEY", None)
        base_url: str = getattr(settings, "BABYLAI_BASE_URL", None)

        if tenant_id is None or api_key is None:
            return Response(
                {"error": "BabylAI credentials not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            client = BabylAiAuthClient(
                tenant_id=tenant_id,
                api_key=api_key,
                base_url=base_url
            )
            resp: ClientTokenResponse = client.get_client_token()
            return Response(
                {"token": resp.Token, "expiresIn": resp.ExpiresIn},
                status=status.HTTP_200_OK
            )

        except RequestException as http_ex:
            # Network / timeout / DNS errors
            return Response(
                {"error": "Upstream HTTP error", "details": str(http_ex)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except RuntimeError as re:
            # Our client raised because status != 200 or invalid JSON
            msg = str(re)
            if "Status code:" in msg:
                return Response(
                    {"error": "Upstream error", "details": msg},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            return Response(
                {"error": msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            # Fallback for any other exceptions
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

GET /api/Token
- Reads tenant_id, api_key, base_url from settings.py.
- Instantiates BabylAiAuthClient.
- Calls .get_client_token() → returns a dataclass with .Token and .ExpiresIn.
- Returns 200 OK JSON {"token": "...", "expiresIn": ...}.
- On upstream errors: returns 502 Bad Gateway with details.
- On any other exceptions: returns 500 Internal Server Error.

### 4. Wire URLs

#### 4.1. Project‐level urls.py
Open babylai_token_service/urls.py:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Note: no trailing slash → matches exactly /api/Token
    path("api/Token", include("token_service.urls")),
]
```

#### 4.2. App‐level urls.py
Create (or open) token_service/urls.py:

```python
from django.urls import path
from .views import TokenView

urlpatterns = [
    # Empty string matches exactly the prefix "api/Token"
    path("", TokenView.as_view(), name="get-token"),
]
```

Now:
- A request to GET http://<hostname>:<port>/api/Token
- Falls into TokenView.get()

### 5. Test the Endpoint

Run migrations (even with no custom models):

```bash
python manage.py migrate
```

Start the development server on port 7075 (to mirror your .NET example):

```bash
python manage.py runserver 7075
```

From your front‐end (e.g. http://localhost:4200), make a fetch call:

```javascript
fetch("http://127.0.0.1:7075/api/Token")
  .then((res) => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  })
  .then((data) => {
    console.log("Token:", data.token);
    console.log("Expires in (sec):", data.expiresIn);
    // store in state or localStorage...
  })
  .catch((err) => {
    console.error("Failed to fetch token:", err);
  });
```

Expected JSON response on success:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.…",
  "expiresIn": 900
}
```

If BabylAI returns an error (e.g. invalid API key):

```json
{
  "error": "Upstream error",
  "details": "Failed to fetch token. Status code: 401, Response body: '{\"error\":\"Invalid API key\"}'"
}
```

with HTTP status code 502 Bad Gateway.

## Full Django Example (Structure)

```
babylai_token_service/
├── manage.py
├── babylai_token_service/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── token_service/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

## License
AAU