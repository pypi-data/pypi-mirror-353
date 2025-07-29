import os
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture(scope="function", autouse=True)
def clear_test_dir(dir_tests: Path) -> None:
    os.chdir(dir_tests)

    dir_packages = dir_tests / "packages"
    if dir_packages.exists():
        shutil.rmtree(dir_packages, ignore_errors=True)

    requirements_file = dir_tests / "requirements.txt"
    if requirements_file.exists():
        os.remove(requirements_file)


@pytest.fixture(scope="function")
def requirments_file(dir_tests: Path) -> None:
    os.chdir(dir_tests)
    with open("requirements.txt", "w") as f:
        f.write("lxml==4.9.1\n")
        f.write("numba==0.58.1\n")


def test_pip_download(typer_runner: CliRunner, dir_tests: Path) -> None:
    os.chdir(dir_tests)

    from pycmd2.pip.pip_download import cli

    result = typer_runner.invoke(cli.app, ["lxml"])
    assert result.exit_code == 0

    files = list(dir_tests.glob("packages/lxml-*.whl"))
    assert len(files) == 1


def test_pip_download_req(typer_runner, requirments_file, dir_tests) -> None:
    os.chdir(dir_tests)

    from pycmd2.pip.pip_download_req import cli

    result = typer_runner.invoke(cli.app, [])
    assert result.exit_code == 0

    files = list(dir_tests.glob("packages/lxml-*.whl"))
    assert len(files) == 1

    files = list(dir_tests.glob("packages/numba-*.whl"))
    assert len(files) == 1

    files = list(dir_tests.glob("packages/numpy-*.whl"))
    assert len(files) == 1


def test_pip_freeze(typer_runner, dir_tests) -> None:
    os.chdir(dir_tests)

    from pycmd2.pip.pip_freeze import cli

    result = typer_runner.invoke(cli.app, [])
    assert result.exit_code == 0

    with open("requirements.txt") as f:
        libs = {_.split("==")[0] for _ in f.readlines()}
        assert "hatch" in libs
        assert "pytest" in libs


def test_pip_install(typer_runner, dir_tests) -> None:
    os.chdir(dir_tests)

    from pycmd2.pip.pip_install import cli

    result = typer_runner.invoke(cli.app, ["lxml", "typing-extensions"])
    assert result.exit_code == 0


def test_pip_install_offline(typer_runner, dir_tests) -> None:
    os.chdir(dir_tests)
    from pycmd2.pip.pip_install_offline import cli

    result = typer_runner.invoke(cli.app, ["lxml", "typing-extensions"])
    assert result.exit_code == 0


def test_pip_install_req(typer_runner, requirments_file, dir_tests) -> None:
    os.chdir(dir_tests)

    from pycmd2.pip.pip_install_req import cli

    result = typer_runner.invoke(cli.app, [])
    assert result.exit_code == 0


def test_pip_uninstall_req(typer_runner, requirments_file, dir_tests) -> None:
    os.chdir(dir_tests)

    from pycmd2.pip.pip_uninstall_req import cli

    result = typer_runner.invoke(cli.app, [])
    assert result.exit_code == 0
