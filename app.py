import os
import requests
import streamlit as st
import json

class AIGenerator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
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
                "columns": 1,
                "sections": ["section1", "section2"]
            }
        }"""

        payload = {
            "inputs": f"System: {system_prompt}\n\nUser: Create a specification for this productivity tool: {user_description}"
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
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

    def generate_streamlit_code(self, tool_spec):
        """Generate Streamlit code based on the tool specification"""

        system_prompt = """You are an expert Streamlit developer. Generate complete, functional Streamlit code based on the provided tool specification.

        IMPORTANT REQUIREMENTS:
        - Use only Streamlit, pandas, and plotly
        - Implement data entry, CRUD, and visual layout from spec
        - Include helpful tooltips and basic error handling
        - Wrap the app inside `def execute_tool():`
        - Include all necessary imports
        - Do NOT use mock data — only create empty inputs and interfaces
        """

        user_prompt = f"Generate Streamlit code for this tool specification:\n\n{json.dumps(tool_spec, indent=2)}"

        payload = {
            "inputs": f"System: {system_prompt}\n\nUser: {user_prompt}"
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            if response.status_code != 200:
                st.error(f"❌ Request failed: {response.status_code} - {response.text}")
                return None

            return response.json()[0]["generated_text"]

        except Exception as e:
            st.error(f"❌ Error generating Streamlit code: {str(e)}")
            return None
