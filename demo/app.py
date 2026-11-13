"""
AI Gateway Demo
The simplest possible agent: a chat that can search a small database of synthetic records.
Every request goes through the AI gateway. The app adds no security logic of its own:
whatever the gateway allows or refuses is shown exactly as the gateway sends it.

Run it from the main project folder:  python3 -m streamlit run demo/app.py
"""

import json
import os

import streamlit as st
from openai import APIStatusError, OpenAI

from database import TOOLS, lookup_records, run_tool
from prompts import DEMO_PROMPTS, SYSTEM_PROMPT


# =============================================================================
# OPTIONAL: SAVE YOUR GATEWAY DETAILS HERE
# -----------------------------------------------------------------------------
# You can paste the API key and gateway URL into the app's sidebar instead.
# Fill them in here only if you want them loaded every time the app starts.
#
# Where to find them: in your gateway's console, create an API key for this app.
# The console shows the key and the gateway URL. Copy them exactly as shown.
#
#   API key       looks like:  sk-AbCdEf1234567890XyZ
#   Gateway URL   looks like:  https://your-gateway.example.com/v1
#
# Do NOT upload this file to GitHub, or share it, after you paste a real key.
# =============================================================================

API_KEY = "PASTE-YOUR-API-KEY-HERE"
BASE_URL = "PASTE-YOUR-GATEWAY-URL-HERE"

# Models that appear in the Model dropdown.
# REPLACE these with the model names your gateway gives you, spelled exactly as they
# appear in your gateway's console or documentation.
# Put the model your agent IS allowed to use first. The "Restricted model" prompt uses the second.
MODELS = ["haiku-5-5", "sonnet-5-5"]

# How long to wait for an answer before giving up, in seconds.
REQUEST_TIMEOUT_SECONDS = 30

# The assistant searches the synthetic database with tool calls. If your gateway doesn't
# support tool calling, set this to False: the app then looks up matching records itself
# and sends them along with the question.
AGENT_USE_TOOLS = True

# =============================================================================
# End of settings. You should not need to change anything below this line.
# =============================================================================

# Environment variables, if set, fill these in too. The sidebar can override both.
API_KEY = os.getenv("GATEWAY_API_KEY", API_KEY)
BASE_URL = os.getenv("GATEWAY_BASE_URL", BASE_URL)
SAVED_KEY = "" if API_KEY.startswith("PASTE") else API_KEY
SAVED_URL = "" if BASE_URL.startswith("PASTE") else BASE_URL
MAX_TOOL_ROUNDS = 5


# -----------------------------------------------------------------------------
# Page setup and styling
# -----------------------------------------------------------------------------

st.set_page_config(page_title="AI Gateway Demo", layout="centered")

st.markdown(
    """
    <style>
      #MainMenu, footer, [data-testid="stDecoration"] {visibility: hidden;}
      html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      }
      .block-container {padding-top: 2.5rem; max-width: 820px;}
      h1 {font-weight: 600; font-size: 1.7rem; letter-spacing: -0.01em;}
      .subtle {color: #6B6A66; font-size: 0.88rem;}
      .meta {color: #8A8984; font-size: 0.78rem; margin-top: 0.35rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Talking to the gateway
# -----------------------------------------------------------------------------

def ask(model, history):
    """
    Send the conversation through the gateway, running any database searches the model asks for.
    Returns the answer, or the gateway's response exactly as it came back if the request failed.
    """
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=0)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    steps = []

    if not AGENT_USE_TOOLS:
        question = messages[-1]["content"]
        rows = lookup_records(question)
        messages[-1] = {"role": "user", "content": f"{question}\n\nDatabase records:\n{json.dumps(rows, indent=1)}"}
        steps.append(f"Looked up {len(rows)} records")

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            request = {"model": model, "messages": messages, "max_tokens": 1024}
            if AGENT_USE_TOOLS:
                request["tools"] = TOOLS
            message = client.chat.completions.create(**request).choices[0].message
            if not message.tool_calls:
                return {"ok": True, "text": message.content or "", "steps": steps}
            messages.append({"role": "assistant", "content": message.content or "", "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in message.tool_calls]})
            for tc in message.tool_calls:
                steps.append(f"{tc.function.name}({tc.function.arguments})")
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": run_tool(tc.function.name, tc.function.arguments)})
        return {"ok": False, "text": f"Stopped after {MAX_TOOL_ROUNDS} rounds of tool calls.", "steps": steps}
    except APIStatusError as e:
        # The gateway's own response, unchanged.
        return {"ok": False, "text": f"HTTP {e.status_code}\n\n{e.response.text}", "steps": steps}
    except Exception as e:
        return {"ok": False, "text": f"{type(e).__name__}: {e}", "steps": steps}


def show(reply):
    if reply["ok"]:
        st.markdown(reply["text"])
    else:
        st.code(reply["text"], language=None, wrap_lines=True)
    if reply["steps"]:
        st.markdown(f'<div class="meta">Database: {" · ".join(reply["steps"])}</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar: connection and model choice
# -----------------------------------------------------------------------------

st.session_state.setdefault("messages", [])

with st.sidebar:
    st.markdown("### AI Gateway")
    BASE_URL = st.text_input("Gateway URL", value=SAVED_URL, placeholder="https://.../v1").strip()
    API_KEY = st.text_input("API key", value=SAVED_KEY, type="password", placeholder="sk-...").strip()
    st.caption("Never saved to a file. Cleared when you close the tab or stop the app.")
    st.write("")
    model = st.selectbox("Model", MODELS)
    st.divider()
    if st.button("Start over", width="stretch"):
        st.session_state.messages = []
        st.rerun()


# -----------------------------------------------------------------------------
# Main area: the conversation, then the demo prompts and message box at the bottom
# -----------------------------------------------------------------------------

st.title("AI Gateway Demo")
st.markdown('<div class="subtle">Every request is sent through the AI gateway. The assistant can search a '
            'database of personnel and mission records. <b>All of the data is synthetic.</b></div>',
            unsafe_allow_html=True)
st.write("")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=":material/person:" if msg["role"] == "user" else ":material/smart_toy:"):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            show(msg["reply"])

# Pinned to the bottom of the page, next to the message box. (Falls back to the normal page
# flow if a future Streamlit version renames this container.)
with getattr(st, "_bottom", st.container()):
    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    picked = col1.selectbox("Demo prompts", DEMO_PROMPTS, format_func=lambda p: f'{p["category"]}: {p["name"]}')
    send_demo = col2.button("Send", type="primary", width="stretch")
    typed = st.chat_input("Message the assistant")

prompt, prompt_model = None, model
if send_demo:
    prompt = picked["prompt"]
    if picked.get("model") == "restricted":
        prompt_model = MODELS[-1]
elif typed:
    prompt = typed

if prompt:
    if not (BASE_URL and API_KEY):
        st.warning("Enter the gateway URL and API key in the sidebar first.")
    else:
        # Earlier turns that got an answer are sent along, so follow-up questions work.
        history = []
        msgs = st.session_state.messages
        for user_msg, reply in zip(msgs[0::2], msgs[1::2]):
            if reply["reply"]["ok"]:
                history += [{"role": "user", "content": user_msg["content"]},
                            {"role": "assistant", "content": reply["reply"]["text"]}]
        history.append({"role": "user", "content": prompt})
        with st.spinner("Thinking"):
            reply = ask(prompt_model, history)
        st.session_state.messages += [{"role": "user", "content": prompt},
                                      {"role": "assistant", "reply": reply}]
        st.rerun()
