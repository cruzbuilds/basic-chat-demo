# Enterprise Assistant

A demo of an AI gateway, built as the kind of simple internal assistant any team might create.

The simplest possible AI agent: a chat assistant with one tool, a small database it can search. Every request goes through an AI gateway, and the gateway decides what's allowed.

- **The app** sends requests and shows what comes back. It has no security logic of its own. When the gateway refuses something, the page shows the gateway's response exactly as it was sent.
- **The gateway** controls which models the app may use and enforces the guardrails.
- **The database** holds 200 records of **synthetic** personnel and mission data, including fake Social Security numbers. It's built in memory each time the app starts, and nothing is saved to disk. It's there so the demo can show requests a model would happily answer, but the gateway should stop.

Pick a suggested prompt from the dropdown at the bottom of the page, click **Send**, and watch what the gateway does.

```
basic-chat-demo/
├── README.md              You are here
├── requirements.txt       The two packages the app needs
├── demo/
│   ├── app.py             The app
│   ├── prompts.py         The assistant's instructions and the suggested prompts
│   ├── database.py        The synthetic data and the tool that searches it
│   └── DEMO_SCRIPT.md     Step-by-step script for presenting the demo
└── architecture/
    └── README.md          How the pieces fit together
```

---

## Start the demo

### 1. Install Python (one time only)

Open the **Terminal** app on a Mac (press `Cmd + Space`, type `Terminal`, press **Enter**), or **Command Prompt** on Windows. A terminal is a window where you type commands. Paste each command below and press **Enter**.

First check whether Python is already installed:

```bash
python3 --version
```

On Windows, type `python --version` instead.

If it prints `Python 3.10` or higher, skip to step 2.

If it prints an older version (a new Mac often has 3.9), or a box pops up offering to install "command line developer tools", close the box and install Python with the commands below.

**Mac:** paste these two commands, one at a time. The second asks for your Mac password. Nothing shows while you type, which is normal.

```bash
curl -o ~/Downloads/python.pkg https://www.python.org/ftp/python/3.12.8/python-3.12.8-macos11.pkg
```

```bash
sudo installer -pkg ~/Downloads/python.pkg -target /
```

**Windows:**

```bash
winget install -e --id Python.Python.3.12
```

Then close the terminal and open it again, so it finds the new Python.

If a command fails, or says you don't have permission (common when your computer is managed by IT), install Python from your company's software center app, or download it from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick **Add python.exe to PATH** on the installer's first screen.

### 2. Get the project

If you're on the GitHub page, click the green **Code** button, then **Download ZIP**. If someone emailed you a ZIP file, use that instead.

Unzip it. You get a folder, which may be called `basic-chat-demo` or `basic-chat-demo-main`. It's the folder that contains this `README.md` file.

### 3. Move the terminal into the project folder

The next step only works from inside the project folder.

**Mac:** paste this. It finds the project in your Downloads, Desktop, or Documents folder and moves you into it:

```bash
P="$(find ~/Downloads ~/Desktop ~/Documents -maxdepth 4 -name requirements.txt -path '*basic-chat*' 2>/dev/null | head -1)"; if [ -n "$P" ]; then cd "$(dirname "$P")" && pwd && ls; else echo "Project folder not found. Use the drag method below."; fi
```

If your Mac asks whether Terminal may access your Downloads, Desktop, or Documents folder, click **OK**. If you have more than one copy of the project, delete the extras first, or use the drag method below.

**Windows:** open the project folder in File Explorer. Click the address bar at the top, type `cmd`, then press **Enter**. Then paste `dir`.

**Check before you continue:** the list printed in the terminal must include `README.md`, `requirements.txt`, `demo`, and `architecture`. If it doesn't, you're not in the project folder yet.

**Drag method (Mac):** type `cd` followed by a space, drag the project folder from Finder into the Terminal window, then press **Enter**. Then paste `ls` and check the list as above.

### 4. Copy, paste, press Enter

**Mac:**

```bash
python3 -m pip install -r requirements.txt && python3 -m streamlit run demo/app.py
```

**Windows:**

```bash
python -m pip install -r requirements.txt && python -m streamlit run demo/app.py
```

