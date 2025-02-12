import pytest
from unittest.mock import patch, MagicMock, call
import sqlite3
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pages')))

from login import get_db_connection

class TestDatabaseConnection:
    
    def test_get_db_connection(self):
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            
            conn = get_db_connection()
            
            mock_connect.assert_called_once_with('crm.db')
            assert conn.row_factory == sqlite3.Row
            assert conn is not None
    
    def test_get_db_connection_row_factory(self):
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            
            conn = get_db_connection()
            
            mock_connect.assert_called_once_with('crm.db')
            assert conn.row_factory == sqlite3.Row

    def test_get_db_connection_closes_properly(self):
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            
            conn = get_db_connection()
            
            mock_connect.assert_called_once_with('crm.db')
            assert conn.row_factory == sqlite3.Row
            
            conn.close()
            mock_conn.close.assert_called_once()

    def test_get_db_connection_concurrent(self):
        with patch('sqlite3.connect') as mock_connect:
            mock_conn1 = MagicMock()
            mock_conn2 = MagicMock()
            mock_connect.side_effect = [mock_conn1, mock_conn2]

            # Simulate concurrent connections
            conn1 = get_db_connection()
            conn2 = get_db_connection()

            # Assert that two separate connections were created
            assert conn1 is not conn2
            assert mock_connect.call_count == 2
            mock_connect.assert_has_calls([call('crm.db'), call('crm.db')])

            # Verify that row_factory was set for both connections
            assert conn1.row_factory == sqlite3.Row
            assert conn2.row_factory == sqlite3.Row

    def test_get_db_connection_multiple_requests(self):
        connections = []
        for _ in range(5):
            conn = get_db_connection()
            assert isinstance(conn, sqlite3.Connection)
            assert conn.row_factory == sqlite3.Row
            connections.append(conn)

        # Verify that each connection is unique
        connection_ids = [id(conn) for conn in connections]
        assert len(set(connection_ids)) == 5

        # Close all connections
        for conn in connections:
            conn.close()

    def test_get_db_connection_data_integrity(self):
        # Create two separate connections
        conn1 = get_db_connection()
        conn2 = get_db_connection()

        # Insert data using the first connection
        cursor1 = conn1.cursor()
        cursor1.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, value TEXT)")
        cursor1.execute("INSERT INTO test_table (value) VALUES (?)", ("test_value",))
        conn1.commit()

        # Retrieve data using the second connection
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT value FROM test_table WHERE id = 1")
        result = cursor2.fetchone()

        # Assert that the data is consistent across connections
        assert result['value'] == "test_value"

        # Clean up
        cursor1.execute("DROP TABLE test_table")
        conn1.commit()
        conn1.close()
        conn2.close()

    def test_get_db_connection_performance(self):
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            # Test with a large number of connections
            num_connections = 1000
            start_time = time.time()
            for _ in range(num_connections):
                conn = get_db_connection()
                assert conn is not None
            end_time = time.time()

            # Check if the total time taken is reasonable (e.g., less than 1 second)
            total_time = end_time - start_time
            assert total_time < 1, f"Creating {num_connections} connections took {total_time:.2f} seconds, which is too long"

            # Verify that sqlite3.connect was called the correct number of times
            assert mock_connect.call_count == num_connections

            # Verify that row_factory was set for each connection (check its value instead of call_count)
            assert mock_conn.row_factory == sqlite3.Row
