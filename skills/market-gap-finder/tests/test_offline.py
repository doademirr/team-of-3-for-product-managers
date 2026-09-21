"""Offline adapter tests — prove the parsing/contract logic without network.

Fixtures mirror the real shapes: Apple's customerreviews RSS-as-JSON feed, and
google-play-scraper's review dicts. Run: `PYTHONPATH=. python tests/test_offline.py`
(the live network round-trip is verified separately, by hand — see PROGRESS.md).
"""

from __future__ import annotations

import datetime

import tempfile

import requests

from gap_finder.ingest import apple, google_play, trustpilot
from gap_finder.ingest import base
from gap_finder.ingest.base import BlockedError
from gap_finder import handoff, discovery, synthesis, report, cli
from gap_finder.discovery import Player
from gap_finder.schema import Source, FetchStatus, SourceResult, Review


class FakeResp:
    def __init__(self, payload, status=200):
        self._p = payload
        self.status_code = status
        self.text = ""

    def raise_for_status(self):
        pass

    def json(self):
        return self._p


# --- Apple: real feed shape (entry[0] is app metadata, no im:rating) ---
_APP_META = {"im:name": {"label": "MyFitnessPal"}, "id": {"label": "app"}}
_REVIEW = {
    "im:rating": {"label": "4"},
    "im:version": {"label": "24.1"},
    "title": {"label": "Solid tracker"},
    "content": {"label": "Great for macros but the ads are annoying"},
    "updated": {"label": "2026-09-01T10:00:00-07:00"},
    "id": {"label": "https://itunes.apple.com/review/1"},
}
_REVIEW_2 = {**_REVIEW, "im:rating": {"label": "1"},
             "content": {"label": "Crashes constantly since the update"}}


def test_apple_pull_parses_and_stops():
    a = apple.AppleAdapter()
    calls = {"n": 0}

    def fake_get(url, timeout=20, **kw):
        calls["n"] += 1
        if calls["n"] == 1:                       # first storefront page: 2 reviews
            return FakeResp({"feed": {"entry": [_APP_META, _REVIEW, _REVIEW_2]}})
        return FakeResp({"feed": {"entry": [_APP_META]}})  # next pages: app meta only -> stop

    a.session.get = fake_get
    res = a.pull("MyFitnessPal", {"app_id": "123", "url": "http://store"}, limit=50)
    assert res.status == FetchStatus.OK, res.status
    assert len(res.reviews) == 2, len(res.reviews)
    assert res.reviews[0].rating == 4.0
    assert res.reviews[1].rating == 1.0
    assert "macros" in res.reviews[0].text
    assert res.reviews[0].source == Source.APPLE
    assert res.reviews[0].source_metadata["country"] in ("gb", "us")
    print(f"  apple pull OK: {len(res.reviews)} reviews, ratings {[r.rating for r in res.reviews]}")


def test_apple_empty_is_fail_closed():
    a = apple.AppleAdapter()
    a.session.get = lambda url, timeout=20, **kw: FakeResp({"feed": {"entry": [_APP_META]}})
    res = a.pull("Ghost", {"app_id": "0", "url": None}, limit=50)
    assert res.status == FetchStatus.EMPTY, res.status   # NOT "ok with 0 complaints"
    assert res.reviews == []
    print("  apple empty -> FetchStatus.EMPTY (fail-closed) OK")