You'll see a lot of text scroll by, and maybe a yellow `WARNING`. That's normal. The first time takes a minute or two.

It's ready when you see **You can now view your Streamlit app in your browser**. Your browser then opens the app at `http://localhost:8501`. If it doesn't open on its own, open your browser and go to `http://localhost:8501`. Only your own computer can open it.

Leave the terminal window open while you use the app. Closing it stops the app.

### 5. Connect to the gateway

The app needs a gateway URL and an API key. **If your administrator already gave you both, skip to item 4**, and use the URL exactly as they gave it (it may start with `http://` or `https://`).

To get them yourself, ask your gateway administrator for access to the gateway's console, then:

1. In the console, create an API key for this app. Some gateways call it an agent key.
2. Copy the key. Many consoles show it **only once**, so paste it somewhere safe right away.
3. Copy the gateway's **base URL**. It starts with `https://` (sometimes `http://`) and ends in `/v1`.
   - In the console, it's the address shown on its own line, or the value after `base_url=` in a **Python** example.
   - **Don't** copy the address from a **curl** example. It has `/chat/completions` on the end, and requests will fail with `HTTP 404`.
   - No `/` at the end, no quotes, no spaces.

   | | Example |
   |---|---|
   | Right | `https://your-gateway.example.com/v1` |
   | Wrong | `https://your-gateway.example.com/v1/chat/completions` |

4. In the app's left sidebar, paste the gateway URL into the **Gateway URL** box and press **Enter**. Then paste the API key into the **API key** box and press **Enter**.
5. Check that it works: in the **Suggested prompts** box at the bottom of the page, choose **Baseline: Explain zero trust** and click **Send**. An answer means you're connected. A gray box starting with `HTTP` means something's wrong: see "If something goes wrong" below.

If the sidebar is hidden, move your mouse to the top-left corner of the page and click the arrow that appears.

The values look like this. Yours will be different:

| Value | Example |
|---|---|
| Gateway URL | `https://your-gateway.example.com/v1` |
| API key | `sk-AbCdEf1234567890XyZ` |
| Model names | `haiku-5-5`, as listed in your gateway's console or documentation |

If your gateway uses different model names from the two this demo lists (`haiku-5-5` and `sonnet-5-5`), see "Changing things" below.

## Using the app

- **Suggested prompts** (bottom of the page): pick one and click **Send**. Typing in the box filters the list. Each suggested prompt is sent on its own, so an earlier prompt can't affect the next result.
- **Message box** (very bottom): type your own question. Typed messages continue the conversation, so follow-up questions work.
- **Start over** (sidebar): clears the conversation. It keeps the URL and key.
- When the gateway refuses something, the app shows exactly what the gateway sent back, in a gray box starting with an HTTP code. The app never blocks or changes anything itself.

---

## Stop and restart

To stop the app, click the terminal window and press `Ctrl + C`.

To start it again later, open a terminal, run the step 3 command, then paste this on a Mac:

```bash
python3 -m streamlit run demo/app.py
```

On Windows, use `python` instead of `python3`.

If you used the `.venv` fix from the troubleshooting table, paste `source .venv/bin/activate` first, every time.

After a restart, paste the URL and key into the sidebar again. To avoid that, set them once per terminal window (see "Changing things" below), or save them in the file.

---

## Presenting

Follow [demo/DEMO_SCRIPT.md](demo/DEMO_SCRIPT.md). It covers what to check the day before, what to click, what to say, and how to answer common questions.

To see how the app, the gateway, and the models connect, read [architecture/README.md](architecture/README.md).

---

## Changing things

