# 🤖 Ollama Discord Bot

A Discord bot powered by your **local Ollama LLM models**. Run AI conversations directly in Discord without sending data to external APIs — everything runs on your own machine.

---

## Features

- 💬 **Conversational memory** — `!chat` remembers your conversation context per user
- 🧠 **Multi-model support** — Switch between fast and powerful models on the fly
- 👤 **Per-user settings** — Each user has their own conversation history and model preference
- 📄 **Long response handling** — Automatically splits responses exceeding Discord's 2000 character limit
- ⚡ **Async design** — Non-blocking responses, multiple users can chat simultaneously
- 🔒 **100% local** — No data sent to external APIs, fully private

---

## Prerequisites

- macOS / Linux
- [Python 3.12+](https://www.python.org/)
- [Ollama](https://ollama.com/) installed and running
- At least one Ollama model pulled (see below)
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))

---

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:Arjun-Ramesh-tech/ollama-discord-bot.git
cd ollama-discord-bot
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
nano .env  # Add your Discord bot token
```

Edit `.env` with your values:

```env
DISCORD_TOKEN=your_discord_bot_token_here
DEFAULT_MODEL=qwen2.5:7b
FAST_MODEL=qwen2.5:7b
SMART_MODEL=qwen2.5:14b
OLLAMA_HOST=http://localhost:11434
BOT_PREFIX=!
MAX_RESPONSE_LENGTH=1900
```

### 5. Pull Ollama Models

```bash
# Fast model for daily use
ollama pull qwen2.5:7b

# Powerful model for complex reasoning
ollama pull qwen2.5:14b
```

### 6. Start Ollama Service

```bash
brew services start ollama   # macOS
# or
ollama serve                 # Manual start
```

### 7. Run the Bot

```bash
python bot.py
```

You should see:

```
🚀 Starting Ollama Discord Bot...
✅ YourBot#1234 is online!
   Default model : qwen2.5:7b
   Fast model    : qwen2.5:7b
   Smart model   : qwen2.5:14b
```

---

## Commands

| Command            | Alias            | Description                                                  |
| ------------------ | ---------------- | ------------------------------------------------------------ |
| `!chat <message>`  | `!c`, `!ask`     | Chat with your active model (maintains conversation history) |
| `!think <message>` | `!s`, `!smart`   | Use the smarter model for complex reasoning (no history)     |
| `!models`          | `!m`, `!list`    | List all available Ollama models                             |
| `!switch <model>`  | `!use`, `!model` | Switch your active model                                     |
| `!clear`           | `!reset`, `!new` | Clear your conversation history                              |
| `!help`            | `!h`             | Show all available commands                                  |

### Examples

```
!chat What is machine learning?
!c Write a Python function to reverse a string
!think Analyze the philosophical implications of AI consciousness
!switch qwen2.5:14b
!models
!clear
```

---

## Recommended Models

| Model         | Size   | Speed       | Best For                             |
| ------------- | ------ | ----------- | ------------------------------------ |
| `qwen2.5:7b`  | 4.7 GB | ~27 tok/s   | Daily use, quick questions           |
| `qwen2.5:14b` | 9 GB   | ~13.5 tok/s | Complex reasoning, detailed analysis |
| `llama3.2:3b` | 2 GB   | ~60 tok/s   | Ultra-fast simple tasks              |

---

## Running in Background (Optional)

To keep the bot running when your terminal is closed, use `tmux`:

```bash
# Install tmux
brew install tmux

# Start a named session
tmux new -s discord-bot

# Run the bot inside tmux
source .venv/bin/activate
python bot.py

# Detach from session: Ctrl+B then D
# Reattach later:
tmux attach -t discord-bot
```

---

## Troubleshooting

**Bot not responding:**

- Check that Ollama is running: `ollama list`
- Verify Message Content Intent is enabled in Discord Developer Portal
- Make sure the bot has Send Messages and Read Messages permissions in the channel

**Slow responses:**

- Use a smaller model: `!switch qwen2.5:7b`
- Check system memory usage
- Avoid running large model downloads while the bot is active

**`externally-managed-environment` error:**

- Always use `python -m pip install` inside a virtual environment instead of `pip install`

---

## License

MIT License — feel free to use and modify for your own projects.

---

## Author

**Arjun Ramesh** — [GitHub](https://github.com/Arjun-Ramesh-tech)