# --- Google Play: patch the module-level library functions ---
def test_gplay_probe_and_pull():
    gp = google_play
    orig = (gp.search, gp.app, gp.reviews)
    try:
        gp.search = lambda q, **k: [{"appId": "com.mfp.android", "title": "MyFitnessPal",
                                     "developer": "MFP Inc"}]
        gp.app = lambda aid, **k: {"reviews": 120000}
        gp.reviews = lambda aid, **k: ([
            {"content": "Love the barcode scanner", "score": 5,
             "at": datetime.datetime(2026, 9, 1), "thumbsUpCount": 3},
            {"content": "Paywall everywhere now", "score": 2,
             "at": datetime.datetime(2026, 8, 20), "thumbsUpCount": 10},
        ], "token")

        a = gp.GooglePlayAdapter()
        loc = a.probe("MyFitnessPal", {})
        assert loc["app_id"] == "com.mfp.android", loc
        assert loc["review_count"] == 120000, loc
        res = a.pull("MyFitnessPal", loc, limit=50)
        assert res.status == FetchStatus.OK and len(res.reviews) == 2
        assert res.reviews[0].rating == 5.0 and "barcode" in res.reviews[0].text
        assert res.reviews[1].rating == 2.0
        assert res.reviews[0].source == Source.GOOGLE_PLAY
        print(f"  gplay probe+pull OK: count={loc['review_count']}, {len(res.reviews)} reviews")
    finally:
        gp.search, gp.app, gp.reviews = orig


# --- Block detector (the wrapper Codex C kept) ---
def test_block_detector():
    assert base.looks_blocked(FakeResp({}, status=403)) is not None
    assert base.looks_blocked(FakeResp({}, status=429)) is not None
    captcha = FakeResp({}, status=200); captcha.text = "Please complete the CAPTCHA to continue"
    assert base.looks_blocked(captcha) is not None      # silent 200 block caught
    ok = FakeResp({}, status=200); ok.text = "<html>normal reviews page</html>"
    assert base.looks_blocked(ok) is None
    print("  block detector OK: 403/429/CAPTCHA flagged, clean 200 passes")


# --- Trustpilot: __NEXT_DATA__ JSON parse + block -> handoff ---
_TP_HTML = """<html><head>
<script id="__NEXT_DATA__" type="application/json">
{"props":{"pageProps":{
 "businessUnit":{"displayName":"MyFitnessPal","numberOfReviews":{"total":3456}},
 "reviews":[
  {"title":"Awful support","text":"Could not cancel my subscription for months",
   "rating":1,"dates":{"publishedDate":"2026-08-01T00:00:00Z"},"likes":2,
   "consumer":{"displayName":"Jane"}},
  {"title":"","text":"Great for logging food","rating":5,
   "dates":{"publishedDate":"2026-08-05T00:00:00Z"},"likes":0,
   "consumer":{"displayName":"Bob"}}
 ]}}}
</script></head><body></body></html>"""

_TP_EMPTY = _TP_HTML.replace('"reviews":[', '"reviews_x":[')  # no reviews key -> stop


def _tp_patch(fn):
    """Patch trustpilot.guarded_fetch for the duration of a test."""
    orig = trustpilot.guarded_fetch
    trustpilot.guarded_fetch = fn
    return orig


def test_trustpilot_probe_and_pull():
    orig = _tp_patch(lambda url, **kw: _tp_resp(url))
    try:
        a = trustpilot.TrustpilotAdapter()
        loc = a.probe("MyFitnessPal", {"domain": "www.myfitnesspal.com"})
        assert loc and loc["review_count"] == 3456, loc
        assert loc["matched_name"] == "MyFitnessPal"
        res = a.pull("MyFitnessPal", loc, limit=50)
        assert res.status == FetchStatus.OK and len(res.reviews) == 2, res.status
        assert res.reviews[0].rating == 1.0 and "cancel" in res.reviews[0].text
        assert res.reviews[0].source == Source.TRUSTPILOT
        print(f"  trustpilot probe+pull OK: count={loc['review_count']}, {len(res.reviews)} reviews")
    finally:
        trustpilot.guarded_fetch = orig


def _tp_resp(url):
    """Page 1 -> reviews; page 2+ -> no reviews (stop)."""
    return FakeResp_text(_TP_EMPTY if "page=" in url else _TP_HTML)


