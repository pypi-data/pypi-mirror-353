import argparse
import logging
from pathlib import Path

from imas_validator.common.utils import (
    flatten_2d_list_or_return_empty,
    prepare_rule_filter_object,
)
from imas_validator.validate.validate import validate
from imas_validator.validate_options import ValidateOptions

from .command_generic import GenericCommand


class ValidateCommand(GenericCommand):
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self, args: argparse.Namespace) -> None:
        super(ValidateCommand, self).__init__(args)
        self._uri = args.uri[0]
        self.validate_options = ValidateOptions(
            rulesets=flatten_2d_list_or_return_empty(args.ruleset),
            extra_rule_dirs=[
                Path(element)
                for element in flatten_2d_list_or_return_empty(args.extra_rule_dirs)
            ],
            apply_generic=args.no_generic,
            use_pdb=args.debug,
            use_bundled_rulesets=not args.no_bundled,  # invert logic
            track_node_dict=args.node_coverage,
            rule_filter=prepare_rule_filter_object(args),
            explore=False,
        )

    def execute(self) -> None:
        super().execute()
        self._result = validate(
            imas_uri=self._uri, validate_options=self.validate_options
        )

    def __str__(self) -> str:
        return f"VALIDATE URI={self._uri} VALIDATE_OPTIONS={self.validate_options}"
