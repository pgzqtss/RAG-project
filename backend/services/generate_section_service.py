import textwrap
from sentence_transformers import util
from config import model, bert_model, SECTION_LENGTH_LIMITS

def generate_section(results, query, section_title, section_prompt, 
                     previous_sections=None, chunk_size=30, similarity_threshold=0.8):
    '''
    Generates a **Systematic Review** section with:
    - **Context awareness** (previously generated sections as input)
    - **De-duplication** (removes redundant content using BERT-based similarity checking)
    - **Smooth transitions** (AI is explicitly instructed to generate transition sentences)
    - **Flexible length control** (section-specific length limits)
    
    Parameters:
    - results: Research data in chunks
    - query: Current research topic
    - model: AI model for text generation
    - section_title: The title of the section being generated
    - section_prompt: Writing instructions for the section
    - previous_sections: Previously generated sections (to enhance continuity)
    - chunk_size: Number of data chunks to use for context
    - similarity_threshold: Sentence similarity threshold for de-duplication
    '''

    seen_sentences = set()  # Store unique sentences

    # 🔥 Ensure `previous_sections` is always a list
    if not isinstance(previous_sections, list):  
        previous_sections = []  # Force conversion to an empty list to ensure no errors

    # Retrieve the max length for this section
    max_length = SECTION_LENGTH_LIMITS.get(section_title, 1500)  # Default to 1500 words if unspecified

    # 1️⃣ **Context Expansion** (Use both research data and previously generated sections)
    context_data = '\n\n'.join(results[:chunk_size]) if results else ''

    # 🔥 Prevent `join()` from throwing errors by ensuring previous_sections is a list and does not contain non-string elements
    previous_content = '\n\n'.join(str(s) for s in previous_sections) if previous_sections else ''

    if previous_content:
        context_data = previous_content + '\n\n' + context_data  # Append previous sections for better flow

    # 2️⃣ **Construct the Prompt**
    prompt = textwrap.dedent(f'''
    # 📚 **Systematic Review Writing Task: {section_title}**

    You are an expert researcher conducting a **Systematic Review** following **PRISMA guidelines**. 
    Your task is to generate the **{section_title}** section in a **structured, evidence-based, and academic** manner.

    ## 🔍 **Key Writing Guidelines**

    - Follow **PRISMA guidelines** for transparency & reproducibility.
    - Use **formal academic language** and ensure logical coherence with previous sections.
    - **Maintain logical flow** with clear transition sentences.
    - **Avoid redundancy**—summarize rather than repeat ideas.

    ## 📌 **Context (Original Query, Previously Generated Sections & Research Data)**

    Below is the **original query** that sets the topic of the systematic review, followed by previously generated content and relevant research data:

    ```
    {query}
    ```

    ```
    {context_data}
    ```

    ## 🛠 **Instructions for Writing This Section**
    {section_prompt}

    - Use this data as a reference to ensure consistency.
    - If methodology or prior findings are referenced, align your section accordingly.

    ## 🛠 **Instructions for Writing This Section**

    ## 🎯 **Output Constraints**

    - **Format:** Use clear headings & subheadings where necessary.
    - **Word Limit:** Aim for **{max_length} words**, prioritizing essential details.
    - **Clarity & Coherence:** Ensure smooth readability and logical consistency.

    ## 📝 **Now, generate the full {section_title} section:**


    ''')

    try:
        response = model.invoke(prompt).content if model else None

        # 🔥 **Check if response is None**
        if response is None or not isinstance(response, str):
            raise ValueError(f'AI model did not return a valid response for {section_title}')

        response = response.strip()

        # 🔥 **Check if response is empty**
        if not response:
            raise ValueError(f'Generated response is empty for {section_title}')

        # Limit the text length based on the predefined constraints
        response = response[:max_length * 6]  # Approximate conversion: 1 word ≈ 6 characters
        
        # 4️⃣ **Deduplication Logic**
        generated_sentences = response.split('\n')
        unique_sentences = []

        for sentence in generated_sentences:
            if sentence.strip() and sentence not in seen_sentences:
                unique_sentences.append(sentence)
                seen_sentences.add(sentence)

        # 5️⃣ **BERT-based Semantic Deduplication**
        filtered_sentences = []
        for sentence in unique_sentences:
            if not filtered_sentences:  # First sentence is always added
                filtered_sentences.append(sentence)
                continue
            
            # Compute similarity between new sentence and existing filtered ones
            embeddings1 = bert_model.encode([sentence], convert_to_tensor=True)
            embeddings2 = bert_model.encode(filtered_sentences, convert_to_tensor=True)
            similarity_scores = util.pytorch_cos_sim(embeddings1, embeddings2).mean().item()

            # Only add sentence if it is not too similar to previous ones
            if similarity_scores < similarity_threshold:
                filtered_sentences.append(sentence)

        final_section = '\n'.join(filtered_sentences)  # Return the final cleaned section
        
        # ✅ **Append the generated section to previous_sections for future use**
        previous_sections.append(final_section)

        return final_section

    except ValueError as ve:
        print(f'⚠️ ValueError in {section_title}: {ve}')
        return ''
    except Exception as e:
        print(f'⚠️ Unexpected error in {section_title}: {e}')
        return ''