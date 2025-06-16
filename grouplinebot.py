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
    welcome_text = """🎉 歡迎加入《澳貝客遊學｜出遊群組》 🎉

嗨嗨～歡迎新朋友加入我們的出遊群組 👋
為了讓活動安排更順利，請新加入的朋友務必完成報到手續！

✅ 請到【記事本】留言報到
➡️ 寫上以下資訊：

中文名字／英文護照名／性別／語言學校
（範例：王小明／Wang Shaw Ming／男／Fella2）

⚠️ 沒有留言報到的同學，將不會列入出遊名單計算喔！

💵 訂金提醒
我們將於週四晚上 18:30 至 22:00 派員工到各語言學校門口收取訂金（現金付款）。
請準時出現並準備好正確金額，感謝配合！
"""
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

def reminder_message():
    message_text = """🧳 明天就要準備出發囉！

親愛的同學們，請大家務必提前準備，並注意以下事項：

✅ 請到【記事本】查看：
📌 行程內容
📌 行前注意事項
📌 接駁集合時間與地點
📌 建議攜帶的物品清單

🔔 請將手機設定鬧鐘，並打開鈴聲！
我們無法一一聯繫遲到者，請自行確保準時集合。

⚠️ 若超過接駁時間仍未到場，將視同自動放棄行程，訂金恕不退還。

感謝大家配合，我們明天見～🌴☀️
"""
    if GROUP_ID == 'Fill your groupId here':
        print("Group ID not set. Please retrieve correct groupId via webhook log first.")
        return

    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text=message_text))
        print("Successfully sent reminder message.")
    except Exception as e:
        print("Failed to send reminder message:", e)


def feedback_message():
    message_text = """💙 感謝大家參與澳貝客本週末的行程！ 💙

我們由衷感謝您的支持，這次的旅程因為有大家的熱情參與而更加精彩！✨ 為了提供更好的服務，我們誠摯地邀請您分享寶貴的意見與回饋。您的建議對我們來說至關重要，我們將虛心接受，努力提升每一次的旅行體驗。🙏

同時，也誠摯邀請您看看我們接下來的拼團活動！如果有感興趣的行程，歡迎加入，我們將以最熱情的笑容迎接您的參與！😊🌍

🔥 iOutback Agency 澳貝客遊學 週末拼團活動 🔥
📌 報名傳送門 👉 https://forms.gle/3pxQ9kjZMHZJQXd67
"""
    if GROUP_ID == 'Fill your groupId here':
        print("Group ID not set. Please retrieve correct groupId via webhook log first.")
        return

    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text=message_text))
        print("Successfully sent feedback message.")
    except Exception as e:
        print("Failed to send feedback message:", e)



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

scheduler.add_job(feedback_message, 'cron', day_of_week='mon', hour=14, minute=30)
scheduler.add_job(feedback_message, 'cron', day_of_week='mon', hour=14, minute=40)
scheduler.add_job(feedback_message, 'cron', day_of_week='mon', hour=15, minute=00)
# 每週四 中午12:00
scheduler.add_job(reminder_message, 'cron', day_of_week='thu', hour=12, minute=0)
# 每週五 晚上20:00
scheduler.add_job(reminder_message, 'cron', day_of_week='fri', hour=20, minute=0)
# 每週日 晚上20:00 (與回饋訊息重複，視你要發哪一個)
scheduler.add_job(reminder_message, 'cron', day_of_week='sun', hour=20, minute=0)

# 每週日 晚上 20:00 自動發送
scheduler.add_job(feedback_message, 'cron', day_of_week='sun', hour=20, minute=0)
scheduler.add_job(feedback_message, 'cron', day_of_week='mon', hour=14, minute=30)
scheduler.add_job(feedback_message, 'cron', day_of_week='mon', hour=14, minute=40)
scheduler.add_job(feedback_message, 'cron', day_of_week='mon', hour=15, minute=00)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
