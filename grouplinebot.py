from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import time

# 讀取環境變數
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '41bca95b39fdcdafef85449690202269')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '2FXQloCpn0Z4wpsUBT3Eep6aKseq9nG4xKlDATZBkfeBGnz4cBg0vbLr0iaEpidUHsRRuHASxj3b+a/FFA+r6n8zeZQFkcFy1uq1qHt/GDVGLHmkClduiOgqksEdUyA7CWST4E+BergVk1A6pTjMZwdB04t89/1O/w1cDnyilFU=')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# 你的 Group ID
GROUP_ID = os.getenv('GROUP_ID', 'C9ec92493f183879f10869c237aa145e6')

# 歡迎訊息防重複控制
last_welcome_time = 0
WELCOME_COOLDOWN = 3  # 秒

# Webhook 入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("Received webhook:", body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 成員加入事件處理
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    global last_welcome_time
    now = time.time()
    if now - last_welcome_time < WELCOME_COOLDOWN:
        print("Skip sending welcome message due to cooldown.")
        return

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
    last_welcome_time = now

# 印出 Group ID (方便第一次取 ID 用)
@handler.add(MessageEvent)
def handle_message(event):
    if event.source.type == 'group':
        print("Current Group ID:", event.source.group_id)

# 排程初始化
scheduler = BackgroundScheduler()

# 每日固定提醒
# def scheduled_message():
#     message_text = 'Scheduled reminder: Don’t forget to complete your tasks!'
#     try:
#         line_bot_api.push_message(GROUP_ID, TextSendMessage(text=message_text))
#         print("Successfully sent scheduled message.")
#     except Exception as e:
#         print("Failed to send scheduled message:", e)

# 行前提醒
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
    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text=message_text))
        print("Successfully sent reminder message.")
    except Exception as e:
        print("Failed to send reminder message:", e)

# 週末回饋
def feedback_message():
    message_text = """💙 感謝大家參與澳貝客本週末的行程！ 💙

我們由衷感謝您的支持，這次的旅程因為有大家的熱情參與而更加精彩！✨ 為了提供更好的服務，我們誠摯地邀請您分享寶貴的意見與回饋。您的建議對我們來說至關重要，我們將虛心接受，努力提升每一次的旅行體驗。🙏

同時，也誠摯邀請您看看我們接下來的拼團活動！如果有感興趣的行程，歡迎加入，我們將以最熱情的笑容迎接您的參與！😊🌍

🔥 iOutback Agency 澳貝客遊學 週末拼團活動 🔥
📌 報名傳送門 👉 https://forms.gle/3pxQ9kjZMHZJQXd67
"""
    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text=message_text))
        print("Successfully sent feedback message.")
    except Exception as e:
        print("Failed to send feedback message:", e)

# 安排排程時間
# 每日提醒
# scheduler.add_job(scheduled_message, 'cron', hour=8, minute=55)
# scheduler.add_job(scheduled_message, 'cron', hour=9, minute=0)
# scheduler.add_job(scheduled_message, 'cron', hour=9, minute=30)
# scheduler.add_job(scheduled_message, 'cron', hour=10, minute=0)
# scheduler.add_job(scheduled_message, 'cron', hour=10, minute=20)
# scheduler.add_job(scheduled_message, 'cron', hour=10, minute=30)
# scheduler.add_job(scheduled_message, 'cron', hour=10, minute=40)
# scheduler.add_job(scheduled_message, 'cron', hour=10, minute=50)
# scheduler.add_job(scheduled_message, 'cron', hour=21, minute=0)

# 行前提醒
scheduler.add_job(reminder_message, 'cron', day_of_week='wed', hour=12, minute=0)
scheduler.add_job(reminder_message, 'cron', day_of_week='thu', hour=12, minute=0)
scheduler.add_job(reminder_message, 'cron', day_of_week='fri', hour=20, minute=0)
scheduler.add_job(reminder_message, 'cron', day_of_week='sun', hour=20, minute=0)

# 週末回饋
scheduler.add_job(feedback_message, 'cron', day_of_week='sun', hour=20, minute=0)

scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