def test_trustpilot_probe_needs_domain():
    a = trustpilot.TrustpilotAdapter()
    assert a.probe("MyFitnessPal", {}) is None   # no domain hint -> can't locate
    print("  trustpilot probe without domain -> None OK")


def test_trustpilot_block_triggers_handoff():
    def blocked(url, **kw):
        raise BlockedError(url, "HTTP 403")
    orig = _tp_patch(blocked)
    try:
        a = trustpilot.TrustpilotAdapter()
        res = a.pull("MyFitnessPal", {"domain": "www.myfitnesspal.com"}, limit=50)
        assert res.status == FetchStatus.BLOCKED, res.status
        assert res.reviews == []
        assert "manual" in res.note.lower() and res.url
        print(f"  trustpilot block -> BLOCKED + handoff note OK: {res.note[:60]}...")
    finally:
        trustpilot.guarded_fetch = orig


def test_trustpilot_pull_from_html():
    a = trustpilot.TrustpilotAdapter()
    res = a.pull_from_html("MyFitnessPal", "http://tp", [_TP_HTML])
    assert res.status == FetchStatus.OK and len(res.reviews) == 2
    print("  trustpilot pull_from_html (handoff completion) OK")


class FakeResp_text:
    def __init__(self, text):
        self.text = text
        self.status_code = 200

    def raise_for_status(self):
        pass


def test_handoff_roundtrip():
    run_id = "test-handoff"
    blocked = SourceResult("MyFitnessPal", Source.TRUSTPILOT, FetchStatus.BLOCKED,
                           url="https://www.trustpilot.com/review/www.myfitnesspal.com",
                           note="BLOCKED (HTTP 403). Needs manual fetch.")
    ok = SourceResult("MyFitnessPal", Source.APPLE, FetchStatus.OK, reviews=[])
    entries = handoff.report_blocked(run_id, [blocked, ok])
    assert len(entries) == 1 and entries[0]["source"] == "trustpilot"
    assert handoff.pending(run_id) == entries          # persisted

    # human saves the page HTML; complete the handoff from it
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(_TP_HTML)
        html_path = f.name
    a = trustpilot.TrustpilotAdapter()
    res = handoff.complete_from_files(run_id, a, "MyFitnessPal", blocked.url,
                                      [html_path])
    assert res.status == FetchStatus.OK and len(res.reviews) == 2
    assert handoff.pending(run_id) == []               # entry cleared
    print("  handoff round-trip OK: alert -> persist -> complete from HTML -> clear")


# --- Discovery: LLM parsing + hallucination drop + Worth-It Gate (no network) ---
class _Block:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _Resp:
    def __init__(self, text, stop_reason="end_turn"):
        self.content = [_Block(text)]
        self.stop_reason = stop_reason


class _Msgs:
    def __init__(self, script):
        self._script = list(script)  # list of _Resp, returned in order

    def create(self, **kw):
        return self._script.pop(0)


class _FakeClient:
    def __init__(self, *script):
        self.messages = _Msgs(script)


class _FakeAdapter:
    def __init__(self, source, table):
        self.source = source
        self._table = table            # name -> locator dict or None

    def probe(self, name, hints):
        return self._table.get(name)


def test_extract_json_array():
    fenced = 'blah\n```json\n[{"name":"A"}]\n```\ntrailing'
    assert discovery._extract_json_array(fenced) == [{"name": "A"}]
    bare = 'text [{"name":"B"}] more'
    assert discovery._extract_json_array(bare) == [{"name": "B"}]
    assert discovery._extract_json_array("no json here") == []
    print("  discovery JSON extraction OK (fenced, bare, none)")


def test_identify_players_with_pause_turn():
    reply = '```json\n[{"name":"MyFitnessPal","category":"direct","domain":"myfitnesspal.com"}]\n```'
    client = _FakeClient(_Resp("searching...", stop_reason="pause_turn"),
                         _Resp(reply))              # loop consumes both
    players = discovery.identify_players("track calories", client=client)
    assert len(players) == 1 and players[0].name == "MyFitnessPal"
    assert players[0].domain == "myfitnesspal.com"
    print("  identify_players OK (pause_turn loop + parse)")


