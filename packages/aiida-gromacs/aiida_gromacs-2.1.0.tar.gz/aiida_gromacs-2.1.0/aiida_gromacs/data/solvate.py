"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from voluptuous import Optional, Required, Schema

from aiida.orm import Dict

# A subset of solvate command line options
cmdline_options = {
    Required("cs", default="spc216.gro"): str,
    Required("o", default="solvated.gro"): str,
    Optional("box"): str,
    Optional("radius"): str,
    Optional("scale"): str,
    Optional("shell"): str,
    Optional("maxsol"): str,
    Optional("vel"): str,
}


class SolvateParameters(Dict):  # pylint: disable=too-many-ancestors
    """
    Command line options for diff.

    This class represents a python dictionary used to
    pass command line options to the executable.
    """

    # "voluptuous" schema  to add automatic validation
    schema = Schema(cmdline_options)

    # pylint: disable=redefined-builtin
    def __init__(self, dict=None, **kwargs):
        """
        Constructor for the data class

        Usage: ``SolvateParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(SolvateParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return SolvateParameters.schema(parameters_dict)

    def cmdline_params(self, grofile, topfile):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param grofile: Name of input gro file
        :param type grofile: str

        """
        parameters = []

        parameters.append("solvate")
        parameters.extend(["-cp", grofile])
        parameters.extend(["-p", topfile])

        parm_dict = self.get_dict()

        for key, value in parm_dict.items():
            parameters.extend(["-" + key, value])

        return [str(p) for p in parameters]

    def __str__(self):
        """String representation of node.

        Append values of dictionary to usual representation. E.g.::

            uuid: b416cbee-24e8-47a8-8c11-6d668770158b (pk: 590)
            {'ignore-case': True}

        """
        string = super().__str__()
        string += "\n" + str(self.get_dict())
        return string
