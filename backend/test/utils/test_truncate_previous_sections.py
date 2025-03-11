import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.truncate_previous_sections import _get_fixed_limit_previous_sections 

def test_get_fixed_limit_previous_sections():
    """Test truncating previous sections to the given character limit."""
    systematic_review = {
        "Introduction": "This is a long introduction section.",
        "Methods": "This method section is quite detailed.",
        "Results": "Results are significant and detailed.",
    }
    
    section_char_limit = 10
    result = _get_fixed_limit_previous_sections(systematic_review, section_char_limit)
    print("DEBUG: result =", result)

    assert result == [
        "This is a ",  # Truncated to 10 chars
        "This metho",  # Truncated to 10 chars
        "Results ar"  # Truncated to 10 chars
    ]
