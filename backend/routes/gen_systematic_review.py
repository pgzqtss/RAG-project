from services.pinecone_service import search_pinecone, get_all_paper_ids
from utils.truncate_previous_sections import _get_fixed_limit_previous_sections
from utils.get_files import get_files
from services.section_prompts_service import (
  generate_background_section,
  generate_methods_section,
  generate_results_section,
  generate_discussion_section,
  generate_conclusion_section
)
from config import SECTION_CHAR_LIMIT
from flask import jsonify, request
from __main__ import app

@app.route('/api/generate', methods=['POST'])
def generate_full_systematic_review():
    '''Generate different sections of a Systematic Review step by step, each section processed independently'''
    data = request.json
    query = data.get('prompt')
    id = data.get('id')

    # (ISSUE: GETS ALL PAPERS IN INDEX NOT JUST THE ONES FOR ONE SYSTEMATIC REVIEW)
    # paper_ids = get_all_paper_ids()  # ✅ Get all stored paper IDs 
    
    paper_ids = [paper for paper in get_files(id)]

    systematic_review = {}  # Dictionary to store all generated sections

    print('🔍 Generating Background section...')
    background_results = search_pinecone(query, paper_ids=paper_ids, section='Background', top_k=50)
    systematic_review['Background'] = generate_background_section(
        results=background_results,
        query=query,
        chunk_size=30,
        previous_sections=[]
    )

    print('🔍 Generating Methods section...')
    methods_results = search_pinecone(query, paper_ids=paper_ids, section='Methods', top_k=50)
    systematic_review['Methods'] = generate_methods_section(
        results=methods_results,
        query=query,
        chunk_size=30,
        previous_sections=_get_fixed_limit_previous_sections(systematic_review, SECTION_CHAR_LIMIT)
    )

    print('🔍 Generating Results section...')
    results_results = search_pinecone(query, paper_ids=paper_ids, section='Results', top_k=50)
    systematic_review['Results'] = generate_results_section(
        results=results_results,
        query=query,
        chunk_size=30,
        previous_sections=_get_fixed_limit_previous_sections(systematic_review, SECTION_CHAR_LIMIT)
    )

    print('🔍 Generating Discussion section...')
    discussion_results = search_pinecone(query, paper_ids=paper_ids, section='Discussion', top_k=50)
    systematic_review['Discussion'] = generate_discussion_section(
        results=discussion_results,
        query=query,
        chunk_size=30,
        previous_sections=_get_fixed_limit_previous_sections(systematic_review, SECTION_CHAR_LIMIT)
    )

    print('🔍 Generating Conclusion section...')
    conclusion_results = search_pinecone(query, paper_ids=paper_ids, section='Conclusion', top_k=50)
    systematic_review['Conclusion'] = generate_conclusion_section(
        results=conclusion_results,
        query=query,
        chunk_size=30,
        previous_sections=_get_fixed_limit_previous_sections(systematic_review, SECTION_CHAR_LIMIT)
    )

    # Join all sections into one
    combined_sections = ''.join(systematic_review[section] + '\n' for section in systematic_review)

    print(f'Systematic Review: {combined_sections[:-1]}')

    # Remove last '\n'
    return jsonify({'systematic_review': combined_sections[:-1]}), 200 