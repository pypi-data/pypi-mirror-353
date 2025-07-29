"""This file describes the functionality for discovering and loading validation rules"""

import inspect
import logging
import os
from operator import attrgetter
from pathlib import Path
from typing import Dict, List

from importlib_resources import files

import imas_validator
from imas_validator.exceptions import InvalidRulesetName, InvalidRulesetPath
from imas_validator.rules.ast_rewrite import run_path
from imas_validator.rules.data import IDSValidationRule, ValidatorRegistry
from imas_validator.rules.docs_dataclass import (
    ExplorerData,
    RuleData,
    RuleDirData,
    RuleFileData,
    RuleSetData,
)
from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate_options import ValidateOptions

logger = logging.getLogger(__name__)

DEFAULT_FUNC_DOCSTRING = (
    "No function docstring available. Add a docstring to your function."
)
DEFAULT_MODULE_DOCSTRING = (
    "No module docstring available. Add a docstring at the top of your ruleset."
)
DEFAULT_FOLDER_DOCSTRING = (
    "No folder docstring available. Add an __init__.py file "
    "to your rule directory with a docstring."
)


def load_docs(
    result_collector: ResultCollector,
    validate_options: ValidateOptions,
    show_empty: bool = False,
) -> ExplorerData:
    """
    Load docstrings for several rule dirs

    Args:
        result_collector: ResultCollector where the found tests will deposit their
            results after being run
        validate_options: Dataclass for validate options
        show_empty: Whether or not to show show empty directories and files

    Returns:
        ExploreData object with doctstrings and rule directory structure
    """
    ruleset_dirs = discover_rulesets(validate_options=validate_options)
    filtered_dirs = filter_rulesets(ruleset_dirs, validate_options=validate_options)
    docs: Dict[str, List] = {}
    rule_dirs = []
    for dir in filtered_dirs:
        rule_dir_name = str(dir.parts[-2])
        rule_set_name = str(dir.parts[-1])
        docs[rule_dir_name] = docs.get(rule_dir_name, [])
        rule_set_doc = DEFAULT_FOLDER_DOCSTRING
        if Path.joinpath(dir, "__init__.py").exists():
            folder_path = Path.joinpath(dir, "__init__.py")
            glob = run_path(
                folder_path, ValidatorRegistry(folder_path), result_collector
            )
            rule_set_doc = glob.get("__doc__", rule_set_doc)

        paths = discover_rule_modules([dir])
        rule_files = load_docs_from_rule_files(
            result_collector, validate_options, paths, show_empty
        )
        if show_empty or len(rule_files) > 0:
            rule_set = RuleSetData(
                name=rule_set_name,
                docstring=rule_set_doc,
                rule_files=rule_files,
            )
            docs[rule_dir_name].append(rule_set)
    for rule_dir_name, rule_set_list in docs.items():
        if show_empty or len(rule_set_list) > 0:
            rule_dir = RuleDirData(
                name=rule_dir_name,
                rule_sets=rule_set_list,
            )
            rule_dirs.append(rule_dir)
    explorer = ExplorerData(rule_dirs=rule_dirs)
    return explorer


def load_docs_from_rule_files(
    result_collector: ResultCollector,
    validate_options: ValidateOptions,
    paths: List[Path],
    show_empty: bool = True,
) -> List[RuleFileData]:
    """
    Load docstrings for several rule files

    Args:
        result_collector: ResultCollector where the found tests will deposit their
            results after being run
        validate_options: Dataclass for validate options
        paths: Paths in which validation rules were found
        show_empty: Whether or not to show show empty directories and files

    Returns:
        List of RuleFileData objects
    """
    rule_files = []
    for path in paths:
        file_name = str(path.parts[-1])
        glob = run_path(path, ValidatorRegistry(path), result_collector)
        rule_list = load_rules_from_path(path, result_collector)
        rule_list = filter_rules(rule_list, validate_options)
        rules = []
        for rule in rule_list:
            rule_data = RuleData(
                name=rule.func.__name__,
                docstring=inspect.getdoc(rule.func) or DEFAULT_FUNC_DOCSTRING,
                path=path,
                ids_names=rule.ids_names,
            )
            rules.append(rule_data)
        if show_empty or len(rules) > 0:
            rule_file = RuleFileData(
                name=file_name,
                docstring=glob.get("__doc__", DEFAULT_MODULE_DOCSTRING),
                rules=rules,
            )
            rule_files.append(rule_file)
    return rule_files


def load_rules(
    result_collector: ResultCollector,
    validate_options: ValidateOptions,
) -> List[IDSValidationRule]:
    """
    Load IDSValidationRule objects from given rulesets and directories

    Args:
        result_collector: ResultCollector where the found tests will deposit their
            results after being run
        validate_options: Dataclass for validate options

    Returns:
        Loaded validation rules.
    """
    logger.info("Started loading rules")
    ruleset_dirs = discover_rulesets(validate_options=validate_options)
    filtered_dirs = filter_rulesets(ruleset_dirs, validate_options=validate_options)
    paths = discover_rule_modules(filtered_dirs)
    rules = []
    for path in paths:
        rules += load_rules_from_path(path, result_collector)
    logger.info(f"{len(rules)} total rules found")
    rules = filter_rules(rules, validate_options)
    if len(rules) == 0:
        logger.warning("No rules found after filtering")
    logger.info(f"{len(rules)} rules found after filtering")
    return rules


