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
    search_namespace,
    compute_summary_accuracy,
    filter_low_accuracy_papers,
    answer_question_for_paper,
    main
)

# Sets the enviornment variables with mock values temporarily
@patch.dict('os.environ', {'PINECONE_API_KEY': 'p-mock_key', 'OPENAI_API_KEY': 'o-mock_key'})
def test_environment_variables():
    # Test each environment variable is set correctly
    assert os.getenv('PINECONE_API_KEY') == 'p-mock_key'
    assert os.getenv('OPENAI_API_KEY') == 'o-mock_key'

def test_search_namespace():
    # Mock data
    query = 'What is the efficacy of vaccines for COVID-19?'
    index_name = 'test_index'
    namespace = 'test_namespace'
    embedding = MagicMock()
    top_k = 3

    # Mock the from_existing_index function with my own
    with patch('pipeline.LangchainPinecone.from_existing_index') as mock_from_existing_index:
        mock_docsearch = MagicMock()
        mock_docsearch.similarity_search.return_value = ['vector1', 'vector2', 'vector3']
        mock_from_existing_index.return_value = mock_docsearch

        result = search_namespace(query=query,
                                           index_name=index_name,
                                           namespace=namespace,
                                           embeddings=embedding,
                                           top_k=top_k)
        
        # Test functions are called with correct arguments
        mock_from_existing_index.assert_called_once_with(index_name=index_name,
                                                         namespace=namespace,
                                                         embedding=embedding)
        mock_docsearch.similarity_search.assert_called_once_with(query, k=top_k)

        # Test result is the same as the expected
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

        mock_invoke.assert_called_once()
        assert len(result) == 5
        # Test each question is a non-empty string
        for question in result:
            assert isinstance(question, str)
            assert question.split() != ''

def test_generate_review_answer():
    # Mock data
    question = 'What type of COVID-19 vaccine was studied in the research paper?'
    data = 'mock_data'
    paper = 'paper1'

    with patch('pipeline.ChatOpenAI.invoke') as mock_invoke:
        mock_response = MagicMock()
        mock_response.content = 'ZF2001'
        mock_invoke.return_value = mock_response

        # The OpenAI model is replaced with our own model with set return value
        mock_model = MagicMock()
        mock_model.invoke = mock_invoke

        result = generate_review_answer(question=question,
                                                 data=data,
                                                 paper=paper,
                                                 model=mock_model)
        
        # Test only one invoke is called
        mock_invoke.assert_called_once()
        # Test the result is the same as the set return value
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
        
        # Test there is a call for each question for each namespace
        assert mock_answer_question_for_paper.call_count == len(mock_namespaces) * len(mock_questions)
        assert expected_result == result
        
        # Test the calls to the mock function are the same as †he expected
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
        
        # Test the mock function is called once for each namespace
        assert mock_generate_summary.call_count == len(mock_namespaces)
        assert expected_result == result

        # Test each call has only 3 arguments
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
        
        # Test the invoke function is only called once and results are as expected
        mock_invoke.assert_called_once()
        assert result == mock_systematic_review

def test_compute_summary_accuracy():
    mock_summary = 'summary'
    mock_namespace = 'paper1'

    with patch('pipeline.search_namespace') as mock_search_namespace:
        mock_response = MagicMock()
        mock_response.content = 'Original text'
        mock_search_namespace.return_value = mock_response

        mock_model = MagicMock()
        mock_model.invoke.return_value.content = '70'

        result = compute_summary_accuracy(summary_text=mock_summary,
                                          namespace=mock_namespace,
                                          model=mock_model)

        # Test each function is called only once
        mock_search_namespace.assert_called_once()
        mock_model.invoke.assert_called_once()
        assert result == 70

# Differs from previous test by using invalid input (no digits)
def test_invalid_computer_summary_accuracy():
    mock_summary = 'summary'
    mock_namespace = 'paper1'

    with patch('pipeline.search_namespace') as mock_search_namespace:
        mock_search_namespace.return_value.content = 'Data'

        mock_model = MagicMock()
        mock_model.invoke.return_value.content = 'ABC'

        result = compute_summary_accuracy(summary_text=mock_summary,
                                          namespace=mock_namespace,
                                          model=mock_model)
        
        mock_search_namespace.assert_called_once()
        mock_model.invoke.assert_called_once()
        # Test the other branch is executed
        assert result == 0

