# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

log = logging.getLogger(__name__)


def format_datetime_to_isoformat_without_tz(
    datetime_arg: datetime.datetime,
) -> str:
    """Format the provided datetime object to a string in ISO format.

    The resulting string will not contain the timezone information.

    Returns
    -------
    str
        The formatted datetime string in the format: "YYYY-MM-DDTHH:MM:SS.sss".
        For example, a datetime object representing April 8, 2024, at 15:30:45.124567 would be formatted as "2024-04-08T15:30:45.124".
    """
    return datetime_arg.astimezone(tz=datetime.UTC).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )[:-3]
