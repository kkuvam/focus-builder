import os
import json
import requests
import streamlit as st
import re

class AIGenerator:
    def __init__(self):
        # Force offline mode to avoid API quota issues
        self.use_offline = True
        self.api_key = None
        self.client = None
        self.model = None
        
        st.info("🔧 Running in offline mode - using built-in templates and patterns")
    
    def generate_tool_specification(self, user_description):
        """Generate a structured specification for the productivity tool"""
        
        if self.use_offline:
            return self._generate_offline_specification(user_description)
        
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
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Create a specification for this productivity tool: {user_description}"}
                    ],
                    response_format={"type": "json_object"}
                )
                
                return json.loads(response.choices[0].message.content)
            else:
                return self._generate_offline_specification(user_description)
            
        except Exception as e:
            st.error(f"Error generating tool specification: {str(e)}")
            return self._generate_offline_specification(user_description)
    
    def generate_streamlit_code(self, tool_spec):
        """Generate Streamlit code based on the tool specification"""
        
        if self.use_offline:
            return self._generate_offline_code(tool_spec)
        
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
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=3000
                )
                
                return response.choices[0].message.content
            else:
                return self._generate_offline_code(tool_spec)
            
        except Exception as e:
            st.error(f"Error generating Streamlit code: {str(e)}")
            return self._generate_offline_code(tool_spec)
    
    def improve_tool(self, tool_code, improvement_request):
        """Improve existing tool code based on user feedback"""
        
        if self.use_offline:
            st.info("Tool improvement not available in offline mode")
            return tool_code
        
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
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=3000
                )
                
                return response.choices[0].message.content
            else:
                st.info("Tool improvement not available in offline mode")
                return tool_code
            
        except Exception as e:
            st.error(f"Error improving tool: {str(e)}")
            return tool_code
    
    def _generate_offline_specification(self, user_description):
        """Generate a basic specification using keyword matching"""
        
        description_lower = user_description.lower()
        
        # Determine category based on keywords
        if any(word in description_lower for word in ['habit', 'daily', 'routine', 'track']):
            category = "tracker"
            name = "Daily Habit Tracker"
            features = ["habit logging", "progress tracking", "streak counting", "statistics"]
            fields = [
                {"name": "habit_name", "type": "string", "description": "Name of the habit"},
                {"name": "target", "type": "number", "description": "Daily target"},
                {"name": "date", "type": "date", "description": "Date of entry"},
                {"name": "completed", "type": "number", "description": "Amount completed"}
            ]
        elif any(word in description_lower for word in ['task', 'project', 'todo', 'manage']):
            category = "dashboard"
            name = "Task Management Dashboard"
            features = ["task creation", "status tracking", "project organization", "deadline management"]
            fields = [
                {"name": "task_title", "type": "string", "description": "Task title"},
                {"name": "status", "type": "string", "description": "Task status"},
                {"name": "priority", "type": "string", "description": "Task priority"},
                {"name": "due_date", "type": "date", "description": "Due date"}
            ]
        elif any(word in description_lower for word in ['budget', 'expense', 'money', 'finance']):
            category = "tracker"
            name = "Expense Tracker"
            features = ["expense logging", "category tracking", "budget monitoring", "spending analysis"]
            fields = [
                {"name": "description", "type": "string", "description": "Expense description"},
                {"name": "amount", "type": "number", "description": "Amount spent"},
                {"name": "category", "type": "string", "description": "Expense category"},
                {"name": "date", "type": "date", "description": "Date of expense"}
            ]
        elif any(word in description_lower for word in ['meal', 'food', 'plan', 'recipe']):
            category = "planner"
            name = "Meal Planner"
            features = ["meal scheduling", "recipe storage", "shopping lists", "nutrition tracking"]
            fields = [
                {"name": "meal_name", "type": "string", "description": "Name of the meal"},
                {"name": "meal_type", "type": "string", "description": "Breakfast, lunch, or dinner"},
                {"name": "date", "type": "date", "description": "Planned date"},
                {"name": "ingredients", "type": "string", "description": "Required ingredients"}
            ]
        else:
            category = "other"
            name = "Custom Productivity Tool"
            features = ["data entry", "list management", "basic tracking", "simple visualization"]
            fields = [
                {"name": "title", "type": "string", "description": "Item title"},
                {"name": "description", "type": "string", "description": "Item description"},
                {"name": "date", "type": "date", "description": "Date created"},
                {"name": "status", "type": "string", "description": "Current status"}
            ]
        
        return {
            "name": name,
            "category": category,
            "description": user_description,
            "features": features,
            "data_structure": {
                "fields": fields
            },
            "visualizations": [
                {"type": "chart", "description": "Progress over time"},
                {"type": "metric", "description": "Summary statistics"}
            ],
            "interactions": ["add", "edit", "delete", "filter", "view"],
            "layout": {
                "columns": 2,
                "sections": ["input_section", "data_display", "analytics"]
            }
        }
    
    def _generate_offline_code(self, tool_spec):
        """Generate basic Streamlit code based on tool specification"""
        
        category = tool_spec.get('category', 'other')
        name = tool_spec.get('name', 'Productivity Tool')
        fields = tool_spec.get('data_structure', {}).get('fields', [])
        
        # Generate field inputs based on specification
        input_code = []
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            
            if field_type == 'string':
                input_code.append(f'    {field_name} = st.text_input("{field["description"].title()}")')
            elif field_type == 'number':
                input_code.append(f'    {field_name} = st.number_input("{field["description"].title()}", min_value=0.0)')
            elif field_type == 'date':
                input_code.append(f'    {field_name} = st.date_input("{field["description"].title()}")')
            elif field_type == 'boolean':
                input_code.append(f'    {field_name} = st.checkbox("{field["description"].title()}")')
        
        input_section = '\n'.join(input_code)
        field_names = [f['name'] for f in fields]
        
        code_template = f'''def execute_tool():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, date
    
    st.subheader("📊 {name}")
    
    # Initialize session state
    if 'tool_data' not in st.session_state:
        st.session_state.tool_data = []
    
    # Input section
    with st.expander("➕ Add New Entry", expanded=True):
{input_section}
        
        if st.button("Add Entry") and {field_names[0] if field_names else 'True'}:
            entry = {{
{chr(10).join([f'                "{field}": {field},' for field in field_names])}
                "created_at": datetime.now()
            }}
            st.session_state.tool_data.append(entry)
            st.success("Entry added successfully!")
            st.rerun()
    
    # Display data
    if st.session_state.tool_data:
        st.subheader("📋 Your Data")
        
        # Convert to DataFrame for display
        df = pd.DataFrame(st.session_state.tool_data)
        st.dataframe(df, use_container_width=True)
        
        # Basic analytics
        if len(df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Entries", len(df))
            
            with col2:
                if 'date' in df.columns:
                    latest_date = df['date'].max() if 'date' in df.columns else None
                    if latest_date:
                        st.metric("Latest Entry", latest_date.strftime('%Y-%m-%d'))
        
        # Clear data option
        if st.button("🗑️ Clear All Data"):
            st.session_state.tool_data = []
            st.rerun()
    else:
        st.info("No data yet. Add your first entry above!")
'''
        
        return code_template
