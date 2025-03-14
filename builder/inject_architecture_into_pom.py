# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# pylint: skip-file


import copy
import pathlib

from lxml import etree
from lxml.builder import E


def patch_root_pom_xml() -> None:
    pom_xml_path = pathlib.Path("pom.xml")

    root = etree.parse(pom_xml_path.open()).getroot()
    environments = root.xpath("//*[local-name()='environments']")[0]
    environments.append(
        E.environment(
            E.os("linux"),
            E.ws("gtk"),
            E.arch("aarch64"),
        )
    )
    environments.append(
        E.environment(
            E.os("macosx"),
            E.ws("cocoa"),
            E.arch("aarch64"),
        )
    )
    pom_xml_path.write_bytes(etree.tostring(root))


def patch_releng_pom_xml() -> None:
    pom_xml_path = pathlib.Path(
        "releng/plugins/org.polarsys.capella.rcp.product/pom.xml"
    )

    root = etree.parse(pom_xml_path.open()).getroot()

    create_dropins(root)
    package_product(root)

    pom_xml_path.write_bytes(etree.tostring(root))


def create_dropins(root: etree._Element) -> None:
    # We do the packaging ourselves and don't need antrun
    dropins = root.xpath(
        "//*[local-name()='execution' and ./*[local-name()='id']/text()='create-dropins']/*[local-name()='configuration']/*[local-name()='target']"
    )[0]
    dropins.append(
        E.mkdir(
            dir="${project.build.directory}/products/org.polarsys.capella.rcp.product/linux/gtk/aarch64/dropins"
        )
    )
    dropins.append(
        E.mkdir(
            dir="${project.build.directory}/products/org.polarsys.capella.rcp.product/macosx/cocoa/aarch64/Capella.app/Contents/Eclipse/dropins"
        )
    )


def package_product(root: etree._Element) -> None:
    target = root.xpath(
        "//*[local-name()='execution' and ./*[local-name()='id']/text()='package-product']/*[local-name()='configuration']/*[local-name()='target']"
    )[0]

    existing_packages = {
        "linux": {
            "move": "${project.build.directory}/products/org.polarsys.capella.rcp.product/linux/gtk/x86_64/jre",
            "tar": "${project.build.directory}/products/capella-${unqualifiedVersion}.${buildQualifier}-linux-gtk-x86_64.tar.gz",
        },
        "macos": {
            "move": "${project.build.directory}/products/org.polarsys.capella.rcp.product/macosx/cocoa/x86_64/Capella.app/Contents/jre",
            "tar": "${project.build.directory}/products/capella-${unqualifiedVersion}.${buildQualifier}-macosx-cocoa-x86_64.tar.gz",
        },
    }

    for package in existing_packages.values():
        move_todir = package["move"]
        move = target.xpath(f"./*[local-name()='move' and ./@todir='{move_todir}']")[0]

        copied_move = copy.deepcopy(move)
        copied_move.attrib["todir"] = move_todir.replace("x86_64", "aarch64")
        fileset = copied_move.getchildren()[0]
        fileset.attrib["dir"] = fileset.attrib["dir"].replace("JRE", "JRE-aarch64")

        target.append(copied_move)

        tar_destfile = package["tar"]
        tar = target.xpath(f"./*[local-name()='tar' and ./@destfile='{tar_destfile}']")[
            0
        ]

        copied_tar = copy.deepcopy(tar)
        copied_tar.attrib["destfile"] = copied_tar.attrib["destfile"].replace(
            "x86_64", "aarch64"
        )
        for tarfileset in copied_tar.getchildren():
            tarfileset.attrib["dir"] = tarfileset.attrib["dir"].replace(
                "x86_64", "aarch64"
            )

        target.append(copied_tar)


if __name__ == "__main__":
    patch_root_pom_xml()
    patch_releng_pom_xml()
