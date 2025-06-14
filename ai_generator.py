import os
import json
from openai import OpenAI
import streamlit as st

class AIGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            st.stop()
        
        self.client = OpenAI(api_key=self.api_key)
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a specification for this productivity tool: {user_description}"}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Error generating tool specification: {str(e)}")
            return None
    
    def generate_streamlit_code(self, tool_spec):
        """Generate Streamlit code based on the tool specification"""
        
        system_prompt = """You are an expert Streamlit developer. Generate complete, functional Streamlit code based on the provided tool specification.

        IMPORTANT REQUIREMENTS:
        1. Use ONLY Streamlit's built-in components and styling
        2. Include proper session state management for data persistence
        3. Use pandas for data manipulation and plotly for visualizations
        4. Handle errors gracefully with try-catch blocks
        5. Provide clear user feedback for all actions
        6. Use st.columns() for layout organization
        7. Include data validation and input sanitization
        8. Add helpful tooltips and instructions for users
        9. Implement CRUD operations (Create, Read, Update, Delete) as needed
        10. Use datetime for date/time handling
        
        The code should be a complete function that can be executed within a Streamlit app.
        Start the function with 'def execute_tool():' and include all necessary imports at the top.
        
        Do NOT include any mock or sample data - use empty states with clear instructions for users to add their own data."""
        
        user_prompt = f"""Generate Streamlit code for this tool specification:
        
        {json.dumps(tool_spec, indent=2)}
        
        The code should be production-ready and handle all specified features and interactions."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error generating Streamlit code: {str(e)}")
            return None
    
    def improve_tool(self, tool_code, improvement_request):
        """Improve existing tool code based on user feedback"""
        
        system_prompt = """You are an expert Streamlit developer. Improve the provided Streamlit code based on the user's improvement request.
        
        Maintain the same code structure and ensure compatibility with the existing session state.
        Only modify what's necessary for the improvement.
        Keep all error handling and validation in place."""
        
        user_prompt = f"""Improve this Streamlit code:
        
        CURRENT CODE:
        {tool_code}
        
        IMPROVEMENT REQUEST:
        {improvement_request}
        
        Return the complete improved code."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error improving tool: {str(e)}")
            return None