def test_discover_gate_and_hallucination_drop():
    reply = ('```json\n[{"name":"A","domain":"a.com"},'
             '{"name":"B","domain":"b.com"},'
             '{"name":"Ghost","domain":"ghost.com"}]\n```')
    client = _FakeClient(_Resp(reply))
    apple_ad = _FakeAdapter(Source.APPLE,
                            {"A": {"review_count": 500}, "B": {"review_count": 100}})
    gplay_ad = _FakeAdapter(Source.GOOGLE_PLAY, {"A": {"review_count": 1000}})
    tp_ad = _FakeAdapter(Source.TRUSTPILOT, {"B": {"review_count": 10}})  # below 30
    res = discovery.discover("some problem", client=client,
                             adapters=[apple_ad, gplay_ad, tp_ad])

    kept = {p.name for p in res.players}
    assert kept == {"A", "B"}, kept                 # Ghost resolved nowhere -> dropped
    assert res.dropped == ["Ghost"]
    # Apple: A(500)+B(100) both >=30 -> 2 players -> live.
    # Google Play: only A -> 1 < 2 -> not live. Trustpilot: B=10 < 30 -> not live.
    assert res.live_sources == [Source.APPLE], res.live_sources
    assert any("Ghost" in n for n in res.notes)
    print(f"  discover OK: kept={kept}, dropped={res.dropped}, live={[s.value for s in res.live_sources]}")


# --- Synthesis (map-reduce) + Report render (no network) ---
def _rv(product, text, rating):
    return Review(source=Source.APPLE, product=product, text=text, rating=rating)


def test_synthesise_map_reduce():
    a = SourceResult("Alpha", Source.APPLE, FetchStatus.OK,
                     reviews=[_rv("Alpha", "love the scanner", 5),
                              _rv("Alpha", "paywall everywhere now", 2)])
    b = SourceResult("Beta", Source.APPLE, FetchStatus.OK,
                     reviews=[_rv("Beta", "great UI", 5),
                              _rv("Beta", "too expensive, constant upsell", 2)])
    c = SourceResult("Gamma", Source.TRUSTPILOT, FetchStatus.BLOCKED,
                     note="blocked")  # no reviews -> incomplete

    map_a = '```json\n{"loves":[{"theme":"scanner","support":"~1","quote":"love the scanner"}],"complaints":[{"theme":"paywall","support":"~1","severity":"high","quote":"paywall everywhere now"}]}\n```'
    map_b = '```json\n{"loves":[{"theme":"UI","support":"~1","quote":"great UI"}],"complaints":[{"theme":"pricing","support":"~1","severity":"high","quote":"too expensive"}]}\n```'
    reduce = '```json\n{"market_summary":"Crowded and pricey.","gaps":[{"gap":"aggressive paywalls","products_affected":["Alpha","Beta"],"unserved_by":"all players","why_opportunity":"transparent pricing wins","confidence":"high"}]}\n```'
    client = _FakeClient(_Resp(map_a), _Resp(map_b), _Resp(reduce))

    res = synthesis.synthesise([a, b, c], "budget tracking", client=client)
    names = {p["product"] for p in res["products"]}
    assert names == {"Alpha", "Beta", "Gamma"}, names
    gamma = next(p for p in res["products"] if p["product"] == "Gamma")
    assert gamma.get("incomplete") is True and gamma["coverage"]["trustpilot"] == "blocked"
    assert len(res["gaps"]) == 1 and res["gaps"][0]["gap"] == "aggressive paywalls"
    assert res["market_summary"] == "Crowded and pricey."
    print(f"  synthesise OK: {len(res['products'])} products, {len(res['gaps'])} gaps, Gamma incomplete")


