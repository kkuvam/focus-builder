import streamlit as st
import requests
import json

class AIGenerator:
    def __init__(self):
        self.api_url = "https://router.huggingface.co/hf-inference/models/HuggingFaceH4/zephyr-7b-beta/v1/chat/completions"
        token = st.secrets.get('HF_TOKEN', '')
        if not token:
            raise ValueError("Hugging Face token missing in Streamlit secrets as 'HF_TOKEN'")
        self.headers = {"Authorization": f"Bearer {token}"}

    def query_huggingface(self, prompt):
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "parameters": {"max_new_tokens": 1024}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
        if response.status_code != 200:
            raise Exception(f"HuggingFace API error {response.status_code}: {response.text}")

        try:
            # Adjust this according to the exact API response format
            return response.json()['choices'][0]['message']['content']
        except (KeyError, IndexError, json.JSONDecodeError):
            raise Exception("Invalid response format from Hugging Face")

    def generate_tool_specification(self, user_description):
        prompt = (
            "You are a productivity app planner. Convert the following user idea into a JSON object "
            "with keys: 'name', 'description', 'features', 'inputs', 'outputs', and 'visualizations'."
            f"\n\nUser Idea: {user_description}\n\nJSON:"
        )
        result = self.query_huggingface(prompt)
        json_part = result[result.find('{'):]  # Could be improved with regex if needed
        try:
            return json.loads(json_part)
        except Exception as e:
            raise Exception("Failed to parse JSON: " + str(e))

    def generate_streamlit_code(self, spec):
        prompt = (
            "Write a working Streamlit Python script using only built-in modules and the following libraries: "
            "pandas, plotly, datetime. Build a dashboard/tool with the following specification:\n"
            f"{json.dumps(spec, indent=2)}\n\nStart the code with 'import streamlit'. Only return code."
        )
        result = self.query_huggingface(prompt)
        code = result[result.find("import streamlit"):]
        return code
