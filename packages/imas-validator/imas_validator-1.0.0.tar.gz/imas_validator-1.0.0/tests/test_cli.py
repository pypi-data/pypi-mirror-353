import argparse
from pathlib import Path

import imas  # type: ignore
import pytest

from imas_validator.cli import imas_validator_cli
from imas_validator.cli.commands import validate_command


def test_cli_no_arguments():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        imas_validator_cli.main([])

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_cli_wrong_command():
    argv = ["wrong_command"]

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        imas_validator_cli.main(argv)

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2

@pytest.mark.skip(reason="Skipping this test due to imas-core unavailability")
def test_non_existing_pulsefile(tmp_path):
    empty_db_dir = tmp_path / "empty_testdb"
    empty_db_dir.mkdir()

    argv = ["validate", f"imas:hdf5?path={empty_db_dir}"]

    # When using imas_core >= 5.2, this raises an ALException. In earlier AL versions
    # IMAS-Python raises a LowlevelError.
    with pytest.raises(SystemExit):
        imas_validator_cli.main(argv)

@pytest.mark.skip(reason="Skipping this test due to imas-core unavailability")
def test_existing_pulsefile(tmp_path):
    db_dir = tmp_path / "testdb"
    db_dir.mkdir()

    uri = f"imas:hdf5?path={db_dir}"
    entry = imas.DBEntry(uri=uri, mode="x")
    entry.close()

    argv = ["validate", uri]

    imas_validator_cli.main(argv)


def test_non_existing_pulsefile(tmp_path):
    empty_db_dir = tmp_path / "empty_testdb"
    empty_db_dir.mkdir()

    argv = ["validate", f"{empty_db_dir}/pulse.nc"]

    # When using imas_core >= 5.2, this raises an ALException. In earlier AL versions
    # IMAS-Python raises a LowlevelError.
    with pytest.raises(Exception):
        imas_validator_cli.main(argv)


def test_existing_pulsefile(tmp_path):
    db_dir = tmp_path / "testdb"
    db_dir.mkdir()

    uri = f"{db_dir}/pulse.nc"
    entry = imas.DBEntry(uri=uri, mode="x")
    entry.close()

    argv = ["validate", uri]
    with pytest.raises(Exception):
        imas_validator_cli.main(argv)


def test_validate_command_str_cast():
    args = argparse.Namespace(
        command="Validate",
        uri="testdb/pulse.nc",
        ruleset=[["test_ruleset"]],
        extra_rule_dirs=[[""]],
        no_generic=True,
        debug=False,
        no_bundled=False,
        node_coverage=True,
        filter_name=[],
        filter_ids=[],
        filter=[["homogeneous_time", "core_profiles"]],
    )

    command_object = validate_command.ValidateCommand(args)

    assert command_object.validate_options.rulesets == ["test_ruleset"]
    assert command_object.validate_options.use_bundled_rulesets
    assert command_object.validate_options.extra_rule_dirs == [Path(".")]
    assert command_object.validate_options.apply_generic
    assert not command_object.validate_options.use_pdb
    assert command_object.validate_options.rule_filter.name == ["homogeneous_time"]
    assert command_object.validate_options.rule_filter.ids == ["core_profiles"]


def test_explore_command():
    argv = ["explore"]

    imas_validator_cli.main(argv)
