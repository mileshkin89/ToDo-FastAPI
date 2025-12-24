from fastapi import Response

from apps.auth.utils import set_refresh_token_cookie


def test_set_refresh_token_cookie_sets_cookie():
    response = Response()
    refresh_token = "test-refresh-token"

    set_refresh_token_cookie(response, refresh_token)

    cookies = response.headers.get("set-cookie")
    assert cookies is not None


def test_set_refresh_token_cookie_attributes():
    response = Response()
    refresh_token = "test-refresh-token"

    set_refresh_token_cookie(response, refresh_token)

    cookie_header = response.headers["set-cookie"]

    assert "refresh_token=test-refresh-token" in cookie_header
    assert "HttpOnly" in cookie_header
    assert "SameSite=lax" in cookie_header
    assert "Max-Age=604800" in cookie_header
