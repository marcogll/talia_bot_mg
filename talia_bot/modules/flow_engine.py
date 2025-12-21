# talia_bot/modules/flow_engine.py
import json
import logging
import os
from talia_bot.db import get_db_connection

logger = logging.getLogger(__name__)

class FlowEngine:
    def __init__(self):
        self.flows = self._load_flows()

    def _load_flows(self):
        """Loads all individual flow JSON files from the flows directory."""
        flows_dir = 'talia_bot/data/flows'
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
                            # Asignar un rol basado en el prefijo del nombre del archivo, si existe
                            if filename.startswith('admin_'):
                                flow_data['role'] = 'admin'
                            elif filename.startswith('crew_'):
                                flow_data['role'] = 'crew'
                            elif filename.startswith('client_'):
                                flow_data['role'] = 'client'
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
        for flow in self.flows:
            if flow['id'] == flow_id:
                return flow
        return None

    def get_conversation_state(self, user_id):
        """Gets the current conversation state for a user from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT flow_id, current_step_id, collected_data FROM conversations WHERE user_id = ?", (user_id,))
        state = cursor.fetchone()
        conn.close()
        if state:
            return {
                "flow_id": state['flow_id'],
                "current_step_id": state['current_step_id'],
                "collected_data": json.loads(state['collected_data']) if state['collected_data'] else {}
            }
        return None

    def start_flow(self, user_id, flow_id):
        """Starts a new flow for a user."""
        flow = self.get_flow(flow_id)
        if not flow:
            return None

        initial_step = flow['steps'][0]
        self.update_conversation_state(user_id, flow_id, initial_step['step_id'], {})
        return initial_step

    def update_conversation_state(self, user_id, flow_id, step_id, collected_data):
        """Creates or updates the conversation state in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO conversations (user_id, flow_id, current_step_id, collected_data)
            VALUES (?, ?, ?, ?)
        """, (user_id, flow_id, step_id, json.dumps(collected_data)))
        conn.commit()
        conn.close()

    def handle_response(self, user_id, response_data):
        """
        Handles a user's response, saves the data, and returns the next action.
        Returns a dictionary with the status and the next step or final data.
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

        # Save the user's response using the meaningful variable name
        if 'variable' in current_step:
            variable_name = current_step['variable']
            state['collected_data'][variable_name] = response_data
        else:
            logger.warning(f"Step {current_step['step_id']} in flow {flow['id']} has no 'variable' defined.")
            state['collected_data'][f"step_{current_step['step_id']}_response"] = response_data

        next_step_id = state['current_step_id'] + 1
        next_step = next((step for step in flow['steps'] if step['step_id'] == next_step_id), None)

        if next_step:
            # Check if the next step is a resolution step, which ends the data collection
            if next_step.get('input_type', '').startswith('resolution_'):
                logger.info(f"Flow {state['flow_id']} reached resolution for user {user_id}.")
                self.end_flow(user_id)
                return {
                    "status": "complete",
                    "resolution": next_step,
                    "data": state['collected_data']
                }
            else:
                # It's a regular step, so update state and return it
                self.update_conversation_state(user_id, state['flow_id'], next_step_id, state['collected_data'])
                return {"status": "in_progress", "step": next_step}
        else:
            # No more steps, the flow is complete
            logger.info(f"Flow {state['flow_id']} ended for user {user_id}. Data: {state['collected_data']}")
            self.end_flow(user_id)
            return {
                "status": "complete",
                "resolution": None,
                "data": state['collected_data']
            }

    def end_flow(self, user_id):
        """Ends a flow for a user by deleting their conversation state."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
