# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import difflib
import logging
import os
import pathlib
import shutil
import tarfile
import time

import capellambse
import conftest
import pytest
from capellambse.loader import exs

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

pytestmark = pytest.mark.t4c_server

TECHUSER_UID: str | int = os.getenv("TECHUSER_UID", "")

OA_ACTOR_UUID: str = "ce69cb4c-fd7d-4d92-9414-b627af13ca13"
LA_ACTOR_UUID: str = "68c4da78-f68f-42fa-aee8-2f03c0708679"
SA_ACTOR_UUID: str = "9db9070c-509a-42f3-b6f6-bdf9a7788aa2"


@pytest.fixture(name="t4c_exporter_local_environment")
def fixture_t4c_exporter_local_environment(
    t4c_exporter_general_environment: dict[str, str]
) -> dict[str, str]:
    return t4c_exporter_general_environment | {"FILE_HANDLER": "local"}


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
def test_backup_locally(
    model_export_import_diff_path: tuple[
        pathlib.Path, pathlib.Path, pathlib.Path
    ],
    t4c_exporter_local_environment: dict[str, str],
):
    export_path, import_path, model_diff_path = model_export_import_diff_path

    copy_model_files_to_directory(
        model_dir=pathlib.Path(__file__).parents[0]
        / "data"
        / conftest.T4C_PROJECT_NAME,
        tar_dir=export_path,
    )

    initial_model: capellambse.MelodyModel = capellambse.MelodyModel(
        export_path / "test-project.aird"
    )

    export_model(export_path, t4c_exporter_local_environment)
    for i in range(2):
        if i == 0:
            initial_model = apply_model_changes(initial_model)
            initial_model.save()

        export_model(export_path, t4c_exporter_local_environment)
        import_model(import_path, t4c_exporter_local_environment)

        imported_model: capellambse.MelodyModel = capellambse.MelodyModel(
            import_path / conftest.T4C_PROJECT_NAME / "test-project.aird"
        )

        create_model_diff(initial_model, imported_model, model_diff_path, i)

        clear_files_and_delete_directory(
            import_path / conftest.T4C_PROJECT_NAME
        )

    print(model_export_import_diff_path)
    breakpoint()
    assert True


def apply_model_changes(
    model: capellambse.MelodyModel,
) -> capellambse.MelodyModel:
    layer: str = "SA"

    if layer == "SA":
        actor_uuid = SA_ACTOR_UUID
        layer_accessor = model.sa
    elif layer == "LA":
        actor_uuid = LA_ACTOR_UUID
        layer_accessor = model.la

    actor = model.by_uuid(actor_uuid)
    actor.description = "modified-by-test"

    func_1 = layer_accessor.root_function.functions.create(name="do stuff 1")
    func_2 = layer_accessor.root_function.functions.create(name="do stuff 2")

    actor.allocated_functions.insert(0, func_1)
    actor.allocated_functions.append(func_2)

    return model


def import_model(model_dir: pathlib.Path, env: dict[str, str]):
    model_tar_path: pathlib.Path = model_dir / "imported_model.tar"

    with conftest.get_container(
        image="t4c/client/backup",
        environment=env,
        network="host",
    ) as container:
        conftest.wait_for_container(container, "Backup finished")
        strm, _ = conftest.client.api.get_archive(container.id, "/tmp/model/")

        with open(file=model_tar_path, mode="wb") as tar_file:
            for chunk in strm:
                tar_file.write(chunk)

        with tarfile.open(name=model_tar_path, mode="r") as tar_file:
            for member in tar_file.getmembers():
                tar_file.extract(member, path=model_dir)

        shutil.copytree(
            model_dir / "model" / conftest.T4C_PROJECT_NAME,
            model_dir / conftest.T4C_PROJECT_NAME,
        )


def export_model(model_dir: pathlib.Path, env: dict[str, str]):
    with conftest.get_container(
        image="t4c/client/exporter",
        path=model_dir,
        mount_path="/tmp/data",
        environment=env,
        network="host",
    ) as container:
        conftest.wait_for_container(container, "Export finished")
        time.sleep(4)


def create_model_diff(
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


def copy_model_files_to_directory(
    model_dir: pathlib.Path, tar_dir: pathlib.Path
):
    for _file in model_dir.glob("*"):
        if not str(_file).endswith("license"):
            shutil.copy2(_file, tar_dir)


def clear_files_and_delete_directory(model_dir: pathlib.Path):
    for _file in model_dir.glob("*"):
        if _file.is_file():
            _file.unlink()
    model_dir.rmdir()
