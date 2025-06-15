import json
import requests
import streamlit as st
import re

class AIGenerator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        self.headers = {
            "Authorization": f"Bearer {st.secrets['HF_API_KEY']}",
            "Content-Type": "application/json"
        }

    def generate_tool_specification(self, user_description):
        prompt = (
            "<|system|>\nYou are an expert in creating productivity tools for Streamlit.\n"
            "Respond ONLY with valid JSON.\n"
            "<|user|>\n"
            f"Create a specification for this idea: {user_description}\n"
            "<|assistant|>"
        )
        payload = {"inputs": prompt}

        res = requests.post(self.api_url, headers=self.headers, json=payload)
        if res.status_code != 200:
            st.error(f"❌ API Error {res.status_code}: {res.text}")
            return None

        text = res.json()[0].get("generated_text", "")
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]

        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)
        json_str = re.sub(r"[“”‘’]", '"', json_str)

        try:
            return json.loads(json_str)
        except Exception as e:
            st.error(f"❌ JSON parse failed: {e}")
            return None
