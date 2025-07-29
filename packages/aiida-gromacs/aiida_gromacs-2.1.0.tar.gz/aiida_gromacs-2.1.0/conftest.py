"""pytest fixtures for simplified testing."""
import pytest

pytest_plugins = ["aiida.manage.tests.pytest_fixtures"]


@pytest.fixture(scope="function", autouse=True)
def clear_database_auto(aiida_profile_clean):  # pylint: disable=unused-argument
    """Automatically clear database in between tests."""


@pytest.fixture(scope="function")
def gromacs_code(aiida_local_code_factory):
    """Get a gromacs code."""
    return aiida_local_code_factory(executable="gmx", entry_point="gromacs")


@pytest.fixture(scope="function")
def bash_code(aiida_local_code_factory):
    """Get a bash code."""
    return aiida_local_code_factory(executable="bash", entry_point="gromacs")
