"""Unit tests with a fake session (no network). Live check: LIVE=1 pytest -k live."""
import os

import pytest
import requests

from langchain_cyberwarex import CyberwarexReadPage, CyberwarexSearch, make_session


class FakeResp:
    def __init__(self, status, body=None, bad_json=False):
        self.status_code, self._body, self._bad = status, body, bad_json

    def json(self):
        if self._bad:
            raise ValueError("nope")
        return self._body


class FakeSession:
    def __init__(self, resp=None, exc=None):
        self.resp, self.exc, self.calls = resp, exc, []
        self.headers = {"X-Free-Trial": "1"}

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        if self.exc:
            raise self.exc
        return self.resp


def tool_with(cls, sess, **kw):
    t = cls(**kw)
    t._session = sess
    return t


def test_free_trial_session_has_header_and_no_key(monkeypatch):
    monkeypatch.delenv("CYBERWAREX_PRIVATE_KEY", raising=False)
    s = make_session()
    assert s.headers["X-Free-Trial"] == "1"
    assert "langchain-cyberwarex" in s.headers["User-Agent"]


def test_wallet_session_has_no_trial_header():
    pytest.importorskip("x402")
    s = make_session("0x" + "11" * 32)
    assert "X-Free-Trial" not in s.headers


def test_key_not_in_repr_or_dump():
    t = CyberwarexSearch(private_key="0xSECRET")
    assert "SECRET" not in repr(t) and "SECRET" not in str(t.model_dump())


def test_search_formats_rows():
    sess = FakeSession(FakeResp(200, {"results": [{"title": "T", "url": "https://u", "snippet": "S"}]}))
    out = tool_with(CyberwarexSearch, sess, max_results=3).invoke({"query": "x"})
    assert out == "T - https://u - S"
    assert sess.calls[0][1] == {"q": "x", "max_results": 3}


def test_search_snippet_is_one_short_line():
    sess = FakeSession(FakeResp(200, {"results": [{"title": "T", "url": "https://u", "snippet": "a\n\n b " + "x" * 500}]}))
    out = tool_with(CyberwarexSearch, sess).invoke({"query": "x"})
    assert "\n" not in out and out.endswith("...") and len(out) < 330


def test_search_empty():
    assert tool_with(CyberwarexSearch, FakeSession(FakeResp(200, {"results": []}))).invoke({"query": "x"}) == "No results."


@pytest.mark.parametrize("status,needle", [(402, "Payment required"), (429, "Rate limited"), (500, "HTTP 500")])
def test_http_errors_become_readable_text(status, needle):
    out = tool_with(CyberwarexSearch, FakeSession(FakeResp(status, {}))).invoke({"query": "x"})
    assert needle in out


def test_network_error_and_bad_json():
    out = tool_with(CyberwarexSearch, FakeSession(exc=requests.ConnectionError("down"))).invoke({"query": "x"})
    assert "request failed" in out
    out = tool_with(CyberwarexSearch, FakeSession(FakeResp(200, bad_json=True))).invoke({"query": "x"})
    assert "not JSON" in out


def test_read_page_caps_and_validates():
    sess = FakeSession(FakeResp(200, {"content": "a" * 50, "status": 200}))
    assert tool_with(CyberwarexReadPage, sess, max_chars=10).invoke({"url": "https://e.com"}) == "a" * 10
    assert "must start with" in tool_with(CyberwarexReadPage, sess).invoke({"url": "file:///etc/passwd"})
    assert len(sess.calls) == 1
    empty = FakeSession(FakeResp(200, {"content": "", "status": 404}))
    assert "no readable text" in tool_with(CyberwarexReadPage, empty).invoke({"url": "https://e.com"})


@pytest.mark.skipif(os.environ.get("LIVE") != "1", reason="live call, set LIVE=1")
def test_live_free_trial():
    out = CyberwarexSearch(max_results=3).invoke({"query": "LangChain tools"})
    assert out.count(" - http") >= 1, out
    page = CyberwarexReadPage().invoke({"url": "https://example.com"})
    assert "documentation examples" in page, page


def test_bad_key_is_not_echoed():
    pytest.importorskip("x402")
    with pytest.raises(ValueError) as e:
        make_session("0xNOTAKEY123")
    assert "NOTAKEY" not in str(e.value) and e.value.__cause__ is None


def test_402_with_wallet_says_wallet():
    sess = FakeSession(FakeResp(402, {}))
    sess.headers = {}
    assert "wallet could not pay" in tool_with(CyberwarexSearch, sess).invoke({"query": "x"})
