from unittest.mock import Mock, patch

import pytest

from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate.rule_executor import RuleExecutor
from imas_validator.validate_options import ValidateOptions


@pytest.fixture
def validate_options():
    validate_options = ValidateOptions(use_pdb=True)
    return validate_options


@pytest.fixture
def res_collector(validate_options):
    res_col = ResultCollector(validate_options=validate_options, imas_uri="")
    return res_col


@pytest.fixture
def rule(res_collector):
    def cool_func_name(ids_name):
        """put docs here"""
        res_collector.assert_(ids_name)

    mock = Mock()
    mock.apply_func = lambda x: cool_func_name(*x)
    return mock


@pytest.fixture
def rule_error(res_collector):
    def func_error(ids_name):
        """Error docs"""
        a = ids_name / 0
        res_collector.assert_(a)

    mock = Mock()
    mock.apply_func = lambda x: func_error(*x)
    return mock


@pytest.fixture
def rule_executor(rule, rule_error, res_collector, validate_options):
    dbentry = Mock()
    rules = [rule, rule_error]
    rule_executor = RuleExecutor(
        dbentry, rules, res_collector, validate_options=validate_options
    )
    return rule_executor


def assert_last_tb(tbi, res):
    while tbi.tb_next:
        tbi = tbi.tb_next
    assert tbi.tb_frame.f_code.co_name == res


def test_debug_true(rule, rule_executor, res_collector, test_data_core_profiles):
    my_pdb = Mock()

    with patch(
        "imas_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(
            rule, [(test_data_core_profiles._obj, "core_profiles", 0)]
        )
        rule_executor.run(rule, [True])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 0


def test_debug_false(rule, rule_executor, res_collector, test_data_core_profiles):
    my_pdb = Mock()

    with patch(
        "imas_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(
            rule, [(test_data_core_profiles._obj, "core_profiles", 0)]
        )
        rule_executor.run(rule, [False])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 1
        assert_last_tb(my_pdb.call_args_list[0][0][0], "cool_func_name")


def test_debug_error(rule_error, rule_executor, res_collector, test_data_core_profiles):
    my_pdb = Mock()

    with patch(
        "imas_validator.validate.rule_executor.pdb",
        post_mortem=my_pdb,
    ):
        res_collector.set_context(
            rule_error, [(test_data_core_profiles._obj, "core_profiles", 0)]
        )
        rule_executor.run(rule_error, [1])
        assert len(res_collector.results) == 1
        assert my_pdb.call_count == 1
        assert_last_tb(my_pdb.call_args_list[0][0][0], "func_error")
