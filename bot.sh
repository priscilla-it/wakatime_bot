#!/bin/bash

SESSION_NAME="wakatime_bot"

if [[ "$1" == "--stop" ]]; then
    if screen -list | grep -q "$SESSION_NAME"; then
        screen -S "$SESSION_NAME" -X quit
        echo "🛑 Bot stopped."
    else
        echo "❌ No running session found for '$SESSION_NAME'."
    fi
    exit 0
fi

if [[ "$1" == "--attach" ]]; then
    if screen -list | grep -q "$SESSION_NAME"; then
        screen -r "$SESSION_NAME"
    else
        echo "❌ No running session found for '$SESSION_NAME'."
    fi
    exit 0
fi

if screen -list | grep -q "$SESSION_NAME"; then
    echo "⚠️ A session '$SESSION_NAME' already exists. Please terminate it or choose a different name."
    exit 1
fi

screen -S "$SESSION_NAME" -d -m uv run src/bot.py

if [[ $? -eq 0 ]]; then
    echo "✅ Bot started in the background in screen session '$SESSION_NAME'."
else
    echo "❌ Failed to start the bot."
    exit 1
fi
