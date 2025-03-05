from config import model

def classify_chunk_with_llm(chunk_text):
    '''Classifies a text chunk into Background, Methods, Results, Discussion, or Conclusion using LLM.'''
    prompt = f'''
    You are an AI assistant classifying research paper sections.
    The following text is an excerpt from a scientific paper.
    Determine whether it belongs to one of these sections:
    - Background
    - Methods
    - Results
    - Discussion
    - Conclusion

    If uncertain, choose the most relevant section.

    ---TEXT---
    {chunk_text}
    ------------------
    
    Output only the section name: 
    '''

    try:
        response = model.invoke(prompt).content.strip()
        valid_sections = {'Background', 'Methods', 'Results', 'Discussion', 'Conclusion'}
        
        classification = response if response in valid_sections else 'Background'
        # print(f'✅ LLM classified chunk as "{classification}"')
        return classification
    except Exception as e:
        print(f'⚠️ LLM classification failed: {e}. Defaulting to "Background".')
        return 'Background'