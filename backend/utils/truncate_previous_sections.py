def _get_fixed_limit_previous_sections(systematic_review, section_char_limit):
    previous_sections = []

    # Iterate through the sections in the order they were generated
    for _, section_content in systematic_review.items():
        section_content_str = str(section_content)  # Ensure content is a string
        # Truncate the section to the first `section_char_limit` characters
        truncated_section = section_content_str[:section_char_limit]
        previous_sections.append(truncated_section)

    return previous_sections