import warnings

import pytest
from standard_names.standardname import StandardName
from standard_names.standardname import is_valid_name


def test_get_component_name(initialized_bmi):
    """Test component name is a string."""
    name = initialized_bmi.get_component_name()
    assert isinstance(name, str)


def test_var_names(var_name):
    """Test var names are valid."""
    assert isinstance(var_name, str)
    if is_valid_name(var_name):
        StandardName(var_name)
    else:
        warnings.warn(f"not a valid standard name: {var_name}", stacklevel=2)


@pytest.mark.dependency()
def test_input_var_name_count(initialized_bmi):
    if hasattr(initialized_bmi, "get_input_var_name_count"):
        n_names = initialized_bmi.get_input_var_name_count()
        assert isinstance(n_names, int)
        assert n_names >= 0
    else:
        pytest.skip("get_input_var_name_count not implemented")


@pytest.mark.dependency()
def test_output_var_name_count(initialized_bmi):
    if hasattr(initialized_bmi, "get_output_var_name_count"):
        n_names = initialized_bmi.get_output_var_name_count()
        assert isinstance(n_names, int)
        assert n_names >= 0
    else:
        pytest.skip("get_output_var_name_count not implemented")


@pytest.mark.dependency(depends=["test_input_var_name_count"])
def test_get_input_var_names(initialized_bmi):
    """Input var names is a list of strings."""
    names = initialized_bmi.get_input_var_names()
    assert isinstance(names, tuple)

    if hasattr(initialized_bmi, "get_input_var_name_count"):
        n_names = initialized_bmi.get_input_var_name_count()
        assert len(names) == n_names
    else:
        warnings.warn("get_input_var_name_count not implemented", stacklevel=2)


@pytest.mark.dependency(depends=["test_output_var_name_count"])
def test_get_output_var_names(initialized_bmi):
    """Output var names is a list of strings."""
    names = initialized_bmi.get_output_var_names()
    assert isinstance(names, tuple)

    if hasattr(initialized_bmi, "get_output_var_name_count"):
        n_names = initialized_bmi.get_output_var_name_count()
        assert len(names) == n_names
    else:
        warnings.warn("get_output_var_name_count not implemented", stacklevel=2)