def test_get_accuracy_score():
    mock_summaries = {
        'paper1': 'summary',
        'paper2': 'summary'
    }

    mock_namespaces = ['paper1', 'paper2']

    expected_result = {
        'paper1': 70,
        'paper2': 70
    }
    
    with patch('pipeline.compute_summary_accuracy') as mock_compute_summary_accuracy:
        mock_compute_summary_accuracy.return_value = 70

        mock_model = MagicMock()
        mock_model.invoke.return_value = 'Mock response'

        result = get_accuracy_score(summaries=mock_summaries, model=mock_model, namespaces=mock_namespaces)

        # Test the summary accuracy is computed once for each namespace
        assert mock_compute_summary_accuracy.call_count == len(mock_namespaces)
        assert expected_result == result

        # Test each call has only 3 arguments each
        calls = [call.arg for call in mock_compute_summary_accuracy.call_args_list]
        assert all(len(call) == 3 for call in calls)

def test_filter_low_accuracy_papers():
    mock_summaries = {
        'paper1': 'summary',
        'paper2': 'summary'
    }

    mock_model = MagicMock()
    mock_model.invoke.return_value = 'Mock response'

    expected_summaries = {
        'paper1': 'summary',
        'paper2': 'summary'
    }

    expected_scores = {
        'paper1': 70,
        'paper2': 70
    }

    with patch('pipeline.get_accuracy_score') as mock_get_accuracy_score:
        mock_get_accuracy_score.return_value = expected_scores

        result = filter_low_accuracy_papers(summaries=mock_summaries, model= mock_model)
        
        # Test values in the returned tuple are same as expected
        assert expected_summaries == result[0]
        assert expected_scores == result[1]

@patch('pipeline.search_namespace')
def test_answer_question_for_paper(mock_search_namespace):
    mock_query = 'What is COVID-19?'
    mock_namespace = 'paper1'
    mock_data = ['data1', 'data2']
    mock_answer = 'answer'

    with patch('pipeline.generate_review_answer') as mock_generate_review_answer:
        mock_search_namespace.return_value = mock_data
        mock_generate_review_answer.return_value = mock_answer

        result = answer_question_for_paper(question=mock_query,
                                            paper=mock_namespace)
        
        mock_search_namespace.assert_called_once()
        mock_generate_review_answer.assert_called_once()
        assert len(result) == 3

        # Test that each value in the returned tuple is same as expected
        assert result[0] == mock_query
        assert result[1] == mock_namespace
        assert result[2] == mock_answer

@patch('pipeline.generate_review_questions')
@patch('pipeline.generate_answers')
@patch('pipeline.generate_summaries')
@patch('pipeline.filter_low_accuracy_papers')
@patch('pipeline.generate_systematic_review')
def test_main(mock_generate_systematic_review, mock_filter_low_accuracy_papers,
                mock_generate_summaries, mock_generate_answers, mock_generate_review_questions):

    mock_generate_review_questions.return_value = ['What is the cost of the vaccine?']
    mock_generate_answers.return_value = {'paper1': ['answer'], 'paper2': ['answer']}
    mock_generate_summaries.return_value = {'paper1': 'summary2', 'paper2': 'summary2'}
    mock_filter_low_accuracy_papers.return_value = ({'paper1': 'summary1'}, {'paper1': 80})
    mock_generate_systematic_review.return_value = 'Mock systematic review'

    with patch('builtins.print') as mock_print:  # Mock print to verify output
        main()

        # Test the main function only calls each function once
        mock_generate_review_questions.assert_called_once()
        mock_generate_answers.assert_called_once()
        mock_generate_summaries.assert_called_once()
        mock_filter_low_accuracy_papers.assert_called_once()
        mock_generate_systematic_review.assert_called_once()

        # Test the print statements are the same as the expected strings
        mock_print.assert_any_call('Systematic Review: Mock systematic review')
        mock_print.assert_any_call("Scores: {'paper1': 80}")