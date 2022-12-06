# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for metrics"""
import time
from unittest import mock

import pytest
from metrics import IdleTimer

# pylint: disable=redefined-outer-name


@pytest.fixture
def idler() -> IdleTimer:
    """Return an instance of `metrics.IdleTime`"""
    return IdleTimer()


def print_no_display(*__, **_) -> str:
    """
    Just print: 'could not open display', the response of xprintidle
    when there is no X server.
    """
    return mock.MagicMock(stdout="couldn't open display")


def test_get_idletime_had_no_display_on_init_but_later() -> None:
    with mock.patch("subprocess.run", print_no_display):
        idler = IdleTimer()
        _, init_idletime = idler.first_checkpoint

    idletime = idler.get_idletime()

    assert init_idletime == -1
    assert idletime > -1


def test_get_idletime_never_had_a_display_and_returns_minus_one() -> None:
    with mock.patch("subprocess.run", print_no_display):
        idler = IdleTimer()
        _, init_idletime = idler.first_checkpoint

        time.sleep(10)

        idletime = idler.get_idletime()

    assert init_idletime == -1
    assert idletime == -1


def test_get_idletime_works(idler: IdleTimer) -> None:
    idletime = idler.get_idletime()

    assert isinstance(idletime, float)


def test_get_idletime_increases_after_display_is_closed(
    idler: IdleTimer,
) -> None:
    idletime = idler.get_idletime()

    time.sleep(60)

    mock.patch("subprocess.run", print_no_display)

    second_idletime = idler.get_idletime()

    assert isinstance(idletime, float) and isinstance(second_idletime, float)
    assert idletime < second_idletime
