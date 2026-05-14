#!/usr/bin/env python3
"""
Discord bot powered by local Ollama LLM models.
Commands:
  !chat <message>     - Chat with default model (qwen2.5:7b)
  !think <message>    - Use smarter model (qwen2.5:14b)
  !models             - List available models
  !switch <model>     - Switch default model
  !clear              - Clear your conversation history
  !help               - Show help
"""

import discord
from discord.ext import commands
import ollama
import asyncio
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

# Configuration
DISCORD_TOKEN   = os.getenv("DISCORD_TOKEN")
DEFAULT_MODEL   = os.getenv("DEFAULT_MODEL", "qwen2.5:7b")
FAST_MODEL      = os.getenv("FAST_MODEL", "qwen2.5:7b")
SMART_MODEL     = os.getenv("SMART_MODEL", "qwen2.5:14b")
OLLAMA_HOST     = os.getenv("OLLAMA_HOST", "http://localhost:11434")
BOT_PREFIX      = os.getenv("BOT_PREFIX", "!")
MAX_LENGTH      = int(os.getenv("MAX_RESPONSE_LENGTH", 1900))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# Store conversation history per user
conversation_history = defaultdict(list)
user_models = {}  # Track each user's chosen model

def get_user_model(user_id):
    return user_models.get(user_id, DEFAULT_MODEL)

def split_response(text, max_length=1900):
    """Split long responses into chunks for Discord's 2000 char limit."""
    if len(text) <= max_length:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_at = text.rfind('\n', 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    return chunks

async def query_ollama(model, messages):
    """Query Ollama asynchronously."""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: ollama.chat(model=model, messages=messages)
    )
    return response['message']['content']

# ─── Events ───────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
    print(f'   Default model : {DEFAULT_MODEL}')
    print(f'   Fast model    : {FAST_MODEL}')
    print(f'   Smart model   : {SMART_MODEL}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{BOT_PREFIX}chat | Powered by Ollama"
    ))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❓ Unknown command. Use `{BOT_PREFIX}help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Missing argument. Use `{BOT_PREFIX}help` for usage.")
    else:
        await ctx.send(f"❌ An error occurred: `{str(error)}`")

# ─── Commands ─────────────────────────────────────────────────────────────────

@bot.command(name='chat', aliases=['c', 'ask'])
async def chat(ctx, *, message: str):
    """Chat with the default model (maintains conversation history)."""
    user_id = ctx.author.id
    model = get_user_model(user_id)

    async with ctx.typing():
        conversation_history[user_id].append({
            'role': 'user',
            'content': message
        })

        try:
            response = await query_ollama(model, conversation_history[user_id])
            conversation_history[user_id].append({
                'role': 'assistant',
                'content': response
            })

            chunks = split_response(response)
            for i, chunk in enumerate(chunks):
                prefix = f"🤖 **{model}**\n" if i == 0 else ""
                await ctx.send(f"{prefix}{chunk}")

        except Exception as e:
            conversation_history[user_id].pop()
            await ctx.send(f"❌ Error connecting to Ollama: `{str(e)}`\nMake sure Ollama is running!")

@bot.command(name='think', aliases=['smart', 's'])
async def think(ctx, *, message: str):
    """Use the smarter model for complex reasoning (no history)."""
    async with ctx.typing():
        await ctx.send(f"🧠 Thinking with **{SMART_MODEL}**...")
        try:
            response = await query_ollama(SMART_MODEL, [
                {'role': 'user', 'content': message}
            ])
            chunks = split_response(response)
            for i, chunk in enumerate(chunks):
                prefix = f"🧠 **{SMART_MODEL}**\n" if i == 0 else ""
                await ctx.send(f"{prefix}{chunk}")
        except Exception as e:
            await ctx.send(f"❌ Error: `{str(e)}`")

@bot.command(name='models', aliases=['m', 'list'])
async def list_models(ctx):
    """List all available Ollama models."""
    try:
        loop = asyncio.get_event_loop()
        model_list = await loop.run_in_executor(None, ollama.list)
        models = model_list.get('models', [])

        if not models:
            await ctx.send("⚠️ No models found. Pull a model with `ollama pull <model>`")
            return

        embed = discord.Embed(
            title="🤖 Available Ollama Models",
            color=discord.Color.blue()
        )

        for m in models:
            name = m['name']
            size = m.get('size', 0)
            size_gb = f"{size / 1e9:.1f} GB"
            active = "⭐ Active" if name == get_user_model(ctx.author.id) else ""
            embed.add_field(name=f"`{name}` {active}", value=size_gb, inline=True)

        embed.set_footer(text=f"Use {BOT_PREFIX}switch <model> to change your model")
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error fetching models: `{str(e)}`")

@bot.command(name='switch', aliases=['use', 'model'])
async def switch_model(ctx, model_name: str):
    """Switch your active model."""
    try:
        loop = asyncio.get_event_loop()
        model_list = await loop.run_in_executor(None, ollama.list)
        available = [m['name'] for m in model_list.get('models', [])]

        if model_name not in available:
            await ctx.send(f"❌ Model `{model_name}` not found.\nAvailable: {', '.join(f'`{m}`' for m in available)}")
            return

        user_models[ctx.author.id] = model_name
        await ctx.send(f"✅ Switched to **{model_name}**")

    except Exception as e:
        await ctx.send(f"❌ Error: `{str(e)}`")

@bot.command(name='clear', aliases=['reset', 'new'])
async def clear_history(ctx):
    """Clear your conversation history."""
    user_id = ctx.author.id
    count = len(conversation_history[user_id])
    conversation_history[user_id] = []
    await ctx.send(f"🧹 Cleared {count} messages from your conversation history.")

@bot.command(name='help', aliases=['h'])
async def help_command(ctx):
    """Show available commands."""
    embed = discord.Embed(
        title="🤖 Ollama Discord Bot",
        description="A Discord bot powered by your local Ollama LLM models.",
        color=discord.Color.green()
    )

    embed.add_field(
        name=f"`{BOT_PREFIX}chat <message>` | `{BOT_PREFIX}c`",
        value="Chat with your active model (maintains conversation history)",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}think <message>` | `{BOT_PREFIX}s`",
        value=f"Use the smarter model (`{SMART_MODEL}`) for complex reasoning",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}models`",
        value="List all available Ollama models",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}switch <model>`",
        value="Switch your active model",
        inline=False
    )
    embed.add_field(
        name=f"`{BOT_PREFIX}clear`",
        value="Clear your conversation history",
        inline=False
    )

    embed.set_footer(text=f"Default: {DEFAULT_MODEL} | Smart: {SMART_MODEL} | Powered by Ollama")
    await ctx.send(embed=embed)

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not set in .env file!")
        print("   1. Go to https://discord.com/developers/applications")
        print("   2. Create a bot and copy the token")
        print("   3. Paste it in your .env file")
        exit(1)

    print("🚀 Starting Ollama Discord Bot...")
    bot.run(DISCORD_TOKEN)
