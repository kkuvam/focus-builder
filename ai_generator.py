import os
import re
import json
import requests
import streamlit as st

class AIGenerator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {
            "Authorization": f"Bearer {st.secrets['HF_API_KEY']}",
            "Content-Type": "application/json"
        }

    def generate_tool_specification(self, user_description):
        """Generate a structured specification for the productivity tool."""

        system_prompt = """You are an expert in creating productivity tools and Streamlit applications.
Only respond with valid JSON. Do NOT include explanations or extra text.
Create a specification in this format:
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
  "interactions": ["add", "edit", "delete", "filter"],
  "layout": {
    "columns": 1,
    "sections": ["Inputs", "Output"]
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

            # Extract JSON-looking section
            json_start = generated_text.find("{")
            json_end = generated_text.rfind("}") + 1
            json_str = generated_text[json_start:json_end]

            # Clean malformed JSON
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r",\s*]", "]", json_str)
            json_str = re.sub(r"[\u2018\u2019\u201c\u201d]", '"', json_str)

            return json.loads(json_str)

        except Exception as e:
            st.error(f"❌ Error generating tool specification: {str(e)}")
            return None
