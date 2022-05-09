from unittest import mock

import pytest
from metrics import get_idletime


@mock.patch("subprocess.run", lambda _: "Could not open display")
def test_get_idletime_fails_when_no_display_is_found() -> None:
    with pytest.raises(TypeError):
        get_idletime()


def test_get_idletime_works() -> None:
    idletime = get_idletime()

    assert isinstance(idletime, float)
