from unittest.mock import MagicMock, patch
import os
from pipeline import (
    generate_answers,
    generate_review_answer,
    generate_review_questions,
    generate_summaries,
    generate_summary,
    generate_systematic_review,
    get_accuracy_score,
    search_namespace
)

@patch.dict('os.environ', {'PINECONE_API_KEY': 'p-mock_key', 'OPENAI_API_KEY': 'o-mock_key'})
def test_environment_variables():
    # Test each environment variable is set correctly
    assert os.getenv('PINECONE_API_KEY') == 'p-mock_key'
    assert os.getenv('OPENAI_API_KEY') == 'o-mock_key'

def test_search_namespace():
    query = 'What is the efficacy of vaccines for COVID-19?'
    index_name = 'test_index'
    namespace = 'test_namespace'
    embedding = MagicMock()
    top_k = 3

    with patch('pipeline.LangchainPinecone.from_existing_index') as mock_from_existing_index:
        mock_docsearch = MagicMock()
        mock_docsearch.similarity_search.return_value = ['vector1', 'vector2', 'vector3']
        mock_from_existing_index.return_value = mock_docsearch

        result = search_namespace(query=query,
                                           index_name=index_name,
                                           namespace=namespace,
                                           embeddings=embedding,
                                           top_k=top_k)
        
        mock_from_existing_index.assert_called_once_with(index_name=index_name,
                                                         namespace=namespace,
                                                         embedding=embedding)
        mock_docsearch.similarity_search.assert_called_once_with(query, k=top_k)
        assert result == ['vector1', 'vector2', 'vector3']

def test_generate_review_questions():
    mock_questions = '''
    1. What type of COVID-19 vaccine was studied in the research paper?
    2. What was the sample size and demographic characteristics of the study population?
    3. What were the primary outcomes measured to assess the efficacy of the COVID-19 vaccine?
    4. What were the key findings regarding the efficacy of the COVID-19 vaccine in preventing infection or reducing severity of illness?
    5. Were there any reported adverse events or side effects associated with the COVID-19 vaccine in the study?
    '''
    # Mock the model's invoke method with my own
    with patch('pipeline.ChatOpenAI.invoke') as mock_invoke:
        # Return a mock response from custom invoke
        mock_response = MagicMock()
        mock_response.content = mock_questions
        mock_invoke.return_value = mock_response

        # Mock model with mock invoke to trigger function call
        mock_model = MagicMock()
        mock_model.invoke = mock_invoke

        result = generate_review_questions(mock_model)

        # Test the invoke method is called only once
        mock_invoke.assert_called_once()
        assert len(result) == 5
        for question in result:
            assert isinstance(question, str)
            assert question.split() != ''

def test_generate_review_answer():
    question = 'What type of COVID-19 vaccine was studied in the research paper?'
    data = 'mock_data'
    paper = 'paper1'

    with patch('pipeline.ChatOpenAI.invoke') as mock_invoke:
        mock_response = MagicMock()
        mock_response.content = 'ZF2001'
        mock_invoke.return_value = mock_response

        mock_model = MagicMock()
        mock_model.invoke = mock_invoke

        result = generate_review_answer(question=question,
                                                 data=data,
                                                 paper=paper,
                                                 model=mock_model)
        
        mock_invoke.assert_called_once()
        assert result == 'ZF2001'

def test_generate_answers():
    mock_questions = ['question1','question2']
    mock_namespaces = ['paper1', 'paper2']
    mock_answer = ['question1', 'paper1', 'answer1']

    expected_result = {
        'paper1': ['answer1','answer1'],
        'paper2': ['answer1','answer1']
    }

    with patch('pipeline.answer_question_for_paper') as mock_answer_question_for_paper:
        mock_answer_question_for_paper.return_value = mock_answer

        result = generate_answers(questions=mock_questions, namespaces=mock_namespaces)
        
        assert mock_answer_question_for_paper.call_count == len(mock_namespaces) * len(mock_questions)
        assert expected_result == result
        
        expected_calls = [
            ('question1','paper1'),
            ('question2','paper1'),
            ('question1','paper2'),
            ('question2','paper2')
        ]
        calls = [call.args for call in mock_answer_question_for_paper.call_args_list]
        assert expected_calls == calls

def test_generate_summary():
    mock_answers = 'answers'
    mock_paper = 'paper1'
    mock_summary = 'summary'

    with patch('pipeline.ChatOpenAI.invoke') as mock_invoke:
        mock_response = MagicMock()
        mock_response.content = mock_summary
        mock_invoke.return_value = mock_response

        mock_model = MagicMock()
        mock_model.invoke = mock_invoke

        result = generate_summary(answers=mock_answers,
                                           paper=mock_paper,
                                           model=mock_model)

        mock_invoke.assert_called_once()
        assert result == mock_summary

def test_generate_summaries():
    mock_answers = {
        'paper1': ['answer1','answer2'],
        'paper2': ['answer1','answer2']
    }
    mock_namespaces = ['paper1','paper2']
    mock_summary = 'summary'

    expected_result = {
        'paper1': 'summary',
        'paper2': 'summary'
    }

    with patch('pipeline.generate_summary') as mock_generate_summary:
        mock_generate_summary.return_value = mock_summary

        result = generate_summaries(answers=mock_answers, namespaces=mock_namespaces)
        
        assert mock_generate_summary.call_count == len(mock_namespaces)
        assert expected_result == result

        calls = [call.args for call in mock_generate_summary.call_args_list]
        assert all(len(call) == 3 for call in calls)

def test_generate_systematic_review():
    mock_summaries = {
        'paper1': 'summary',
        'paper2': 'summary'
    }
    mock_query = 'What is the efficacy of COVID-19 vaccines?'
    mock_systematic_review = 'Mock systematic review'

    with patch('pipeline.ChatOpenAI.invoke') as mock_invoke:
        mock_response = MagicMock()
        mock_response.content = mock_systematic_review
        mock_invoke.return_value = mock_response

        mock_model = MagicMock()
        mock_model.invoke = mock_invoke

        result = generate_systematic_review(summaries=mock_summaries,
                                            query=mock_query,
                                            model=mock_model)

        mock_invoke.assert_called_once()
        assert result == mock_systematic_review

def test_compute_summary_accuracy():
    pass

def test_get_accuracy_score():
    pass

def test_filter_low_accuracy_papers():
    pass