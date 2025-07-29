"""
Data types provided by plugin

Register data types via the "aiida.data" entry point in setup.json.
"""

# You can directly use or subclass aiida.orm.data.Data
# or any other data type listed under 'verdi data'
from voluptuous import Optional, Required, Schema

from aiida.orm import Dict

# A subset of pdb2gmx command line options
cmdline_options = {
    Required("o", default="conf.gro"): str,
    Required("p", default="topol.top"): str,
    Required("i", default="posre.itp"): str,
    Optional("n"): str,
    Optional("q"): str,
    Optional("chainsep"): str,
    Optional("merge"): str,
    Required("ff", default="oplsaa"): str,
    Required("water", default="spce"): str,
    Optional("inter"): str,
    Optional("ss"): str,
    Optional("ter"): str,
    Optional("lys"): str,
    Optional("arg"): str, 
    Optional("asp"): str,
    Optional("glu"): str,
    Optional("gln"): str,
    Optional("his"): str,
    Optional("angle"): str,
    Optional("dist"): str, 
    Optional("una"): str, 
    Optional("ignh"): str,
    Optional("missing"): str,
    Optional("v"): str,
    Optional("posrefc"): str,
    Optional("vsite"): str,
    Optional("heavyh"): str,
    Optional("deuterate"): str,
    Optional("chargegrp"): str,
    Optional("cmap"): str,
    Optional("renum"): str,
    Optional("rtpres"): str,
}


class Pdb2gmxParameters(Dict):  # pylint: disable=too-many-ancestors
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

        Usage: ``Pdb2gmxParameters(dict{'ignore-case': True})``

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict

        """
        dict = self.validate(dict)
        super().__init__(dict=dict, **kwargs)

    def validate(self, parameters_dict):
        """Validate command line options.

        Uses the voluptuous package for validation. Find out about allowed keys using::

            print(Pdb2gmxParameters).schema.schema

        :param parameters_dict: dictionary with commandline parameters
        :param type parameters_dict: dict
        :returns: validated dictionary
        """
        return Pdb2gmxParameters.schema(parameters_dict)

    def cmdline_params(self, pdbfile):
        """Synthesize command line parameters.

        e.g. [ '--ignore-case', 'filename1', 'filename2']

        :param pdbfile: Name of input pdb file
        :param type pdbfile: str

        """
        parameters = []

        parameters.append("pdb2gmx")
        parameters.extend(["-f", pdbfile])

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
