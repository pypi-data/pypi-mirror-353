"""
Parsers provided by aiida_gromacs.

This parser adds the ability to parse the outputs of the 'gmx solvate' executable.
"""
import os
from pathlib import Path
from aiida.common import exceptions
from aiida.engine import ExitCode
from aiida.orm import SinglefileData
from aiida.parsers.parser import Parser
from aiida.plugins import CalculationFactory

SolvateCalculation = CalculationFactory("gromacs.solvate")


class SolvateParser(Parser):
    """
    Parser class for parsing output of calculation.
    """

    def __init__(self, node):
        """
        Initialize Parser instance

        Checks that the ProcessNode being passed was produced by a SolvateCalculation.

        :param node: ProcessNode of calculation
        :param type node: :class:`aiida.orm.nodes.process.process.ProcessNode`
        """
        super().__init__(node)
        if not issubclass(node.process_class, SolvateCalculation):
            raise exceptions.ParsingError("Can only parse SolvateCalculation")

    def parse(self, **kwargs):
        """
        Parse outputs, store results in database.

        :returns: an exit code, if parsing fails (or nothing if parsing succeeds)
        """
        # the directory for storing parsed output files
        output_dir = Path(self.node.get_option("output_dir"))
        outputs = ["stdout", "grofile", "topfile"]

        # Check that folder content is as expected
        files_retrieved = self.retrieved.base.repository.list_object_names()
        files_expected = [
            self.node.get_option("output_filename"),
            self.node.inputs.parameters["o"],
            self.node.inputs.topfile.filename,
        ]

        # Note: set(A) <= set(B) checks whether A is a subset of B
        if not set(files_expected) <= set(files_retrieved):
            self.logger.error(
                f"Found files '{files_retrieved}', expected to find '{files_expected}'"
            )
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILES

        # add outputs
        for index, thing in enumerate(files_expected):
            self.logger.info(f"Parsing '{thing}'")
            with self.retrieved.base.repository.open(thing, "rb") as handle:
                output_node = SinglefileData(filename=thing, file=handle)
            self.out(outputs[index], output_node)

        # If not in testing mode, then copy back the files.
        if "PYTEST_CURRENT_TEST" not in os.environ:
            self.retrieved.copy_tree(output_dir)

        return ExitCode(0)