def discover_rulesets(validate_options: ValidateOptions) -> List[Path]:
    """
    Make a list of directories and child directories which might contain rules.

    Args:
        validate_options: Dataclass for validate options

    Returns:
        List of directories that might contain rules
    """
    rule_dirs: List[Path] = []
    # Ruleset directories from bundled, options and environment variable:
    for rule_dir in get_ruleset_directories(validate_options):
        if not rule_dir.exists():
            raise InvalidRulesetPath(rule_dir)
        rule_dirs.extend(_get_child_dirs(rule_dir))
    # Handle rulesets from entrypoints (TODO?)
    rule_dirs += handle_entrypoints()
    # Keep unique paths:
    rulesets = sorted(set(rule_dirs), key=attrgetter("name"))
    logger.info(
        f"Found {len(rulesets)} rulesets: {', '.join(rs.name for rs in rulesets)}"
    )
    return rulesets


def get_ruleset_directories(validate_options: ValidateOptions) -> List[Path]:
    """Return a list of directory Paths which contain rulesets.

    Args:
        validate_options: Dataclass for validate options
    """
    # Ruleset directories from options:
    ruleset_dirs = validate_options.extra_rule_dirs.copy()
    # Load bundled rule sets:
    if validate_options.use_bundled_rulesets:
        bundled_rule_dir = files(imas_validator) / "assets" / "rulesets"
        if not isinstance(bundled_rule_dir, Path):
            raise NotImplementedError(
                "Loading bundled rulesets is not (yet) supported when they are stored "
                "in a zipfile. Please raise an issue on https://jira.iter.org/."
            )
        ruleset_dirs.append(bundled_rule_dir)
    # Ruleset directories supplied through environment variable
    env_ruleset_paths = os.environ.get("RULESET_PATH", "")
    ruleset_dirs.extend(Path(part) for part in env_ruleset_paths.split(":") if part)
    return ruleset_dirs


def filter_rulesets(
    ruleset_dirs: List[Path],
    validate_options: ValidateOptions,
) -> List[Path]:
    """
    filter list of directories to only those that contain rulesets which should be
    applied

    Args:
        ruleset_dirs: List of directories in which to look for rulesets
        validate_options: Dataclass for validate options

    Returns:
        List of directories corresponding to given rule sets
    """
    filtered_rulesets: List[Path] = []
    for ruleset_dir in ruleset_dirs:
        name = ruleset_dir.name
        if name == "generic":
            if validate_options.apply_generic:
                filtered_rulesets.append(ruleset_dir)
        else:
            if (
                validate_options.explore and len(validate_options.rulesets) == 0
            ) or name in validate_options.rulesets:
                filtered_rulesets.append(ruleset_dir)
    filtered_ruleset_names = [p.name for p in filtered_rulesets]
    for ruleset in validate_options.rulesets:
        if ruleset not in filtered_ruleset_names:
            raise InvalidRulesetName(ruleset, ruleset_dirs)
    logger.info(f"Using {len(filtered_rulesets)} / {len(ruleset_dirs)} rulesets")
    return filtered_rulesets


def discover_rule_modules(ruleset_dirs: List[Path]) -> List[Path]:
    """
    Make a list of files that might contain rulesets

    Args:
        ruleset_dirs: List of directories in which to look for rulesets

    Returns:
        List of files that migth contain rulesets
    """
    rule_modules = []
    for ruleset_dir in ruleset_dirs:
        for path in ruleset_dir.iterdir():
            if path.is_file() and path.parts[-1] not in ["__init__.py"]:
                rule_modules.append(path)
    rule_modules = list(set(rule_modules))
    return rule_modules


def load_rules_from_path(
    rule_path: Path, result_collector: ResultCollector
) -> List[IDSValidationRule]:
    """
    Make a list of files that might contain rulesets

    Args:
        rule_path: Path for file that might contain rulesets
        result_collector: ResultCollector where the found tests will deposit their
            results after being run

    Returns:
        List IDSValidationRule objects from given file
    """
    if rule_path.suffix != ".py":
        logger.warning(
            f"Ignoring ruleset file: {str(rule_path)!r} is not a python file"
        )
        return []
    val_registry = ValidatorRegistry(rule_path)

    run_path(rule_path, val_registry, result_collector)
    if len(val_registry.validators) == 0:
        logger.warning(f"No rules in rule file {rule_path}")
    return val_registry.validators


def handle_entrypoints() -> List[Path]:
    """
    TODO: enable locating rulesets through entrypoints
    """
    return []


def _get_child_dirs(dir: Path) -> List[Path]:
    child_dirs = [
        path
        for path in dir.iterdir()
        if path.is_dir() and path.parts[-1] not in ["__pycache__"]
    ]
    return child_dirs


def filter_rules(
    rules: List[IDSValidationRule], validate_options: ValidateOptions
) -> List[IDSValidationRule]:
    """
    Filter a list of rules based on a given dictionary of criteria

    Args:
        rules: List of loaded IDSValidationRule objects
        validate_options: Dataclass for validate options

    Returns:
        List of directories corresponding to given rule sets
    """
    filtered_rules = [
        rule for rule in rules if validate_options.rule_filter.is_selected(rule)
    ]
    return filtered_rules
