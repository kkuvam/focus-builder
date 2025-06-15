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
        prompt = f"""
        [INST] You are a productivity app designer.
        Turn the following user request into a detailed tool spec in JSON:
        "{user_description}"
        Return a JSON with: name, category, description, features (list),
        data_structure (fields), visualizations, interactions, and layout. [/INST]
        """
        return self.query_model(prompt, expect_json=True)

    def generate_streamlit_code(self, tool_spec):
        """Generate Streamlit code based on the tool specification"""
        prompt = f"""
        [INST] You are a skilled Python and Streamlit developer.
        Write full Streamlit code for this tool spec (no mock data, use session_state):
        {tool_spec}
        [/INST]
        """
        return self.query_model(prompt)

    def improve_tool(self, tool_code, improvement_request):
        """Improve the generated code using user feedback"""
        prompt = f"""
        [INST] Improve this Streamlit app code based on the user's request.

        REQUEST: {improvement_request}

        CODE: {tool_code}
        [/INST]
        """
        return self.query_model(prompt)

    def query_model(self, prompt, expect_json=False):
        """Calls Hugging Face inference endpoint"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "max_new_tokens": 800
            }
        }

        try:
            res = requests.post(self.api_url, headers=self.headers, json=payload)
            result = res.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                output = result[0]["generated_text"]
                if expect_json:
                    try:
                        # attempt to extract valid JSON
                        json_start = output.find("{")
                        json_end = output.rfind("}") + 1
                        return eval(output[json_start:json_end])  # safer alternative is json.loads
                    except Exception:
                        return {"error": "Could not parse JSON."}
                return output.strip()
            return f"❌ Error: {result}"
        except Exception as e:
            return f"❌ Request failed: {str(e)}"