# --- fail-closed fixes ---
def test_apple_fetch_error_is_error():
    a = apple.AppleAdapter()
    def boom(url, timeout=20, **kw):
        raise requests.RequestException("connection reset")
    a.session.get = boom
    res = a.pull("X", {"app_id": "1", "url": "u"}, limit=10)
    assert res.status == FetchStatus.ERROR, res.status   # not EMPTY
    print("  apple fetch failure -> ERROR (not EMPTY) OK")


def test_trustpilot_empty_when_expected_is_error():
    orig = _tp_patch(lambda url, **kw: FakeResp_text(_TP_EMPTY))  # count present, 0 reviews
    try:
        a = trustpilot.TrustpilotAdapter()
        res = a.pull("X", {"domain": "x.com", "review_count": 3456}, limit=50)
        assert res.status == FetchStatus.ERROR, res.status   # markup drift, not EMPTY
        assert "drift" in res.note.lower()
        print("  trustpilot parsed-0-when-expected -> ERROR (markup drift) OK")
    finally:
        trustpilot.guarded_fetch = orig


def test_discover_blocked_probe_forces_source_live():
    client = _FakeClient(_Resp('```json\n[{"name":"A","domain":"a.com"}]\n```'))
    tp = _FakeAdapter(Source.TRUSTPILOT,
                      {"A": {"domain": "a.com", "review_count": 0, "blocked": True}})
    res = discovery.discover("problem", client=client, adapters=[tp])
    assert Source.TRUSTPILOT in res.live_sources   # blocked probe must not be dropped
    print("  discover blocked-probe -> source forced live (handoff can fire) OK")


def test_synthesis_includes_partial_blocked_reviews():
    blocked = SourceResult("Alpha", Source.TRUSTPILOT, FetchStatus.BLOCKED,
                           reviews=[_rv("Alpha", "cancelled after months", 1)],
                           note="blocked mid-pull")
    map_a = '```json\n{"loves":[],"complaints":[{"theme":"cancellation","quote":"cancelled after months"}]}\n```'
    reduce = '```json\n{"market_summary":"x","gaps":[]}\n```'
    res = synthesis.synthesise([blocked], "problem", client=_FakeClient(_Resp(map_a), _Resp(reduce)))
    alpha = res["products"][0]
    assert not alpha.get("incomplete") and alpha.get("review_count") == 1
    assert alpha["coverage"]["trustpilot"] == "blocked"   # still flagged incomplete-source
    print("  synthesis keeps partial reviews from BLOCKED result OK")


# --- security hardening ---
def test_trustpilot_fallback_is_strict():
    loose = "<html><body><article><p>unrelated marketing text</p></article></body></html>"
    assert trustpilot._html_fallback("X", loose) == []   # not treated as reviews
    real = ('<html><body><div data-service-review-card-paper>'
            '<span data-service-review-text-typography>Bad support</span>'
            '<div data-service-review-rating="2"></div></div></body></html>')
    out = trustpilot._html_fallback("X", real)
    assert len(out) == 1 and out[0].text == "Bad support" and out[0].rating == 2.0
    print("  trustpilot strict fallback OK: loose HTML rejected, real card parsed")


def test_synthesis_map_error_flag():
    ok = SourceResult("Alpha", Source.APPLE, FetchStatus.OK,
                      reviews=[_rv("Alpha", "some review", 3)])
    res = synthesis.synthesise([ok], "problem",
                               client=_FakeClient(_Resp("not json at all")))
    assert res["products"][0].get("map_error") is True   # flagged, not silent blank
    print("  synthesis unparseable map -> map_error flag OK")


