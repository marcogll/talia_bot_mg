import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Ensure the 'bot' module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.modules.flow_engine import FlowEngine

class TestFlowEngine(unittest.TestCase):

    def setUp(self):
        """Set up a mock database connection and a mock flow definition."""
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

        self.mock_flow = {
            "id": "test_flow",
            "role": "client",
            "steps": [
                {"step_id": 1, "question": "What is your name?", "variable": "name"},
                {"step_id": 2, "question": "What is your quest?", "variable": "quest"},
                {"step_id": 3, "question": "What is your favorite color?", "variable": "color"}
            ]
        }

        # Patch the database connection and the file loading
        self.patcher_db = patch('bot.modules.flow_engine.get_db_connection', return_value=self.mock_conn)
        self.patcher_load = patch('bot.modules.flow_engine.FlowEngine._load_flows', return_value=[self.mock_flow])

        self.patcher_db.start()
        self.patcher_load.start()

        self.flow_engine = FlowEngine()

    def tearDown(self):
        """Stop the patchers."""
        self.patcher_db.stop()
        self.patcher_load.stop()

    def test_start_flow(self):
        """Test that a flow can be started correctly."""
        user_id = 123
        flow_id = "test_flow"

        initial_step = self.flow_engine.start_flow(user_id, flow_id)

        self.assertEqual(initial_step, self.mock_flow['steps'][0])
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_get_conversation_state_found(self):
        """Test retrieving an existing conversation state."""
        user_id = 123
        db_row = {'flow_id': 'test_flow', 'current_step_id': 1, 'collected_data': '{"name": "Sir Lancelot"}'}
        self.mock_cursor.fetchone.return_value = db_row

        state = self.flow_engine.get_conversation_state(user_id)

        self.assertEqual(state['flow_id'], 'test_flow')
        self.assertEqual(state['current_step_id'], 1)
        self.assertEqual(state['collected_data']['name'], 'Sir Lancelot')
        self.mock_cursor.execute.assert_called_with("SELECT flow_id, current_step_id, collected_data FROM conversations WHERE user_id = ?", (user_id,))

    def test_handle_response_in_progress(self):
        """Test handling a response that leads to the next step."""
        user_id = 123
        self.flow_engine.start_flow(user_id, "test_flow")

        # Mock the current state
        state = {"flow_id": "test_flow", "current_step_id": 1, "collected_data": {}}
        with patch.object(self.flow_engine, 'get_conversation_state', return_value=state):
            result = self.flow_engine.handle_response(user_id, "Sir Galahad")

            self.assertEqual(result['status'], 'in_progress')
            self.assertEqual(result['step'], self.mock_flow['steps'][1])
            self.assertEqual(state['collected_data']['name'], 'Sir Galahad')

    def test_handle_response_flow_completion(self):
        """Test handling the final response that completes a flow."""
        user_id = 123

        # Mock the state to be at the last step
        state = {"flow_id": "test_flow", "current_step_id": 3, "collected_data": {"name": "Sir Robin", "quest": "To seek the Holy Grail"}}
        with patch.object(self.flow_engine, 'get_conversation_state', return_value=state):
            result = self.flow_engine.handle_response(user_id, "Blue")

            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['data']['color'], 'Blue')

            # Check that the conversation is ended
            self.mock_cursor.execute.assert_any_call("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            self.mock_conn.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
