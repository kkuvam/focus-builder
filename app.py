import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from ai_generator import AIGenerator
from templates import get_template_library, get_template_code
from tool_executor import ToolExecutor
from utils import sanitize_input, validate_generated_code

    
# Initialize session state
if 'generated_tools' not in st.session_state:
    st.session_state.generated_tools = {}
if 'current_tool' not in st.session_state:
    st.session_state.current_tool = None
if 'ai_generator' not in st.session_state:
    st.session_state.ai_generator = AIGenerator()
if 'tool_executor' not in st.session_state:
    st.session_state.tool_executor = ToolExecutor()

def main():
    st.set_page_config(
        page_title="AI Productivity Tool Generator",
        page_icon="🛠️",
        layout="wide"
    )
    
    st.title("🛠️ AI Productivity Tool Generator")
    st.markdown("Transform your natural language ideas into functional productivity tools!")
    
    # Sidebar for navigation and templates
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Generate New Tool", "My Generated Tools", "Template Library"]
        )
        
        if page == "Template Library":
            st.header("📚 Template Library")
            templates = get_template_library()
            selected_template = st.selectbox(
                "Choose a template:",
                list(templates.keys())
            )
            if st.button("Use Template"):
                st.session_state.template_input = templates[selected_template]["description"]
                st.rerun()
    
    if page == "Generate New Tool":
        generate_tool_page()
    elif page == "My Generated Tools":
        my_tools_page()
    elif page == "Template Library":
        template_library_page()

def generate_tool_page():
    st.header("🎯 Generate New Tool")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pre-fill with template if selected
        default_text = ""
        if hasattr(st.session_state, 'template_input'):
            default_text = st.session_state.template_input
            delattr(st.session_state, 'template_input')
        
        user_input = st.text_area(
            "Describe the productivity tool you want to create:",
            value=default_text,
            height=150,
            placeholder="Example: Create a daily habit tracker that shows my progress with charts and allows me to mark habits as complete each day..."
        )
        
        tool_name = st.text_input(
            "Tool Name (optional):",
            placeholder="My Awesome Tool"
        )
        
        generate_btn = st.button("🚀 Generate Tool", type="primary")
    
    with col2:
        st.info("""
        **Tips for better results:**
        - Be specific about functionality
        - Mention data you want to track
        - Describe desired visualizations
        - Include user interactions needed
        """)
    
    # Generation process
    if generate_btn and user_input.strip():
        with st.spinner("🤖 AI is analyzing your request..."):
            try:
                # Sanitize input
                clean_input = sanitize_input(user_input)
                
                # Generate tool specification
                tool_spec = st.session_state.ai_generator.generate_tool_specification(clean_input)
                
                if tool_spec:
                    st.success("✅ Tool specification generated!")
                    
                    # Display specification
                    with st.expander("View Tool Specification", expanded=True):
                        st.json(tool_spec)
                    
                    # Generate Streamlit code
                    with st.spinner("🔧 Generating Streamlit code..."):
                        tool_code = st.session_state.ai_generator.generate_streamlit_code(tool_spec)
                        
                        if tool_code and validate_generated_code(tool_code):
                            st.success("✅ Code generated successfully!")
                            
                            # Save generated tool
                            tool_id = f"tool_{len(st.session_state.generated_tools) + 1}"
                            final_name = tool_name.strip() if tool_name.strip() else tool_spec.get('name', 'Unnamed Tool')
                            
                            st.session_state.generated_tools[tool_id] = {
                                'name': final_name,
                                'description': clean_input,
                                'specification': tool_spec,
                                'code': tool_code,
                                'created_at': datetime.now().isoformat(),
                                'data': {}
                            }
                            
                            st.session_state.current_tool = tool_id

                            # Save preview copy for download and display
                            st.session_state["generated_code"] = tool_code

                            # Code preview section
                            st.subheader("🧾 Preview of Generated Code")
                            st.code(tool_code, language='python')

                            # Optional: Provide downloadable version
                            st.download_button(
                                label="📥 Download Generated Tool",
                                data=tool_code,
                                file_name=f"{final_name.replace(' ', '_')}.py",
                                mime="text/plain"
                            )

                            
                            # Preview section
                            st.header("🔍 Tool Preview")
                            preview_tool(tool_id)
                            
                        else:
                            st.error("❌ Failed to generate valid code. Please try again with a different description.")
                else:
                    st.error("❌ Failed to generate tool specification. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
    
    elif generate_btn:
        st.warning("⚠️ Please enter a description of the tool you want to create.")

def preview_tool(tool_id):
    """Preview the generated tool"""
    if tool_id not in st.session_state.generated_tools:
        st.error("Tool not found!")
        return
    
    tool = st.session_state.generated_tools[tool_id]
    
    try:
        # Execute the generated tool code
        st.session_state.tool_executor.execute_tool(tool_id, tool['code'])
        
    except Exception as e:
        st.error(f"❌ Error executing tool: {str(e)}")
        
        # Show code for debugging
        with st.expander("View Generated Code (for debugging)"):
            st.code(tool['code'], language='python')

def my_tools_page():
    st.header("🗂️ My Generated Tools")
    
    if not st.session_state.generated_tools:
        st.info("📝 No tools generated yet. Go to 'Generate New Tool' to create your first productivity tool!")
        return
    
    # Tool selection
    tool_names = {tool_id: tool_data['name'] for tool_id, tool_data in st.session_state.generated_tools.items()}
    selected_tool_id = st.selectbox(
        "Select a tool to view:",
        list(tool_names.keys()),
        format_func=lambda x: tool_names[x]
    )
    
    if selected_tool_id:
        tool = st.session_state.generated_tools[selected_tool_id]
        
        # Tool info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(tool['name'])
            st.write(f"**Description:** {tool['description']}")
        with col2:
            st.write(f"**Created:** {datetime.fromisoformat(tool['created_at']).strftime('%Y-%m-%d %H:%M')}")
        with col3:
            if st.button("🗑️ Delete Tool"):
                del st.session_state.generated_tools[selected_tool_id]
                st.rerun()
        
        st.divider()
        
        # Run the tool
        st.header(f"🚀 {tool['name']}")
        preview_tool(selected_tool_id)

def template_library_page():
    st.header("📚 Template Library")
    
    templates = get_template_library()
    
    for template_name, template_data in templates.items():
        with st.expander(f"📋 {template_name}", expanded=False):
            st.write(f"**Description:** {template_data['description']}")
            st.write(f"**Category:** {template_data['category']}")
            st.write(f"**Features:** {', '.join(template_data['features'])}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Use Template: {template_name}", key=f"use_{template_name}"):
                    st.session_state.template_input = template_data['description']
                    st.switch_page("Generate New Tool")
            
            with col2:
                if st.button(f"View Code: {template_name}", key=f"view_{template_name}"):
                    code = get_template_code(template_name)
                    st.code(code, language='python')

if __name__ == "__main__":
    main()
