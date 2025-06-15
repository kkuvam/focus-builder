import json
import requests
import streamlit as st

class AIGenerator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        self.headers = {
            "Authorization": f"Bearer {st.secrets['HF_API_KEY']}",
            "Content-Type": "application/json"
        }

    def generate_tool_specification(self, user_description):
        """Generate a structured specification for the productivity tool"""

        system_prompt = """You are an expert in creating productivity tools and Streamlit applications.
        Analyze the user's natural language description and create a detailed specification for a Streamlit-based productivity tool.
        
        Respond with a JSON object containing:
        {
            "name": "Tool name",
            "category": "planner|dashboard|tracker|other",
            "description": "Detailed description",
            "features": ["list", "of", "key", "features"],
            "data_structure": {
                "fields": [
                    {"name": "field_name", "type": "string|number|date|boolean", "description": "field description"}
                ]
            },
            "visualizations": [
                {"type": "chart|table|metric|progress", "description": "what it shows"}
            ],
            "interactions": [
                "list of user interactions like add, edit, delete, filter, etc."
            ],
            "layout": {
                "columns": 1-3,
                "sections": ["section1", "section2"]
            }
        }"""

        try:
            payload = {
                "inputs": f"System: {system_prompt}\n\nUser: Create a specification for this productivity tool: {user_description}"
            }

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                st.error(f"❌ Request failed: {response.status_code} - {response.text}")
                return None

            generated_text = response.json()[0]["generated_text"]
            json_start = generated_text.find("{")
            json_end = generated_text.rfind("}") + 1
            json_str = generated_text[json_start:json_end]

            return json.loads(json_str)

        except Exception as e:
            st.error(f"❌ Error generating tool specification: {str(e)}")
            return None
