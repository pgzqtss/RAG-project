import pytest
from unittest.mock import MagicMock, patch
import os
import importlib

# 先导入配置模块和 mysql_connection 模块
import config
import utils.mysql_connection as mysql_conn

# 修改环境变量后，重新加载 config 和 mysql_connection 模块
def test_connect_to_database(monkeypatch):
    # 设置环境变量 MYSQL_PASSWORD 为 "dummy"
    monkeypatch.setenv("MYSQL_PASSWORD", "dummy")
    # 重新加载 config 模块
    importlib.reload(config)
    # 重新加载 mysql_connection 模块，以便使用更新后的 config
    importlib.reload(mysql_conn)
    
    from utils.mysql_connection import connect_to_database

    with patch("mysql.connector.connect") as mock_connect:
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        conn = connect_to_database()
        mock_connect.assert_called_once()

        # 获取传递给 mysql.connector.connect 的参数
        call_args = mock_connect.call_args[1]
        assert call_args["host"] == "localhost"
        assert call_args["user"] == "root"
        assert call_args["database"] == "user_data"
        # 此时 password 应该为 "dummy"
        assert isinstance(call_args["password"], str)
        assert call_args["password"] == "dummy"

if __name__ == '__main__':
    test_connect_to_database(monkeypatch=pytest.MonkeyPatch())
    print("MySQL connection test passed")
