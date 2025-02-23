import textwrap
from services.generate_section_service import generate_section

def generate_background_section(results, query, chunk_size, previous_sections):
    '''单独生成 Background 章节'''
    section_title = 'Background'
    section_prompt = textwrap.dedent(f'''
        {section_title}
                                        
        Generate the {section_title} section for the systematic review using the relevant information from the retrieved documents. 
        Integrate findings directly from the provided sources and ensure all claims are supported by the retrieved evidence.

        🔹 Required Content:
            1.	Introduction to the Topic:
                •	Introduce the research topic and highlight its significance using insights from the most relevant retrieved documents.
                •	Define essential concepts based on the retrieved material, ensuring consistency with the latest research.
                •	Discuss the broader relevance of the topic, drawing on real-world examples or applications mentioned in the retrieved sources.
            2.	Summary of Existing Literature:
                •	Summarize key findings from the retrieved documents, focusing on significant trends, major discoveries, and methodologies.
                •	Critically assess the strengths, limitations, and relevance of the studies retrieved.
                •	Address inconsistencies or conflicting evidence found in the sources, offering possible explanations or highlighting gaps.
            3.	Justification for This Systematic Review:
                •	Clearly explain why this review is necessary based on the gaps or unresolved issues identified in the retrieved documents.
                •	Describe how this review will address limitations or contribute new insights beyond what the retrieved studies have already established.
                •	Define the research question clearly. Use frameworks like PICO (Population, Intervention, Comparison, Outcome) only if supported by the retrieved material.

        🔹 Writing Style and Source Integration Guidelines:

        ✅ Use a formal, academic tone appropriate for scholarly work
        ✅ Prioritize evidence from the retrieved sources to support all claims
        ✅ Avoid including information not supported by the retrieved evidence.
        ✅ Address conflicting information from different sources, providing analysis or explanation
        ✅ Focus on depth and relevance—highlight the most pertinent findings
        ✅ Adapt the depth of each section based on the relevance and strength of the retrieved evidence
    ''').strip()
    
    return generate_section(
        results=results,
        query=query,
        section_title=section_title,
        section_prompt=section_prompt,
        chunk_size=chunk_size,
        previous_sections=previous_sections
    )


def generate_methods_section(results, query, chunk_size, previous_sections):
    '''Generate the Methods section for a Systematic Review following PRISMA guidelines.'''
    
    section_title = 'Methods'
    section_prompt = textwrap.dedent(f'''
        {section_title}
                                     
        Generate the {section_title} section for the Systematic Review using relevant information retrieved through a RAG system. 
        The output should follow the structure of a systematic review, emphasizing clarity, logical flow, and evidence-based reasoning.

        🔹 Required Content:
            1.	Study Design:
                •	Specify this is a Systematic Review.
                •	State that the methodology aligns with PRISMA guidelines where applicable, focusing on transparency and reproducibility.
            2.	Evidence Synthesis:
                •	Summarize the key themes and findings from the retrieved research.
                •	Highlight any consistent patterns, agreements, or notable contrasts in the evidence.
            3.	Inclusion Rationale:
                •	Emphasize the relevance of the information retrieved to the query.
                •	Clearly explain why certain insights were prioritized (e.g. relevance to the research question, recent developments).
            4.	Strengths and Limitations of Retrieved Information:
                •	Discuss the general strengths of the body of information retrieved.
                •	Note any potential gaps, such as limited coverage or conflicting information.
            5.	Key Insights Summary:
                •	Present major findings, outcomes, or conclusions derived from the available data.
                •	Focus on clear, concise summaries without requiring detailed statistical breakdowns.

        🔹 Writing Style:

        ✅ Clear, structured, and evidence-informed
        ✅ No citations required—focus on summarizing key points
        ✅ Present insights logically, highlighting relevance to the research query  
    ''').strip()

    return generate_section(
        results=results,
        query=query,
        section_title=section_title,
        section_prompt=section_prompt,
        chunk_size=chunk_size,
        previous_sections=previous_sections
    )


