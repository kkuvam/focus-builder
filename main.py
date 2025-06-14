import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Focus Builder", page_icon="🧠")

st.title("🧠 Focus Builder")
st.caption("Create productivity tool ideas using AI.")

user_input = st.text_input("What do you want the tool to do?")

if user_input:
    with st.spinner("Thinking..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a productivity app designer."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=600
        )
        result = response.choices[0].message.content
        st.success("Here's your AI-generated tool:")
        st.markdown(result)
