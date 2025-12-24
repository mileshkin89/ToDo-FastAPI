from datetime import datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException

from apps.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
from settings import settings


def test_create_access_token_contains_payload():
    data = {"sub": "1"}

    token = create_access_token(data)

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": False},
    )

    assert payload["sub"] == "1"
    assert "exp" in payload


def test_create_refresh_token_contains_payload():
    data = {"sub": "1"}

    token = create_refresh_token(data)

    payload = jwt.decode(
        token,
        settings.REFRESH_SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": False},
    )

    assert payload["sub"] == "1"
    assert "exp" in payload


def test_verify_access_token_valid():
    data = {"sub": "1"}
    token = create_access_token(data)

    payload = verify_access_token(token)

    assert payload["sub"] == "1"


def test_verify_access_token_expired():
    expired_payload = {
        "sub": "1",
        "exp": datetime.utcnow() - timedelta(seconds=1),
    }

    token = jwt.encode(
        expired_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc:
        verify_access_token(token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"


def test_verify_access_token_invalid():
    with pytest.raises(HTTPException) as exc:
        verify_access_token("invalid.token.string")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


def test_verify_refresh_token_valid():
    data = {"sub": "1"}
    token = create_refresh_token(data)

    payload = verify_refresh_token(token)

    assert payload["sub"] == "1"


def test_verify_refresh_token_expired():
    expired_payload = {
        "sub": "1",
        "exp": datetime.utcnow() - timedelta(seconds=1),
    }

    token = jwt.encode(
        expired_payload,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc:
        verify_refresh_token(token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Refresh token expired"


def test_verify_refresh_token_wrong_secret():
    data = {"sub": "1"}

    token = jwt.encode(
        data,
        "wrong_secret_key",
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc:
        verify_refresh_token(token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid refresh token"
