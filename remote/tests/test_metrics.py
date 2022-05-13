import time
from unittest import mock

import pytest
from metrics import IdleTime

# pylint: disable=redefined-outer-name


@pytest.fixture
def idler() -> IdleTime:
    """Return an instance of `metrics.IdleTime`"""
    return IdleTime()


no_display_stdouter = lambda _: "could not open display"


@mock.patch("subprocess.run", no_display_stdouter)
def test_get_idletime_fails_when_no_display_is_found(idler: IdleTime) -> None:
    with pytest.raises(TypeError):
        idler.get_idletime()


def test_get_idletime_works(idler: IdleTime) -> None:
    idletime = idler.get_idletime()

    assert isinstance(idletime, float)


def test_get_idletime_increases_after_display_is_closed(idler: IdleTime) -> None:
    idletime = idler.get_idletime()

    time.sleep(10)

    mock.patch("subprocess.run", no_display_stdouter)

    second_idletime = idler.get_idletime()

    assert isinstance(idletime, float) and isinstance(second_idletime, float)
    assert idletime < second_idletime
