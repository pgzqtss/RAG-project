import warnings
import pytest

@pytest.fixture(autouse=True)
def suppress_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="google")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")
