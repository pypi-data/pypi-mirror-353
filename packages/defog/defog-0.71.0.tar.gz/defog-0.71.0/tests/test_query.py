import json
import os
import shutil
import unittest
from unittest import mock

from defog.query import (
    is_connection_error,
    execute_query_once,
    execute_query,
    async_execute_query_once,
    async_execute_query,
)


class ExecuteQueryOnceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # if connection.json exists, copy it to /tmp since we'll be overwriting it
        home_dir = os.path.expanduser("~")
        self.logs_path = os.path.join(home_dir, ".defog", "logs")
        self.tmp_dir = os.path.join("/tmp")
        self.moved = False
        if os.path.exists(self.logs_path):
            print("Moving logs to /tmp")
            if os.path.exists(os.path.join(self.tmp_dir, "logs")):
                os.remove(os.path.join(self.tmp_dir, "logs"))
            shutil.move(self.logs_path, self.tmp_dir)
            self.moved = True

    @classmethod
    def tearDownClass(self):
        # copy back the original after all tests have completed
        if self.moved:
            print("Moving logs back to ~/.defog")
            shutil.move(os.path.join(self.tmp_dir, "logs"), self.logs_path)

    @mock.patch("requests.post")
    @mock.patch("defog.query.execute_query_once")
    def test_execute_query_success(self, mock_execute_query_once, mock_requests_post):
        # Mock the execute_query_once function
        db_type = "postgres"
        db_creds = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
        query1 = "SELECT * FROM table_name;"
        query2 = "SELECT * FROM new_table_name;"
        api_key = "your_api_key"
        question = "your_question"
        hard_filters = "your_hard_filters"
        retries = 3

        # Set up the mock responses
        mock_execute_query_once.return_value = (
            ["col1", "col2"],
            [("data1", "data2"), ("data3", "data4")],
        )
        mock_response = mock.Mock()
        mock_response.json.return_value = {"new_query": query2}
        mock_requests_post.return_value = mock_response

        # Call the function being tested
        colnames, results, rcv_query = execute_query(
            query1, api_key, db_type, db_creds, question, hard_filters, retries
        )

        # Assert the expected behavior
        mock_execute_query_once.assert_called_once_with(db_type, db_creds, query1)
        mock_requests_post.assert_not_called()
        self.assertEqual(colnames, ["col1", "col2"])
        self.assertEqual(results, [("data1", "data2"), ("data3", "data4")])
        self.assertEqual(rcv_query, query1)  # should return the original query

    @mock.patch("requests.post")
    @mock.patch("defog.query.execute_query_once")
    def test_execute_query_success_with_retry(
        self, mock_execute_query_once, mock_requests_post
    ):
        db_type = "postgres"
        db_creds = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
        query1 = "SELECT * FROM table_name;"
        query2 = "SELECT * FROM table_name WHERE colour='blue';"
        api_key = "your_api_key"
        question = "your_question"
        hard_filters = "your_hard_filters"
        retries = 3
        dev = False
        temp = False
        colnames = (["col1", "col2"],)
        results = [("data1", "data2"), ("data3", "data4")]

        # Mock the execute_query_once function to raise an exception the first
        # time it is called and return the results the second time it is called
        err_msg = "Test exception"

        def side_effect(db_type, db_creds, query):
            if query == query1:
                raise Exception(err_msg)
            else:
                return colnames, results

        mock_execute_query_once.side_effect = side_effect
        # mock the response to return {"new_query": query2} when .json() is called
        mock_response = mock.Mock()
        mock_response.json.return_value = {"new_query": query2}
        mock_requests_post.return_value = mock_response

        # remove logs if it exists
        if os.path.exists(os.path.join(self.logs_path)):
            os.remove(os.path.join(self.logs_path))

        # Call the function being tested
        ret = execute_query(
            query=query1,
            api_key=api_key,
            db_type=db_type,
            db_creds=db_creds,
            question=question,
            hard_filters=hard_filters,
            retries=retries,
        )
        # should return new query2 instead of query1
        self.assertEqual(ret, (colnames, results, query2))

        # Assert the mock function calls
        mock_execute_query_once.assert_called_with(db_type, db_creds, query2)
        json_req = {
            "api_key": api_key,
            "previous_query": query1,
            "error": err_msg,
            "db_type": db_type,
            "hard_filters": hard_filters,
            "question": question,
            "dev": dev,
            "temp": temp,
        }
        mock_requests_post.assert_called_with(
            "https://api.defog.ai/retry_query_after_error",
            json=json_req,
            verify=False,
        )

        # check that err logs are populated
        with open(self.logs_path, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 5)
            self.assertIn(err_msg, lines[0])
            self.assertIn(f"Retries left: {retries}", lines[1])
            self.assertIn(json.dumps(json_req), lines[2])


class ExecuteAsyncQueryOnceTestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(self):
        # if connection.json exists, copy it to /tmp since we'll be overwriting it
        home_dir = os.path.expanduser("~")
        self.logs_path = os.path.join(home_dir, ".defog", "logs")
        self.tmp_dir = os.path.join("/tmp")
        self.moved = False
        if os.path.exists(self.logs_path):
            print("Moving logs to /tmp")
            if os.path.exists(os.path.join(self.tmp_dir, "logs")):
                os.remove(os.path.join(self.tmp_dir, "logs"))
            shutil.move(self.logs_path, self.tmp_dir)
            self.moved = True

    @classmethod
    def tearDownClass(self):
        # copy back the original after all tests have completed
        if self.moved:
            print("Moving logs back to ~/.defog")
            shutil.move(os.path.join(self.tmp_dir, "logs"), self.logs_path)

    @mock.patch("asyncpg.connect")
    async def test_async_execute_query_once_success(self, mock_connect):
        # Mock the asyncpg.connect function
        mock_cursor = mock_connect.return_value.fetch
        mock_cursor.return_value = [
            {"col1": "data1", "col2": "data2"},
            {"col1": "data3", "col2": "data4"},
        ]

        db_type = "postgres"
        db_creds = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
        query = "SELECT * FROM table_name;"

        colnames, results = await async_execute_query_once(db_type, db_creds, query)

        # Add your assertions here to validate the results
        self.assertEqual(colnames, ["col1", "col2"])
        self.assertEqual(results, [["data1", "data2"], ["data3", "data4"]])
        print("Postgres async query execution test passed!")

    @mock.patch("aiohttp.ClientSession.post")
    @mock.patch("defog.query.async_execute_query_once")
    async def test_async_execute_query_success(
        self, mock_execute_query_once, mock_aiohttp_post
    ):
        # Mock the execute_query_once function
        db_type = "postgres"
        db_creds = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
        query1 = "SELECT * FROM table_name;"
        query2 = "SELECT * FROM new_table_name;"
        api_key = "your_api_key"
        question = "your_question"
        hard_filters = "your_hard_filters"
        retries = 3

        # Set up the mock responses
        mock_execute_query_once.return_value = (
            ["col1", "col2"],
            [["data1", "data2"], ["data3", "data4"]],
        )

        # Mock the async aiohttp response
        mock_response = mock.Mock()
        mock_response.json = mock.AsyncMock(return_value={"new_query": query2})
        mock_aiohttp_post.return_value.__aenter__.return_value = mock_response

        # Call the function being tested
        colnames, results, rcv_query = await async_execute_query(
            query1, api_key, db_type, db_creds, question, hard_filters, retries
        )

        # Assert the expected behavior
        mock_execute_query_once.assert_called_once_with(
            db_type="postgres",  # Use keyword arguments for db_type
            db_creds={
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "user": "test_user",
                "password": "test_password",
            },  # Use keyword arguments for db_creds
            query="SELECT * FROM table_name;",  # Use keyword arguments for query
        )

        # Since there should be no retry, aiohttp post should not be called
        mock_aiohttp_post.assert_not_called()

        self.assertEqual(colnames, ["col1", "col2"])
        self.assertEqual(results, [["data1", "data2"], ["data3", "data4"]])
        self.assertEqual(rcv_query, query1)  # should return the original query

    @mock.patch("aiohttp.ClientSession.post")
    @mock.patch("defog.query.async_execute_query_once")
    async def test_execute_query_success_with_retry(
        self, mock_execute_query_once, mock_aiohttp_post
    ):
        db_type = "postgres"
        db_creds = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
        query1 = "SELECT * FROM table_name;"
        query2 = "SELECT * FROM table_name WHERE colour='blue';"
        api_key = "your_api_key"
        question = "your_question"
        hard_filters = "your_hard_filters"
        retries = 3
        dev = False
        temp = False
        colnames = (["col1", "col2"],)
        results = [("data1", "data2"), ("data3", "data4")]

        # Mock the execute_query_once function to raise an exception the first
        # time it is called and return the results the second time it is called
        err_msg = "Test exception"

        def side_effect(db_type, db_creds, query):
            if query == query1:
                raise Exception(err_msg)
            else:
                return colnames, results

        mock_execute_query_once.side_effect = side_effect

        # Mock the async aiohttp response for the retry query
        mock_response = mock.Mock()
        mock_response.json = mock.AsyncMock(return_value={"new_query": query2})
        mock_aiohttp_post.return_value.__aenter__.return_value = mock_response

        # remove logs if they exist
        if os.path.exists(os.path.join(self.logs_path)):
            os.remove(os.path.join(self.logs_path))

        # Call the function being tested
        ret = await async_execute_query(
            query=query1,
            api_key=api_key,
            db_type=db_type,
            db_creds=db_creds,
            question=question,
            hard_filters=hard_filters,
            retries=retries,
        )

        # should return new query2 instead of query1
        self.assertEqual(ret, (colnames, results, query2))

        # Assert the mock function calls
        mock_execute_query_once.assert_called_with(db_type, db_creds, query2)

        json_req = {
            "api_key": api_key,
            "previous_query": query1,
            "error": err_msg,
            "db_type": db_type,
            "hard_filters": hard_filters,
            "question": question,
            "dev": dev,
            "temp": temp,
        }

        # Assert aiohttp post was called with the correct arguments
        mock_aiohttp_post.assert_called_with(
            "https://api.defog.ai/retry_query_after_error", json=json_req, timeout=300
        )

        # check that error logs are populated
        with open(self.logs_path, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 5)
            self.assertIn(err_msg, lines[0])
            self.assertIn(f"Retries left: {retries}", lines[1])
            self.assertIn(json.dumps(json_req), lines[2])


class TestConnectionError(unittest.TestCase):
    def test_connection_failed(self):
        self.assertTrue(
            is_connection_error(
                """connection to server on socket "/tmp/.s.PGSQL.5432" failed: No such file or directory
    Is the server running locally and accepting connections on that socket?"""
            )
        )

    def test_not_connection_failed(self):
        self.assertFalse(
            is_connection_error(
                'psycopg2.errors.UndefinedTable: relation "nonexistent_table" does not exist'
            )
        )
        self.assertFalse(
            is_connection_error(
                'psycopg2.errors.SyntaxError: syntax error at or near "nonexistent_table"'
            )
        )
        self.assertFalse(
            is_connection_error(
                'psycopg2.errors.UndefinedColumn: column "nonexistent_column" does not exist'
            )
        )

    def test_empty_string(self):
        self.assertFalse(is_connection_error(""))
        self.assertFalse(is_connection_error(None))


if __name__ == "__main__":
    unittest.main()
