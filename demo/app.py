"""
AI Gateway Demo
The simplest possible agent: a chat assistant with one tool, which searches a small
database of synthetic records. Every request goes through the AI gateway. The app adds
no security logic of its own: whatever the gateway refuses is shown exactly as it was sent.

Run it from the main project folder:  python3 -m streamlit run demo/app.py
"""

import json
import os

import streamlit as st
import streamlit.components.v1 as components
from openai import APIStatusError, OpenAI

from database import TOOLS, run_tool
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

# The two models in the Model dropdown, spelled exactly as your gateway names them.
#   First:  a model this app IS allowed to use. It's selected when the app starts.
#   Second: a model your gateway DENIES for this app. The "Restricted model" demo prompt uses it.
MODELS = ["haiku-5-5", "sonnet-5-5"]

# How long to wait for an answer before giving up, in seconds.
REQUEST_TIMEOUT_SECONDS = 60

# The assistant searches the synthetic database with tool calls. If your gateway doesn't
# support tool calling, set this to False. The assistant then works as a plain chatbot,
# and the "(database)" demo prompts won't have any data to work with.
AGENT_USE_TOOLS = True

# =============================================================================
# End of settings. You should not need to change anything below this line.
# =============================================================================

# Environment variables GATEWAY_API_KEY and GATEWAY_BASE_URL, if set, take priority.
SAVED_KEY = os.getenv("GATEWAY_API_KEY") or ("" if API_KEY.startswith("PASTE") else API_KEY)
SAVED_URL = os.getenv("GATEWAY_BASE_URL") or ("" if BASE_URL.startswith("PASTE") else BASE_URL)
MAX_TOOL_ROUNDS = 5

