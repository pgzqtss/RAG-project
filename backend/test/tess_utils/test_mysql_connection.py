import pytest
from unittest.mock import patch, MagicMock
import mysql.connector
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.mysql_connection import connect_to_database 

@patch("mysql.connector.connect")
def test_connect_to_database(mock_connect):
    """Test that connect_to_database() calls mysql.connector.connect with the correct arguments."""
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection

    conn = connect_to_database()

    mock_connect.assert_called_once()

    # Get the actual arguments passed to `mysql.connector.connect`
    call_args = mock_connect.call_args[1] 


    assert call_args["host"] == "localhost"
    assert call_args["user"] == "root"
    assert call_args["database"] == "user_data"
    assert isinstance(call_args["password"], str) 

    # Check that the function returns the correct mocked connection
    assert conn == mock_connection
