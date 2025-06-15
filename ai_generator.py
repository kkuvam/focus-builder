import json
import requests
import streamlit as st

class AIGenerator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {st.secrets.get('HF_TOKEN', '')}"}

    def query_huggingface(self, prompt):
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 1024, "return_full_text": False}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"HuggingFace API error {response.status_code}: {response.text}")
        try:
            return response.json()[0]['generated_text']
        except Exception:
            raise Exception("Invalid response format from Hugging Face")

    def generate_tool_specification(self, user_description):
        prompt = (
            f"You are a productivity app planner. Convert the following user idea into a JSON object with keys: 'name', 'description', 'features', 'inputs', 'outputs', and 'visualizations'."
            f"\n\nUser Idea: {user_description}\n\nJSON:"
        )
        result = self.query_huggingface(prompt)
        try:
            json_part = result[result.find('{'):]  # Cut to start of JSON
            return json.loads(json_part)
        except Exception:
            raise Exception("Failed to parse tool specification JSON")

    def generate_streamlit_code(self, spec):
        prompt = (
            f"Write a working Streamlit Python script using only built-in modules and the following libraries: pandas, plotly, datetime."
            f" Build a dashboard/tool with the following specification:\n{json.dumps(spec, indent=2)}\n\nStart the code with 'import streamlit'."
        )
        result = self.query_huggingface(prompt)
        code = result[result.find("import streamlit"):]
        return code
