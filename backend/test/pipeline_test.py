from unittest.mock import MagicMock, patch
import os
import pipeline

@patch.dict('os.environ', {'PINECONE_API_KEY': 'p-mock_key', 'OPENAI_API_KEY': 'o-mock_key'})
def test_environment_variables():
    # Test each environment variable is set correctly
    assert os.getenv('PINECONE_API_KEY') == 'p-mock_key'
    assert os.getenv('OPENAI_API_KEY') == 'o-mock_key'

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

        result = pipeline.generate_review_questions(mock_model)

        # Test the invoke method is called only once
        mock_invoke.assert_called_once()
        assert len(result) == 5
        for question in result:
            assert isinstance(question, str)
            assert question.split() != ''