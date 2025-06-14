import re
import ast
import streamlit as st

def sanitize_input(user_input):
    """Sanitize user input to prevent injection attacks and clean up the text"""
    
    if not user_input:
        return ""
    
    # Remove or escape potentially dangerous characters
    # Remove HTML tags
    user_input = re.sub(r'<[^>]+>', '', user_input)
    
    # Remove script tags and javascript
    user_input = re.sub(r'<script.*?</script>', '', user_input, flags=re.IGNORECASE | re.DOTALL)
    user_input = re.sub(r'javascript:', '', user_input, flags=re.IGNORECASE)
    
    # Limit length to prevent extremely long inputs
    max_length = 2000
    if len(user_input) > max_length:
        user_input = user_input[:max_length] + "..."
        st.warning(f"⚠️ Input was truncated to {max_length} characters for safety.")
    
    # Clean up extra whitespace
    user_input = ' '.join(user_input.split())
    
    return user_input.strip()

def validate_generated_code(code):
    """Validate that the generated code is safe and properly structured"""
    
    if not code or not isinstance(code, str):
        return False
    
    try:
        # Check for basic syntax errors
        ast.parse(code)
        
        # Check if execute_tool function is defined
        if 'def execute_tool(' not in code:
            st.error("❌ Generated code must contain an 'execute_tool()' function")
            return False
        
        # Check for potentially dangerous imports or operations
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                st.error(f"❌ Generated code contains potentially unsafe operation: {pattern}")
                return False
        
        # Check if code is too long (potential resource abuse)
        if len(code) > 50000:  # 50KB limit
            st.error("❌ Generated code is too long")
            return False
        
        # Check for required Streamlit import
        if 'import streamlit' not in code and 'st.' in code:
            st.warning("⚠️ Generated code uses Streamlit but doesn't import it (this might be intentional)")
        
        return True
        
    except SyntaxError as e:
        st.error(f"❌ Syntax error in generated code: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Error validating generated code: {str(e)}")
        return False

def format_error_message(error):
    """Format error messages in a user-friendly way"""
    
    error_str = str(error)
    
    # Common error patterns and user-friendly messages
    error_patterns = {
        r'name .* is not defined': "A variable or function name is not recognized. This might be due to missing imports or typos.",
        r'invalid syntax': "There's a syntax error in the generated code. The AI might have made a mistake.",
        r'module .* not found': "A required Python library is missing. Make sure all dependencies are available.",
        r'list index out of range': "Trying to access data that doesn't exist. This might happen with empty datasets.",
        r'key.*not found': "Looking for data that doesn't exist. This often happens with missing session state variables."
    }
    
    for pattern, friendly_message in error_patterns.items():
        if re.search(pattern, error_str, re.IGNORECASE):
            return f"🔍 **Issue:** {friendly_message}\n\n**Technical details:** {error_str}"
    
    return f"❌ **Error:** {error_str}"

def get_tool_stats(generated_tools):
    """Generate statistics about the generated tools"""
    
    if not generated_tools:
        return {}
    
    stats = {
        'total_tools': len(generated_tools),
        'categories': {},
        'creation_dates': [],
        'most_recent': None,
        'oldest': None
    }
    
    for tool_id, tool_data in generated_tools.items():
        # Count by category if available
        category = tool_data.get('specification', {}).get('category', 'other')
        stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        # Track creation dates
        if 'created_at' in tool_data:
            stats['creation_dates'].append(tool_data['created_at'])
    
    # Find most recent and oldest
    if stats['creation_dates']:
        stats['creation_dates'].sort()
        stats['oldest'] = stats['creation_dates'][0]
        stats['most_recent'] = stats['creation_dates'][-1]
    
    return stats

def export_tool_data(tool_data):
    """Export tool data in a downloadable format"""
    
    try:
        import json
        return json.dumps(tool_data, indent=2, default=str)
    except Exception as e:
        st.error(f"Error exporting tool data: {str(e)}")
        return None

def import_tool_data(json_string):
    """Import tool data from JSON string"""
    
    try:
        import json
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error importing tool data: {str(e)}")
        return None

def clean_session_state():
    """Clean up old or unused session state variables"""
    
    # Remove old tool data that's no longer needed
    keys_to_remove = []
    for key in st.session_state:
        if key.startswith('tool_') and key.endswith('_data'):
            # Extract tool_id from the key
            tool_id = key.replace('tool_', '').replace('_data', '')
            if tool_id not in st.session_state.get('generated_tools', {}):
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]
    
    return len(keys_to_remove)
