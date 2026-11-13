# AI Gateway Demo

A simple chatbot that shows how an application connects to an AI gateway, and what the gateway controls once it does:

- **Which models can be used.** One model is allowed, the other is blocked.
- **Where visibility lives.** The app tracks nothing itself. Usage, cost, and logs are recorded by the gateway.
- **What gets stopped.** Prompt injection, harmful requests, and personal data.
- **How it is tested.** One click runs a test set across eight dimensions of responsible AI.

It works right away in **practice mode**, with simulated responses, so you can try it before you have a key.

```
basic-chat-demo/
├── README.md              You are here
├── requirements.txt       The two packages the app needs
├── demo/
│   ├── app.py             The chatbot
│   ├── prompts.py         The assistant's instructions and the demo prompts
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

If it prints `Python 3.10` or higher, skip to step 2. Otherwise, install it.

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

If a command fails, or says you don't have permission (common when your computer is managed by IT), install Python from your company's software center (on a Mac, often the **Self Service** app), or download it from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick **Add python.exe to PATH** on the installer's first screen.

### 2. Get the project

If you're on the GitHub page, click the green **Code** button, then **Download ZIP**. If someone emailed you a ZIP file, use that instead.

Unzip it. You get a folder, which may be called `basic-chat-demo` or `basic-chat-demo-main`. It's the folder that contains this `README.md` file.

### 3. Move the terminal into the project folder

The next step only works from inside the project folder.

**Mac:** paste this. It finds the project in your Downloads, Desktop, or Documents folder and moves you into it:

```bash
cd "$(dirname "$(find ~/Downloads ~/Desktop ~/Documents -maxdepth 4 -name requirements.txt -path '*basic-chat*' 2>/dev/null | head -1)")" && pwd && ls
```

**Windows:** open the project folder in File Explorer. Click the address bar at the top, type `cmd`, then press **Enter**. Then paste `dir`.

**Check before you continue:** the list printed in the terminal must include `README.md`, `requirements.txt`, `demo`, and `architecture`. If it doesn't, you're not in the project folder yet.

Another way on a Mac: type `cd` followed by a space, drag the project folder into the Terminal window, then press **Enter**.

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

It's ready when you see **You can now view your Streamlit app in your browser**. Your browser then opens the app at `http://localhost:8501`. The terminal also lists "Network" and "External" addresses: ignore those.

Leave the terminal window open while you use the app. Closing it stops the app.

### 5. Connect to the gateway

**No key yet?** Skip this step. Everything works in practice mode, with simulated responses, and a banner at the top of the app says so.

To get a key, ask your gateway administrator for access to the gateway's console, then:

1. In the console, create an API key for this app. Some gateways call it an agent key.
2. Copy the key. Many consoles show it **only once**, so paste it somewhere safe right away.
3. Copy the gateway's **base URL**. It ends in `/v1`.
   - In the console, it's the address shown on its own line, or the value after `base_url=` in a **Python** example.
   - **Don't** copy the address from a **curl** example. It has `/chat/completions` on the end, and the app will say "The gateway URL looks wrong."
   - No `/` at the end, no quotes, no spaces.

   | | Example |
   |---|---|
   | Right | `https://your-gateway.example.com/v1` |
   | Wrong | `https://your-gateway.example.com/v1/chat/completions` |

4. In the app's left sidebar, under **Connection**, paste the gateway URL in the first box and the API key in the second.

The sidebar changes from "Practice mode" to "Connected to", and the banner disappears. You're done.

The values look like this. Yours will be different:

| Value | Example |
|---|---|
| Gateway URL | `https://your-gateway.example.com/v1` |
| API key | `sk-AbCdEf1234567890XyZ` |
| Model names | `haiku-5-5`, as listed in your gateway's console or documentation |

If your gateway uses different model names from the two this demo lists (`haiku-5-5` and `sonnet-5-5`), see "Changing things" below.

---

## Stop and restart

To stop the app, click the terminal window and press `Ctrl + C`.

To start it again later, open a terminal, run the step 3 command, then paste this on a Mac:

```bash
python3 -m streamlit run demo/app.py
```

On Windows, use `python` instead of `python3`.

If you used the `.venv` fix from the troubleshooting table, paste `source .venv/bin/activate` first, every time.

After a restart, paste the URL and key into the sidebar again. To avoid that, save them in the file (see below).

---

## Presenting

Follow [demo/DEMO_SCRIPT.md](demo/DEMO_SCRIPT.md). It covers what to check the day before, what to click, what to say, and how to answer common questions.

To see how the app, the gateway, and the models connect, read [architecture/README.md](architecture/README.md).

---

## Changing things

Open the file in a plain-text code editor, such as [Visual Studio Code](https://code.visualstudio.com/) (free), or Notepad on Windows. Avoid Word and TextEdit: they can change quote marks and break the file.

| To change | Edit |
|---|---|
| Save the key and URL so you don't paste them every time | The settings block at the top of `demo/app.py`. Replace `PASTE-YOUR-API-KEY-HERE` and `PASTE-YOUR-GATEWAY-URL-HERE`, keeping the quote marks. |
| Model names | `MODELS` at the top of `demo/app.py`. Use your gateway's names, and put the allowed model first. |
| How the assistant writes (tone, length, rules) | `SYSTEM_PROMPT` in `demo/prompts.py` |
| Demo prompts and risk tests | `DEMO_PROMPTS` in `demo/prompts.py` |

After you save a change, stop and restart the app.

---

## Keeping the key safe

- A key pasted into the sidebar is never saved to a file. It's cleared when you close the tab or stop the app.
- If you save the key in `demo/app.py`, do not upload that file to GitHub or share it.
- If a key is exposed, create a new one in the gateway console, and ask the administrator to turn off the old one.

---

## Words you'll see

| Word | Meaning |
|---|---|
| Gateway | The checkpoint every AI request passes through. It decides which models may be used and what gets blocked. |
| API key | A password for an application. It tells the gateway which agent is asking. |
| HTTP 403, 400, 404 | Codes the gateway sends back. 403 and 400 usually mean "not allowed". 404 usually means the URL is wrong. |
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
| "The gateway rejected the API key" | The key has a typo or was replaced. Paste it again, or create a new one. |
| "The gateway URL looks wrong" | Paste the gateway's base URL, ending in `/v1`: the one on its own line in the console, or after `base_url=` in a Python example. Not the address from a curl example, which ends in `/chat/completions`. |
| "Could not reach the gateway" | Check the gateway URL, and your network or VPN connection. |
| "The gateway is rate limiting this key" | Wait a minute and try again. |
| Every message says "Blocked by gateway" | You probably have the restricted model selected. Switch **Model** in the sidebar back to the first one. |
| A prompt that should be blocked shows a normal answer starting with the gateway's block message | Copy the first few words of that message into `GATEWAY_BLOCK_PHRASES` in `demo/app.py`. |
| "The gateway may not support streaming" | Set `STREAM_RESPONSES = False` in `demo/app.py`. |
| The browser didn't open | Go to `http://localhost:8501` yourself. |
