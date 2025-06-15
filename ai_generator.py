import requests
import json
import streamlit as st

class AIGenerator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        self.headers = {
            "Authorization": f"Bearer {st.secrets.get('HF_TOKEN', '')}",
            "Content-Type": "application/json"
        }

    def query_huggingface(self, prompt):
        payload = {
            "messages": [
                {"role": "system", "content": "You are a productivity app planner."},
                {"role": "user", "content": prompt}
            ],
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "do_sample": True
            }
        }

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"HuggingFace API error {response.status_code}: {response.text}")
        
        try:
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception("Invalid response format from Hugging Face: " + str(e))

    def generate_tool_specification(self, user_description):
        prompt = (
            f"Convert the following user idea into a JSON object with keys: 'name', 'description', "
            f"'features', 'inputs', 'outputs', and 'visualizations'.\n\nUser Idea: {user_description}\n\nJSON:"
        )
        result = self.query_huggingface(prompt)
        try:
            json_part = result[result.find('{'):]  # Get only the JSON part
            return json.loads(json_part)
        except Exception as e:
            raise Exception("Failed to parse tool specification JSON: " + str(e))

    def generate_streamlit_code(self, spec):
        prompt = (
            f"Write a complete Streamlit Python script using only built-in modules, pandas, plotly, and datetime. "
            f"Create a dashboard/tool based on this spec:\n\n{json.dumps(spec, indent=2)}\n\n"
            f"The script should start with 'import streamlit'."
        )
        result = self.query_huggingface(prompt)
        code_start = result.find("import streamlit")
        if code_start == -1:
            raise Exception("Failed to find valid code block in AI response")
        return result[code_start:]
