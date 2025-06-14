import streamlit as st
import sys
import traceback
from io import StringIO
import contextlib

class ToolExecutor:
    def __init__(self):
        pass
    
    def execute_tool(self, tool_id, tool_code):
        """Safely execute the generated tool code within the current Streamlit context"""
        
        if tool_id not in st.session_state.generated_tools:
            st.error("Tool not found!")
            return
        
        # Create a unique namespace for this tool
        tool_namespace = f"tool_{tool_id}_data"
        
        # Initialize tool-specific session state if needed
        if tool_namespace not in st.session_state:
            st.session_state[tool_namespace] = {}
        
        try:
            # Capture any print statements or stdout
            stdout_capture = StringIO()
            
            # Prepare the execution environment
            exec_globals = {
                'st': st,
                'pd': None,  # Will be imported in the code if needed
                'px': None,  # Will be imported in the code if needed
                'go': None,  # Will be imported in the code if needed
                'datetime': None,  # Will be imported in the code if needed
                'timedelta': None,  # Will be imported in the code if needed
                'date': None,  # Will be imported in the code if needed
                'json': None,  # Will be imported in the code if needed
                '__builtins__': __builtins__,
                'tool_data': st.session_state[tool_namespace]  # Tool-specific data storage
            }
            
            # Execute the tool code
            with contextlib.redirect_stdout(stdout_capture):
                exec(tool_code, exec_globals)
                
                # Call the execute_tool function if it exists
                if 'execute_tool' in exec_globals:
                    exec_globals['execute_tool']()
                else:
                    st.error("Generated code must contain an 'execute_tool()' function.")
                    return
            
            # Store any updated tool data back to session state
            st.session_state[tool_namespace] = exec_globals.get('tool_data', {})
            
            # Display any captured output
            captured_output = stdout_capture.getvalue()
            if captured_output.strip():
                with st.expander("Debug Output"):
                    st.text(captured_output)
                    
        except Exception as e:
            st.error(f"❌ Error executing tool: {str(e)}")
            
            # Show detailed error information
            with st.expander("🔍 Error Details", expanded=True):
                st.code(traceback.format_exc(), language='python')
                
                # Show the problematic code section
                st.subheader("Generated Code:")
                st.code(tool_code, language='python', line_numbers=True)
                
                # Provide suggestions
                st.subheader("💡 Troubleshooting Tips:")
                st.write("""
                - The generated code might have syntax errors
                - Required imports might be missing
                - Check if all Streamlit components are used correctly
                - Verify that session state variables are properly initialized
                """)
    
    def validate_tool_code(self, tool_code):
        """Validate the generated tool code for basic syntax and structure"""
        
        try:
            # Check for basic syntax errors
            compile(tool_code, '<string>', 'exec')
            
            # Check if execute_tool function exists
            if 'def execute_tool(' not in tool_code:
                return False, "Code must contain an 'execute_tool()' function"
            
            # Check for potentially dangerous operations (basic security)
            dangerous_keywords = ['import os', 'import sys', 'import subprocess', 'exec(', 'eval(']
            for keyword in dangerous_keywords:
                if keyword in tool_code:
                    return False, f"Code contains potentially dangerous operation: {keyword}"
            
            return True, "Code validation passed"
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_tool_data(self, tool_id):
        """Get the stored data for a specific tool"""
        tool_namespace = f"tool_{tool_id}_data"
        return st.session_state.get(tool_namespace, {})
    
    def set_tool_data(self, tool_id, data):
        """Set the stored data for a specific tool"""
        tool_namespace = f"tool_{tool_id}_data"
        st.session_state[tool_namespace] = data
    
    def clear_tool_data(self, tool_id):
        """Clear the stored data for a specific tool"""
        tool_namespace = f"tool_{tool_id}_data"
        if tool_namespace in st.session_state:
            del st.session_state[tool_namespace]
