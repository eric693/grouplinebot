from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

# 讀取環境變數（部署用更安全）
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '41bca95b39fdcdafef85449690202269')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '2FXQloCpn0Z4wpsUBT3Eep6aKseq9nG4xKlDATZBkfeBGnz4cBg0vbLr0iaEpidUHsRRuHASxj3b+a/FFA+r6n8zeZQFkcFy1uq1qHt/GDVGLHmkClduiOgqksEdUyA7CWST4E+BergVk1A6pTjMZwdB04t89/1O/w1cDnyilFU=')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# 群組ID (第一次先設為空，等等透過 webhook 印出來)
GROUP_ID = os.getenv('GROUP_ID', 'C9ec92493f183879f10869c237aa145e6')

# Webhook 入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    print("收到 webhook:", body)  # Debug用，幫助你拿到 groupId

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 監聽新成員加入事件
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    welcome_text = '歡迎新朋友加入本群組 🎉 有問題請參考置頂公告喔！'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_text))

# 監聽所有訊息事件，順便印出 groupId (第一次拿 ID 用)
@handler.add(MessageEvent)
def handle_message(event):
    if event.source.type == 'group':
        print("你目前的群組ID是:", event.source.group_id)

    # 這裡可以額外加入訊息處理功能
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text="收到訊息囉"))

# 定時排程任務
scheduler = BackgroundScheduler()

def scheduled_message():
    if GROUP_ID == '填入你的群組ID':
        print("尚未設定群組ID，請先透過 webhook 拿到正確 groupId")
        return

    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text='這是固定時段提醒：大家記得完成任務！'))
        print("成功發送排程訊息")
    except Exception as e:
        print("排程發送失敗:", e)

# 每天早上 9:00 與 晚上 21:00 自動發訊息
scheduler.add_job(scheduled_message, 'cron', hour=8, minute=55)
scheduler.add_job(scheduled_message, 'cron', hour=9, minute=0)
scheduler.add_job(scheduled_message, 'cron', hour=9, minute=30)
scheduler.add_job(scheduled_message, 'cron', hour=10, minute=00)
scheduler.add_job(scheduled_message, 'cron', hour=21, minute=0)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
