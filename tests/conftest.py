import pytest


def pytest_collection_modifyitems(items):
    """Make pytest-httpx tolerant of reused callbacks and unused mocks.

    This version of pytest-httpx treats each registered response/callback as
    single-use and asserts every mock is requested. Our scans call the same
    target/judge endpoints many times (and some paths legitimately skip the
    judge), so we relax both behaviors for the whole suite. Harmless for tests
    that don't use the httpx_mock fixture.
    """
    marker = pytest.mark.httpx_mock(
        can_send_already_matched_responses=True,
        assert_all_responses_were_requested=False,
    )
    for item in items:
        item.add_marker(marker)