st.set_page_config(page_title="AI Gateway Demo", layout="centered")
st.markdown("""<style>
  #MainMenu, footer, [data-testid='stDecoration'] {visibility: hidden;}
  [data-testid='stCaptionContainer'] {opacity: 0.75;}
  [data-testid='stMainBlockContainer'] {padding-top: 2.5rem;}
  [data-testid='stBottomBlockContainer'] {padding-bottom: 1rem;}
</style>""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Talking to the gateway
# -----------------------------------------------------------------------------

def raw(status, body):
    """The gateway's response, shown as is."""
    return {"ok": False, "text": f"HTTP {status}\n\n{body}"}


def describe(name, arguments):
    """A database search in plain words, for the gray line under an answer."""
    try:
        query = json.loads(arguments).get("query", "")
    except Exception:
        return f"{name}({arguments})"
    table = {"search_personnel": "personnel", "search_missions": "missions"}.get(name, name)
    return f'searched {table} for "{query}"'


def ask(gateway_url, api_key, model, history):
    """
    Send the conversation through the gateway, running any database searches the model asks for.
    Returns the answer, or the gateway's response exactly as it came back if it wasn't one.
    """
    client = OpenAI(base_url=gateway_url, api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=0)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    steps = []
    try:
        for _ in range(MAX_TOOL_ROUNDS):
            request = {"model": model, "messages": messages, "max_tokens": 4096}
            if AGENT_USE_TOOLS:
                request["tools"] = TOOLS
            response = client.chat.completions.with_raw_response.create(**request)
            try:
                message = response.parse().choices[0].message
            except Exception:  # not a normal answer: show what the gateway sent
                return {**raw(response.status_code, response.text), "steps": steps}
            if not message.tool_calls:
                if not message.content:
                    return {**raw(response.status_code, response.text), "steps": steps}
                return {"ok": True, "text": message.content, "steps": steps}
            messages.append({"role": "assistant", "content": message.content, "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in message.tool_calls]})
            for tc in message.tool_calls:
                steps.append(describe(tc.function.name, tc.function.arguments))
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": run_tool(tc.function.name, tc.function.arguments)})
        return {"ok": False, "text": f"Stopped after {MAX_TOOL_ROUNDS} rounds of database searches.", "steps": steps}
    except APIStatusError as e:
        return {**raw(e.status_code, e.response.text), "steps": steps}
    except Exception as e:
        cause = f"\n{e.__cause__}" if e.__cause__ else ""
        return {"ok": False, "text": f"{type(e).__name__}: {e}{cause}", "steps": steps}


def show(reply):
    if reply["ok"]:
        st.markdown(reply["text"])
    else:
        st.code(reply["text"], language=None, wrap_lines=True)
    if reply["steps"]:
        st.caption("Database: " + " · ".join(reply["steps"]))


# -----------------------------------------------------------------------------
# Sidebar: connection and model choice
# -----------------------------------------------------------------------------

st.session_state.setdefault("messages", [])
st.session_state.setdefault("pending", None)

with st.sidebar:
    st.markdown("### Connection")
    gateway_url = st.text_input("Gateway URL", value=SAVED_URL, placeholder="https://.../v1").strip()
    api_key = st.text_input("API key", type="password", placeholder="sk-...").strip() or SAVED_KEY
    st.caption("Using the key from GATEWAY_API_KEY or app.py." if SAVED_KEY else
               "Press Enter after pasting each one. Not saved to disk. Cleared when this tab is closed or refreshed.")
    st.write("")
    model = st.selectbox("Model", MODELS)
    st.divider()
    if st.button("Start over", width="stretch"):
        st.session_state.messages, st.session_state.pending = [], None
        st.rerun()


# -----------------------------------------------------------------------------
# Main area: the conversation, with the demo prompts and message box pinned at the bottom
# -----------------------------------------------------------------------------

st.title("AI Gateway Demo")
st.caption("Every request is sent through the AI gateway. The assistant can search a database of "
           "personnel and mission records. **All of the data is synthetic.**")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=":material/person:" if msg["role"] == "user" else ":material/smart_toy:"):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            show(msg["reply"])

# Answer the question that was just sent. It was saved first, so it stays on screen
# even if someone clicks something while the answer is on its way.
pending = st.session_state.pending
if pending:
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("Waiting for a response"):
            reply = ask(gateway_url, api_key, pending["model"], pending["history"])
            st.session_state.messages.append({"role": "assistant", "reply": reply})
            st.session_state.pending = None
    st.rerun()

# Keep the latest question and its answer in view.
if st.session_state.messages:
    scroll = f"""<script> /* {len(st.session_state.messages)} */ (() => {{
      const page = window.parent.document;
      const toLatest = () => {{  // bring the latest question to the top, so long answers start in view
        const msgs = page.querySelectorAll('[data-testid="stChatMessage"]');
        const latest = msgs[msgs.length - 2] || msgs[msgs.length - 1];
        if (latest) latest.scrollIntoView({{block: "start"}});
      }};
      [150, 600].forEach(ms => setTimeout(toLatest, ms));  // twice: some versions auto-scroll after the first
    }})();</script>"""
    try:
        st.html(scroll, unsafe_allow_javascript=True)  # newer Streamlit
    except TypeError:
        components.html(scroll, height=0)  # older Streamlit

with getattr(st, "bottom", None) or st._bottom:  # newer Streamlit: st.bottom; older: st._bottom
    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    picked = col1.selectbox("Demo prompts", DEMO_PROMPTS, format_func=lambda p: f'{p["category"]}: {p["name"]}')
    send_demo = col2.button("Send", type="primary", width="stretch")
    typed = st.chat_input("Message the assistant")

if send_demo or typed:
    if not (gateway_url and api_key):
        st.warning("Enter the gateway URL and API key in the sidebar. Press Enter after each.")
    else:
        if send_demo:
            # Demo prompts are sent on their own, so an earlier prompt can't affect the result.
            text, use_model, history = picked["prompt"], MODELS[1] if picked.get("model") == "restricted" else model, []
        else:
            # Typed messages continue the conversation: earlier turns that got an answer are sent along.
            text, use_model, history = typed, model, []
            msgs = st.session_state.messages
            for user_msg, answer in zip(msgs[0::2], msgs[1::2]):
                if answer["reply"]["ok"]:
                    history += [{"role": "user", "content": user_msg["content"]},
                                {"role": "assistant", "content": answer["reply"]["text"]}]
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.pending = {"model": use_model, "history": history + [{"role": "user", "content": text}]}
        st.rerun()
