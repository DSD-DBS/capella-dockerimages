# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


def build_rich_link(link: str, text: str) -> str:
    return f"[underline bright_cyan link={link}]{text}[/underline bright_cyan link]"