def test_report_render():
    synth = {
        "problem": "budget tracking",
        "market_summary": "Crowded and pricey.",
        "gaps": [{"gap": "aggressive paywalls", "products_affected": ["Alpha", "Beta"],
                  "unserved_by": "all players", "why_opportunity": "transparent pricing",
                  "confidence": "high"}],
        "products": [
            {"product": "Alpha", "review_count": 2, "coverage": {"apple_app_store": "ok"},
             "loves": [{"theme": "scanner", "support": "~1", "quote": "love it"}],
             "complaints": [{"theme": "paywall", "severity": "high", "quote": "paywall"}]},
            {"product": "Gamma", "coverage": {"trustpilot": "blocked"}, "incomplete": True},
        ],
    }
    md = report.render(synth, "budget tracking")
    assert "# Market Gap Report" in md
    assert "Market gaps — the opportunity" in md
    assert "aggressive paywalls" in md
    assert "How to read this" in md          # the evidence caveat
    assert "Incomplete" in md                # Gamma's blocked note
    assert "> \"paywall\"" in md             # grounded quote
    print("  report render OK: gaps-first, caveat, incomplete flagged, quotes grounded")


# --- Reddit adapter (fake PRAW client, no network) ---
class _FakeComment:
    def __init__(self, body, score):
        self.body = body; self.score = score; self.created_utc = 1_700_000_000


class _FakeComments(list):
    def replace_more(self, limit=0):
        pass


class _FakeSubmission:
    def __init__(self, title, selftext, subreddit, score, num_comments, comments):
        self.title = title; self.selftext = selftext; self.subreddit = subreddit
        self.score = score; self.num_comments = num_comments
        self.permalink = "/r/x/comments/1"; self.created_utc = 1_700_000_000
        self.comments = _FakeComments(comments)


class _FakeSubreddit:
    def __init__(self, subs):
        self._subs = subs

    def search(self, q, sort="relevance", limit=25):
        return list(self._subs)[:limit]


class _FakeReddit:
    def __init__(self, subs):
        self._subs = subs

    def subreddit(self, name):
        return _FakeSubreddit(self._subs)


def test_reddit_probe_and_pull():
    from gap_finder.ingest.reddit import RedditAdapter
    subs = [_FakeSubmission("Anyone tried Widget?", "It never syncs", "biohackers",
                            42, 10, [_FakeComment("battery drains fast", 7),
                                     _FakeComment("", 0)])]
    a = RedditAdapter(reddit=_FakeReddit(subs))
    loc = a.probe("Widget", {})
    assert loc["review_count"] == 11, loc          # 1 submission + 10 comments
    res = a.pull("Widget", loc, limit=50)
    assert res.status == FetchStatus.OK
    assert len(res.reviews) == 2                    # submission + 1 non-empty comment
    assert res.reviews[0].source_metadata["type"] == "submission"
    assert "never syncs" in res.reviews[0].text and res.reviews[0].rating is None
    assert res.reviews[1].source_metadata["type"] == "comment"
    print("  reddit probe+pull OK: submission + comment mapped, empty comment skipped")


# --- Company anchor + approval checkpoint ---
def test_apply_edits_proceed_drop_add():
    ps = [Player(name="A"), Player(name="B"), Player(name="C")]
    out, done = cli._apply_edits(ps, "")            # Enter = proceed
    assert done and out == ps
    out, done = cli._apply_edits(ps, "2")           # drop #2 (B)
    assert not done and [p.name for p in out] == ["A", "C"]
    out, done = cli._apply_edits(ps, "+Levels")     # add
    assert not done and out[-1].name == "Levels" and out[-1].category == "user-added"
    print("  _apply_edits OK: proceed / drop-by-number / add '+Name'")


def test_company_anchor_injected_when_omitted():
    reply = '```json\n[{"name":"Viome","domain":"viome.com"},{"name":"Levels","domain":"levels.com"}]\n```'
    players = discovery.identify_players(company="Zoe", client=_FakeClient(_Resp(reply)))
    assert "Zoe" in [p.name for p in players]        # injected though model omitted it
    zoe = next(p for p in players if p.name == "Zoe")
    assert zoe.is_anchor and zoe.category == "anchor"
    print("  company anchor injected-when-omitted OK")


