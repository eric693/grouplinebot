from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

# Read environment variables (for safer deployment)
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '41bca95b39fdcdafef85449690202269')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '2FXQloCpn0Z4wpsUBT3Eep6aKseq9nG4xKlDATZBkfeBGnz4cBg0vbLr0iaEpidUHsRRuHASxj3b+a/FFA+r6n8zeZQFkcFy1uq1qHt/GDVGLHmkClduiOgqksEdUyA7CWST4E+BergVk1A6pTjMZwdB04t89/1O/w1cDnyilFU=')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# Group ID (keep empty at first, retrieve from webhook log)
GROUP_ID = os.getenv('GROUP_ID', 'C9ec92493f183879f10869c237aa145e6')

# Webhook entry point
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    print("Received webhook:", body)  # Debug log to help retrieve groupId

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Listen to member joined event
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    welcome_text = 'Welcome to the group 🎉 Please check the pinned messages for important info!'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_text))

# Listen to all message events (for debugging groupId at first time)
@handler.add(MessageEvent)
def handle_message(event):
    if event.source.type == 'group':
        print("Current Group ID:", event.source.group_id)

    # You can add message handling features here
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Message received"))

# Scheduled task setup
scheduler = BackgroundScheduler()

def scheduled_message():
    if GROUP_ID == 'Fill your groupId here':
        print("Group ID not set. Please retrieve correct groupId via webhook log first.")
        return

    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text='Scheduled reminder: Don’t forget to complete your tasks!'))
        print("Successfully sent scheduled message.")
    except Exception as e:
        print("Failed to send scheduled message:", e)

# Schedule: Auto send messages at multiple fixed times daily
scheduler.add_job(scheduled_message, 'cron', hour=8, minute=55)
scheduler.add_job(scheduled_message, 'cron', hour=9, minute=0)
scheduler.add_job(scheduled_message, 'cron', hour=9, minute=30)
scheduler.add_job(scheduled_message, 'cron', hour=10, minute=0)
scheduler.add_job(scheduled_message, 'cron', hour=10, minute=20)
scheduler.add_job(scheduled_message, 'cron', hour=10, minute=30)
scheduler.add_job(scheduled_message, 'cron', hour=10, minute=40)
scheduler.add_job(scheduled_message, 'cron', hour=10, minute=50)
scheduler.add_job(scheduled_message, 'cron', hour=21, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