Open the file in a plain-text code editor, such as [Visual Studio Code](https://code.visualstudio.com/) (free), or Notepad on Windows. Avoid Word and TextEdit: they can change quote marks and break the file.

| To change | Edit |
|---|---|
| Connect automatically, without pasting the URL and key | Stop the app (`Ctrl + C`). In the same terminal window, set the two values, then start the app with the command from "Stop and restart". **Mac:** `export GATEWAY_API_KEY="sk-AbCdEf1234567890XyZ" GATEWAY_BASE_URL="https://your-gateway.example.com/v1"` with your own key and URL in place of the examples. Keep the quote marks in this command. **Windows:** `set GATEWAY_API_KEY=sk-AbCdEf1234567890XyZ`, then `set GATEWAY_BASE_URL=https://your-gateway.example.com/v1`, with no quote marks. The API key box in the app then stays empty and says "Using the key from GATEWAY_API_KEY or app.py". This lasts until you close that terminal window, and nothing is saved to a file. |
| Save the URL and key in the app permanently | The settings block at the top of `demo/app.py`. Replace `PASTE-YOUR-API-KEY-HERE` and `PASTE-YOUR-GATEWAY-URL-HERE`, keeping the quote marks. Don't share or upload the file afterwards. |
| Model names | `MODELS` at the top of `demo/app.py`. Use your gateway's exact names. The **first** must be a model this app is allowed to use. The **second** must be one your gateway **denies** for this app: the "Restricted model" suggested prompt uses it. |
| Gateway doesn't support tool calling | Set `AGENT_USE_TOOLS = False` in `demo/app.py`. The assistant then works as a plain chatbot, and the "(database)" prompts have no data to work with. |
| How the assistant writes (tone and length) | `SYSTEM_PROMPT` in `demo/prompts.py` |
| The suggested prompts in the dropdown | `DEMO_PROMPTS` in `demo/prompts.py`. The comments there explain each field. |

After you save a change, stop and restart the app.

---

## Keeping the key safe

- A key pasted into the sidebar, or set with `export`, is never saved to a file. It's cleared when you close the tab or stop the app.
- The app only accepts connections from your own computer, so nobody else on the same network can open it.
- If you save the key in `demo/app.py`, do not upload that file to GitHub or share it.
- If a key is exposed, create a new one in the gateway console, and ask the administrator to turn off the old one.

---

## Words you'll see

| Word | Meaning |
|---|---|
| Gateway | The checkpoint every AI request passes through. It decides which models may be used and what gets blocked. |
| API key | A password for an application. It tells the gateway which agent is asking. |
| HTTP 400, 403, 404, 429 | Codes the gateway sends back when it refuses a request. Exactly what each means depends on your gateway, but usually: 400 or 403 = not allowed by policy, 404 = wrong URL or unknown model, 429 = too many requests. |
| Tool | Something the assistant can use. Here, the only tool is "search the database". |
| `/v1` | The last part of the gateway URL. It must be included. |

---

## If something goes wrong

| You see | What to do |
|---|---|
| `command not found: python3` or `'python' is not recognized` | Install Python (step 1). On Windows, reinstall and tick **Add python.exe to PATH**. |
| `externally-managed-environment` during install | Paste `python3 -m venv .venv && source .venv/bin/activate`, then run step 4 again. From now on, paste `source .venv/bin/activate` each time before you start the app. |
| The install can't download packages | Your network may block package downloads. Ask IT for the internal Python package mirror. |
| `Could not open requirements file` or `No such file or directory` | The terminal isn't inside the project folder. Run step 3 again, and check that the list it prints includes `requirements.txt`. |
| `No module named streamlit` | Run step 4 again. If you used `.venv`, paste `source .venv/bin/activate` first. |
| `HTTP 401` | The key has a typo or was replaced. Paste it again, or create a new one. |
| `HTTP 404` on every message | The gateway URL is wrong. Paste the base URL ending in `/v1`, not the address from a curl example. |
| `APIConnectionError` or `APITimeoutError` | The app couldn't reach the gateway. Check that the URL is exactly what your administrator gave you, starts with `https://` or `http://`, and has no quotes or spaces, then check your network or VPN connection. The line under the error usually says more. |
| A refusal on every message, even "hello" | You may have the restricted model selected. Switch **Model** in the sidebar back to the first one. |
| An answer comes back, but nothing on screen seems to change | The page scrolls to the newest message on its own. If it didn't, scroll down. |
| `HTTP 400` mentioning `tools` | Your gateway doesn't support tool calling. Set `AGENT_USE_TOOLS = False` in `demo/app.py`. |
| The browser didn't open | Go to `http://localhost:8501` yourself. |