def test_company_anchor_marked_when_present():
    reply = '```json\n[{"name":"Viome","domain":"viome.com"},{"name":"Zoe","domain":"zoe.com"}]\n```'
    players = discovery.identify_players(company="Zoe", client=_FakeClient(_Resp(reply)))
    assert sum(p.is_anchor for p in players) == 1
    assert players[0].name == "Zoe" and players[0].is_anchor   # moved to front
    print("  company anchor marked + moved to front (no duplicate) OK")


def test_cli_rejects_both_inputs():
    import sys as _sys
    old = _sys.argv
    try:
        _sys.argv = ["cli", "some problem", "--company", "Zoe"]
        try:
            cli.main()
            assert False, "should have errored on both inputs"
        except SystemExit:
            pass
    finally:
        _sys.argv = old
    print("  cli XOR guard OK (rejects problem + --company together)")


def test_players_json_roundtrip():
    ps = [Player(name="Zoe", category="anchor", why_relevant="gut+blood", domain="zoe.com", is_anchor=True),
          Player(name="Viome", category="direct", why_relevant="microbiome", domain="viome.com")]
    blob = cli._players_json(ps)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(blob); path = f.name
    loaded = cli._load_players(path)
    assert [p.name for p in loaded] == ["Zoe", "Viome"]
    assert loaded[0].is_anchor and loaded[0].domain == "zoe.com"
    assert not loaded[1].is_anchor
    print("  players JSON round-trip OK (--list-only -> --players-file)")


def test_reddit_probe_propagates_access_error():
    from gap_finder.ingest.reddit import RedditAdapter

    class _BadReddit:
        def subreddit(self, name):
            class _S:
                def search(self, *a, **k):
                    raise RuntimeError("401 Unauthorized")
            return _S()

    a = RedditAdapter(reddit=_BadReddit())
    try:
        a.probe("X", {})
        assert False, "probe should propagate the access error"
    except RuntimeError:
        print("  reddit probe propagates access error (visible, not silent None) OK")


def test_report_anchor_marked():
    synth = {"problem": "x", "market_summary": "", "gaps": [],
             "products": [{"product": "Zoe", "review_count": 1,
                           "coverage": {"apple_app_store": "ok"},
                           "loves": [], "complaints": []}]}
    md = report.render(synth, "x", anchor="Zoe")
    assert "**Anchor:** Zoe" in md and "★ (anchor)" in md
    print("  report anchor marking OK")


if __name__ == "__main__":
    tests = [test_apple_pull_parses_and_stops, test_apple_empty_is_fail_closed,
             test_gplay_probe_and_pull, test_block_detector,
             test_trustpilot_probe_and_pull, test_trustpilot_probe_needs_domain,
             test_trustpilot_block_triggers_handoff, test_trustpilot_pull_from_html,
             test_handoff_roundtrip,
             test_extract_json_array, test_identify_players_with_pause_turn,
             test_discover_gate_and_hallucination_drop,
             test_synthesise_map_reduce, test_report_render,
             test_apple_fetch_error_is_error,
             test_trustpilot_empty_when_expected_is_error,
             test_discover_blocked_probe_forces_source_live,
             test_synthesis_includes_partial_blocked_reviews,
             test_trustpilot_fallback_is_strict, test_synthesis_map_error_flag,
             test_reddit_probe_and_pull,
             test_apply_edits_proceed_drop_add, test_company_anchor_injected_when_omitted,
             test_company_anchor_marked_when_present, test_report_anchor_marked,
             test_cli_rejects_both_inputs, test_reddit_probe_propagates_access_error,
             test_players_json_roundtrip]
    for t in tests:
        t()
    print(f"\nALL {len(tests)} OFFLINE TESTS PASSED")
