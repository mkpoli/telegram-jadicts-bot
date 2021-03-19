# Telegram 用 辞書 BOT

Currently running at: [@jadicts_bot](https://telegram.me/jadicts_bot)

![Python Version](https://img.shields.io/badge/python-3.9-green)

## Deployment
```
# Create a python virtual environment
python3.9 -m venv venv
# Then activate it

# After that
pip install -r requirements.txt
python bot.py
```

## Update *requirements.txt*

```
pip install pip-tools
pip-compile .\requirements.
```

## Development
```
nodemon --exec python bot.py

# In venv: nodemon --exec "./venv/scripts/python bot.py" -e py
```
