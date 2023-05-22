# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import difflib
import logging
import os
import pathlib
import shutil

import capellambse
import capellambse.decl
import conftest
import pytest
from capellambse.loader import exs

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

pytestmark = pytest.mark.t4c_server

TECHUSER_UID: str | int = os.getenv("TECHUSER_UID", "")


@pytest.fixture(name="t4c_exporter_local_env")
def fixture_t4c_exporter_local_env(
    t4c_exporter_env: dict[str, str],
    t4c_ip_addr: str,
) -> dict[str, str]:
    return t4c_exporter_env | {
        "FILE_HANDLER": "local",
        "no_proxy": t4c_ip_addr,
    }


@pytest.fixture(name="model_export_import_diff_path")
def fixture_export_import_model_diff_path(
    tmp_path: pathlib.Path,
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    exporter_path: pathlib.Path = tmp_path / "export_model"
    exporter_path.mkdir(parents=True, exist_ok=True)
    exporter_path.chmod(mode=0o0777)

    import_path: pathlib.Path = tmp_path / "import_model"
    import_path.mkdir(parents=True, exist_ok=True)
    import_path.chmod(mode=0o0777)

    model_diff_path: pathlib.Path = tmp_path / "model_diff"
    model_diff_path.mkdir(parents=True, exist_ok=True)
    model_diff_path.chmod(mode=0o0777)

    return exporter_path, import_path, model_diff_path


@pytest.mark.skipif(
    condition=conftest.is_capella_5_x_x(),
    reason="Capella 5.x.x. not supported",
)
@pytest.mark.usefixtures("init_t4c_server_repo")
def test_export_locally(
    model_export_import_diff_path: tuple[
        pathlib.Path, pathlib.Path, pathlib.Path
    ],
    t4c_exporter_local_env: dict[str, str],
):
    export_path, import_path, _ = model_export_import_diff_path
    data_dir: pathlib.Path = pathlib.Path(__file__).parents[0] / "data"

    copy_model_files_to_directory(
        model_dir=data_dir / conftest.CAPELLA_VERSION,
        tar_dir=export_path,
    )

    initial_model: capellambse.MelodyModel = capellambse.MelodyModel(
        export_path / "test-project.aird"
    )

    export_model(export_path, t4c_exporter_local_env)

    capellambse.decl.apply(initial_model, data_dir / "model-changes.yaml")
    initial_model.save()

    export_model(export_path, t4c_exporter_local_env)
    import_model(import_path, t4c_exporter_local_env)

    imported_model: capellambse.MelodyModel = capellambse.MelodyModel(
        import_path / conftest.T4C_PROJECT_NAME / "test-project.aird"
    )

    assert imported_model

    actor = imported_model.by_uuid("9db9070c-509a-42f3-b6f6-bdf9a7788aa2")
    function_1 = actor.allocated_functions.by_name("do stuff 1")

    assert actor.is_actor
    assert actor.description == "modified-by-test"
    assert len(actor.allocated_functions) == 2

    assert function_1.owner == actor
    assert len(function_1.functions)
    assert function_1.functions[0].name == "do stuff 1.1"


def import_model(model_dir: pathlib.Path, env: dict[str, str]):
    with conftest.get_container(
        image="t4c/client/backup",
        environment=env,
    ) as container:
        conftest.wait_for_container(container, "Backup of model finished")

        conftest.extract_container_dir_to_local_dir(
            container.id, "/tmp/model/", model_dir
        )

        shutil.copytree(
            model_dir / "model" / conftest.T4C_PROJECT_NAME,
            model_dir / conftest.T4C_PROJECT_NAME,
        )


def export_model(model_dir: pathlib.Path, env: dict[str, str]):
    model_tar = model_dir / "model.tar"

    conftest.create_tarfile(
        destination_path=model_tar, source_dir=model_dir, arcname="data"
    )

    with conftest.get_container(
        image="t4c/client/exporter", environment=env, entrypoint=["/bin/bash"]
    ) as container:
        # We can't just mount the test data as a volume as this will cause problems
        # when as we are running Docker in Docker (i.e., we would mount the
        # volume on the host machine but not on the container running the job/test)
        with open(file=model_tar, mode="rb") as tar_file:
            conftest.client.api.put_archive(container.id, "/tmp", tar_file)

        conftest.wait_for_container(
            container,
            "Export of model to TeamForCapella server finished",
            cmd="xvfb-run python /opt/scripts/exporter.py",
        )


def copy_model_files_to_directory(
    model_dir: pathlib.Path, tar_dir: pathlib.Path
):
    for file in model_dir.glob("*"):
        if not str(file).endswith("license"):
            shutil.copy2(file, tar_dir)


def _create_model_diff(
    model_1: capellambse.MelodyModel,
    model_2: capellambse.MelodyModel,
    path: pathlib.Path,
    suffix: int | str | None = None,
):
    differ: difflib.Differ = difflib.Differ()

    diff_file_path: pathlib.Path = path / "diff.xml"
    if suffix is not None:
        diff_file_path = path / f"diff_{suffix}.xml"

    model_diff = differ.compare(
        exs.to_string(model_1._element).splitlines(True),
        exs.to_string(model_2._element).splitlines(True),
    )

    with open(diff_file_path, "w", encoding="UTF-8") as diff_file:
        diff_file.write("".join(model_diff))


def _clear_files_and_delete_directory(model_dir: pathlib.Path):
    for file in model_dir.glob("*"):
        if file.is_file():
            file.unlink()
    model_dir.rmdir()
