"""
This file describes the main function for the IMAS IDS validation tool
"""

import logging
import sys

import imas  # type: ignore
from packaging.version import Version

# from imas_validator.exceptions import IMASVersionError
from imas_validator.rules.loading import load_rules
from imas_validator.validate.result import IDSValidationResultCollection
from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate.rule_executor import RuleExecutor
from imas_validator.validate_options import ValidateOptions

logger = logging.getLogger(__name__)

default_val_opts = ValidateOptions()


def validate(
    imas_uri: str,
    validate_options: ValidateOptions = default_val_opts,
) -> IDSValidationResultCollection:
    """
    Main function

    Args:
        imas_uri: url for DBEntry object
        validate_options: dataclass with options for validate function

    Returns:
        List of IDSValidationResult objects
    """

    _check_imas_version()
    try:
        dbentry = imas.DBEntry(imas_uri, "r")
    except (imas.exception.ALException, imas.exception.LowlevelError) as e:
        logger.error(e)
        sys.exit(1)

    result_collector = ResultCollector(
        validate_options=validate_options, imas_uri=imas_uri
    )
    rules = load_rules(
        result_collector=result_collector,
        validate_options=validate_options,
    )
    rule_executor = RuleExecutor(
        dbentry, rules, result_collector, validate_options=validate_options
    )
    rule_executor.apply_rules_to_data()
    results_collection = result_collector.result_collection()
    logger.info(f"{len(results_collection.results)} results obtained")
    dbentry.close()
    return results_collection


def _check_imas_version() -> None:
    """Check if the installed IMAS version is sufficient."""
    # TODO: check if this is the best level to test for the IMAS version
    if not imas.backends.imas_core.imas_interface.has_imas:
        version_found = imas.backends.imas_core.imas_interface.ll_interface._al_version
        if version_found is None:
            logger.info(
                "No IMAS install could be found."
                "IDS Validation will work with limited functionality."
            )
            return
        else:
            logger.info(f"Found IMAS install with version {version_found}.")

    if imas.backends.imas_core.imas_interface.ll_interface._al_version < Version("5.1"):
        logger.info(
            "IDS Validation requires an IMAS installation of version 5.1 or newer."
            "See the README for more details."
        )

    # if not imas.backends.imas_core.imas_interface.has_imas:
    #     raise IMASVersionError()
    # if imas.backends.imas_core.imas_interface.ll_interface._al_version
    # < Version("5.1"):
    #     raise IMASVersionError(
    #         imas.backends.imas_core.imas_interface.ll_interface._al_version
    #     )
