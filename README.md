# vaxalert


## How to use this
I hope you have a bash shell handy.

1. Clone the repo
```bash
git clone https://github.com/shashankmahajan/vaxalert
```
2. Fire up a new virtual env and activate it
```bash
python3 -m venv vaxalert_env
source vaxalert_env/bin/activate
```

3. Install the deps
```bash
pip install -r requirements.txt
```

4. Open up a new bash shell to set the alert job to run in.

5. Set the telegram bot token and the chat Id to post the messages to...
```bash
export TELERGAM_BOT_TOKEN=<your-bot-token>
export TELEGRAM_BOT_CHAT_ID=<your-group-chat_id>
```

6. Run the `vaxalert.py` script
```bash
chmod +x src/vaxalert/vaxalert.py
python3 -u vaxalert.py
```

If you want to change the polling frequency, update in `vaxalert.py` at line. Needs to be consistent with syntax of the `schedule` package.
```python
@repeat(every(5).minutes)
```