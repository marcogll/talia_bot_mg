# bot/modules/flow_engine.py
import json
import logging
import os
import sqlite3
from bot.db import get_db_connection
from bot.modules.sales_rag import generate_sales_pitch
from bot.modules.nfc_tag import generate_nfc_tag

logger = logging.getLogger(__name__)

class FlowEngine:
    def __init__(self):
        self.flows = self._load_flows()

    def _load_flows(self):
        """Loads all individual flow JSON files from the flows directory."""
        # flows_dir = 'bot/data/flows' # OLD
        base_dir = os.path.dirname(os.path.abspath(__file__))
        flows_dir = os.path.join(base_dir, '..', 'data', 'flows')
        
        loaded_flows = []
        try:
            if not os.path.exists(flows_dir):
                logger.error(f"Flows directory not found at '{flows_dir}'")
                return []

            for filename in os.listdir(flows_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(flows_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            flow_data = json.load(f)
                            if 'role' not in flow_data:
                                logger.warning(f"Flow {filename} is missing a 'role' key. Skipping.")
                                continue
                            loaded_flows.append(flow_data)
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding JSON from {filename}.")
                    except Exception as e:
                        logger.error(f"Error loading flow from {filename}: {e}")

            logger.info(f"Successfully loaded {len(loaded_flows)} flows.")
            return loaded_flows

        except Exception as e:
            logger.error(f"Failed to load flows from directory {flows_dir}: {e}")
            return []

    def get_flow(self, flow_id):
        """Retrieves a specific flow by its ID."""
        return next((flow for flow in self.flows if flow.get('id') == flow_id), None)

    def get_conversation_state(self, user_id):
        """Gets the current conversation state for a user from the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT flow_id, current_step_id, collected_data FROM conversations WHERE user_id = ?", (user_id,))
            state = cursor.fetchone()
            if state:
                return {
                    "flow_id": state['flow_id'],
                    "current_step_id": state['current_step_id'],
                    "collected_data": json.loads(state['collected_data']) if state['collected_data'] else {}
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"Database error in get_conversation_state: {e}")
            return None

    def start_flow(self, user_id, flow_id):
        """Starts a new flow for a user."""
        flow = self.get_flow(flow_id)
        if not flow or 'steps' not in flow or not isinstance(flow['steps'], list) or not flow['steps']:
            logger.error(f"Flow '{flow_id}' is invalid, has no steps, or steps is not a non-empty list.")
            return None

        initial_step = flow['steps'][0]
        self.update_conversation_state(user_id, flow_id, initial_step['step_id'], {})
        return initial_step

    def update_conversation_state(self, user_id, flow_id, step_id, collected_data):
        """Creates or updates the conversation state in the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO conversations (user_id, flow_id, current_step_id, collected_data)
                VALUES (?, ?, ?, ?)
            """, (user_id, flow_id, step_id, json.dumps(collected_data)))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error in update_conversation_state: {e}")

    def handle_response(self, user_id, response_data):
        """
        Handles a user's response, saves the data, and returns the next action.
        """
        state = self.get_conversation_state(user_id)
        if not state:
            return {"status": "error", "message": "No conversation state found."}

        flow = self.get_flow(state['flow_id'])
        if not flow:
            return {"status": "error", "message": f"Flow '{state['flow_id']}' not found."}

        current_step = next((step for step in flow['steps'] if step['step_id'] == state['current_step_id']), None)
        if not current_step:
            self.end_flow(user_id)
            return {"status": "error", "message": "Current step not found in flow."}

        # Save the user's response using the 'variable' key from the step definition
        variable_name = current_step.get('variable')

        if variable_name:
            state['collected_data'][variable_name] = response_data
        else:
            # Fallback for steps without a 'variable' key
            logger.warning(f"Step {current_step['step_id']} in flow {flow['id']} has no 'variable' defined. Saving with default key.")
            state['collected_data'][f"step_{current_step['step_id']}_response"] = response_data


        # Find the index of the current step to determine the next one robustly
        steps = flow['steps']
        current_step_index = -1
        for i, step in enumerate(steps):
            if step['step_id'] == state['current_step_id']:
                current_step_index = i
                break

        # Check if there is a next step in the list
        if current_step_index != -1 and current_step_index + 1 < len(steps):
            next_step = steps[current_step_index + 1]
            self.update_conversation_state(user_id, state['flow_id'], next_step['step_id'], state['collected_data'])
            return {"status": "in_progress", "step": next_step}
        else:
            # This is the last step, so the flow is complete
            final_data = state['collected_data']
            self.end_flow(user_id)

            response = {"status": "complete", "flow_id": flow['id'], "data": final_data}

            if flow['id'] == 'client_sales_funnel':
                user_query = final_data.get('IDEA_PITCH', '')
                sales_pitch = generate_sales_pitch(user_query, final_data)
                response['sales_pitch'] = sales_pitch
            elif flow['id'] == 'admin_create_nfc_tag':
                nfc_tag = generate_nfc_tag(final_data)
                response['nfc_tag'] = nfc_tag

            return response

    def end_flow(self, user_id):
        """Ends a flow for a user by deleting their conversation state."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error in end_flow: {e}")