def generate_results_section(results, query, chunk_size, previous_sections):
    '''Generate the Results section for a Systematic Review.'''

    section_title = 'Results'
    section_prompt = textwrap.dedent(f'''
        {section_title}                             

        Generate the {section_title} section for the Systematic Review using relevant information retrieved through a RAG system. Structure the content logically and focus on summarizing the key findings from the retrieved information.

        🔹 Required Content:
            1.	Relevant Information Summary:
                •	Provide a general overview of the information retrieved that is relevant to the research query.
                •	Focus on summarizing the main themes and findings present across the retrieved documents.
            2.	Study Types and Methodological Insights (If Available):
                •	Briefly describe any study types or methodological details that appear in the retrieved information (e.g., experimental research, observational analysis).
                •	Only include this information if it is explicitly mentioned in the retrieved content.
            3.	Key Findings and Themes:
                •	Present a clear, concise summary of major findings from the retrieved content.
                •	Highlight recurring themes or notable differences, without inferring patterns from incomplete information.
            4.	General Observations and Gaps:
                •	Mention any apparent gaps in the retrieved information, such as missing data on certain outcomes or study populations.
                •	Avoid making assumptions—only report what is supported by the retrieved content.

        🔹 Writing Style:

        ✅ Focused on clear, unbiased summaries
        ✅ Only present information directly supported by retrieved content
        ✅ Flexible structure, prioritizing relevance over strict formatting
    ''').strip()

    return generate_section(
        results=results,
        query=query,
        section_title=section_title,
        section_prompt=section_prompt,
        chunk_size=chunk_size,
        previous_sections=previous_sections
    )


def generate_discussion_section(results, query, chunk_size, previous_sections):
    '''Generate the Discussion section for a Systematic Review.'''

    section_title = 'Discussion'
    section_prompt = textwrap.dedent(f'''
        {section_title}

        Generate the {section_title} section for the Systematic Review using relevant information retrieved through a RAG system. 
        Focus on summarizing the most relevant findings, clearly presenting insights while acknowledging any gaps or inconsistencies.

        🔹 Required Content:
            1.	Summary of Main Findings:
                •	Concisely summarize the key results from the retrieved content.
                •	Highlight consistent themes and acknowledge any conflicting information without attempting to resolve discrepancies.
            2.	Interpretation of Findings:
                •	Discuss potential explanations supported by the retrieved evidence.
                •	Where applicable, note any preliminary findings or well-established conclusions relevant to the research topic.
            3.	Strengths and Limitations of Retrieved Information:
                •	Describe strengths of the available information (e.g., relevance, breadth of coverage).
                •	Address limitations, including gaps, conflicting findings, or lack of depth in the retrieved content.
            4.	Potential Areas for Future Research:
                •	Suggest general future research directions based on observed gaps or trends in the retrieved evidence.
                •	Avoid proposing specific methodological recommendations unless explicitly supported by the retrieved information.

        🔹 Additional Guidelines:

        ✅ Prioritize the most relevant and clearly supported findings
        ✅ Acknowledge conflicting evidence without resolving it
        ✅ Use cautious, evidence-based language (e.g., “may suggest,” “potentially indicates”)
        ✅ Clearly state when information is incomplete or lacking depth 
    ''').strip()

    return generate_section(
        results=results,
        query=query,
        section_title=section_title,
        section_prompt=section_prompt,
        chunk_size=chunk_size,
        previous_sections=previous_sections
    )


def generate_conclusion_section(results, query, chunk_size, previous_sections):
    '''Generate the Conclusion section for a Systematic Review.'''

    section_title = 'Conclusion'
    section_prompt = textwrap.dedent(f'''
        {section_title}

        Generate the {section_title} section for a Systematic Review using the following structure and guidelines:

        🔹 Required Content:

        1.  Concise Summary of Key Findings:
            •   Summarize the most critical findings from the study, focusing on outcomes that are strongly supported by the retrieved evidence.
            •   Ensure the summary is clear, concise, and directly tied to the data retrieved by the RAG system.
        2.  Clinical & Public Health Implications:
            •   Highlight practical implications for healthcare practice or policy, based on the retrieved evidence.
            •   Clearly state limitations and uncertainties to avoid overgeneralization.
            •   Use cautious language (e.g., 'may suggest,' 'could potentially') when discussing implications that are not definitively supported by the evidence.
        3.  Final Recommendations:
            •   Propose specific, actionable next steps for research or practice, addressing gaps or limitations identified in the retrieved evidence.
            •   Avoid generic statements like 'more research is needed'—instead, specify the type of research or areas requiring further investigation.
            •   Ensure recommendations are grounded in the findings and directly linked to the retrieved data.
        🔹 Writing Style:

        ✅ Evidence-based and precise: Use only information retrieved by the RAG system. Do not introduce new ideas or unsupported claims.
        ✅ Structured and logical: Ensure a clear flow from summary to implications to recommendations.
        ✅ Cautious and balanced: Acknowledge limitations and avoid overstating results.
        ✅ Actionable and specific: Provide tailored recommendations that are practical and relevant to stakeholders.
    ''').strip()

    return generate_section(
        results=results,
        query=query,
        section_title=section_title,
        section_prompt=section_prompt,
        chunk_size=chunk_size,
        previous_sections=previous_sections
    )