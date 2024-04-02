# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

log = logging.getLogger(__name__)


def format_datetime_to_isoformat_without_tz(
    datetime_arg: datetime.datetime,
) -> str:
    """Format the provided datetime object to a string in ISO format without timezone information.

    Returns
    -------
    str
        The formatted datetime string in the format: "yyyy-MM-ddThh-mm-ss.SSS".
    """
    return datetime_arg.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
