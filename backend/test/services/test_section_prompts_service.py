import sys
import os
import pytest

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from services.section_prompts_service import generate_background_section

def test_generate_background_section(monkeypatch):
    monkeypatch.setattr(
        "services.section_prompts_service.generate_section",
        lambda results, query, section_title, section_prompt, chunk_size, previous_sections: "Background Section Content"
    )
    result = generate_background_section(["dummy_result"], "Test query", 30, [])
    assert result == "Background Section Content"
