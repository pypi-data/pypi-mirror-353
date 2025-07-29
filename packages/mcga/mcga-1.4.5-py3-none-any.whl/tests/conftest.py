import pytest
import builtins
import mcga
from mcga.core import original_import


@pytest.fixture(autouse=True)
def auto_cleanup():
    """Auto clean up MCGA state after each test"""
    yield
    try:
        mcga.disable_tariffs()
    except:
        builtins.__import__ = original_import
        mcga.core._tariff_sheet.clear()
        mcga.core._processed_modules.clear()
        mcga.core._chicken_courage = 100


@pytest.fixture
def clean_mcga():
    """Provide a clean MCGA state for testing"""
    mcga.disable_tariffs()
    mcga.restore_courage()
    mcga.clear_processed_modules()
    yield
    mcga.disable_tariffs()


@pytest.fixture
def sample_tariffs():
    """Provide sample tariff configurations for testing"""
    return {
        "low": {"numpy": 25},
        "medium": {"pandas": 100, "requests": 75},
        "high": {"scipy": 150, "matplotlib": 175},
        "max": {"tensorflow": 145}
    }


@pytest.fixture
def mock_modules():
    """Provide mock module names for safe testing"""
    return [
        "test_module_1",
        "test_module_2", 
        "safe_test_package",
        "mock_library"
    ]