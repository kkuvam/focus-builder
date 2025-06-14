# 🧠 Focus Builder

**Focus Builder** is an AI-powered productivity assistant that transforms rough ideas into functional planners, dashboards, and trackers — instantly.  
Built for creators, students, and professionals who want to organize fast and think less.

> [Launch the App](https://focus-builder.streamlit.app)  
> [View the Code](https://github.com/kkuvam/focus-builder)

---

## Features

- **Idea to Tool Generator**  
  Convert natural language ideas into structured productivity tools like to-do lists, planners, goal trackers, etc.

- **Powered by GPT**  
  Uses OpenAI’s GPT model to understand context and generate relevant, smart tools.

- **Instant Output**  
  Generate working formats in seconds — ready to use or export.

- **Minimal Interface**  
  Fast, clean UI using Streamlit — no learning curve.


---

## Tech Stack

- **Frontend**: Streamlit  
- **AI Engine**: OpenAI GPT via `st.secrets`  
- **Language**: Python  
- **Hosting**: Streamlit Community Cloud

---

## How to Use

1. Visit the live app: [https://kkuvam-focus-builder.streamlit.app](https://kkuvam-focus-builder.streamlit.app)  
2. Input a rough idea like:  
   _"I want a weekly fitness tracker for 3 goals"_  
3. Instantly get a structured tool with headings, checkboxes, or tables  
4. Copy or refine — more formats coming soon

---

## Environment Variables

To run locally, create a `.streamlit/secrets.toml` file:

```toml
OPENAI_API_KEY = "your-api-key"
