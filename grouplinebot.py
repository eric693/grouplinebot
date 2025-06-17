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

# 觸發語機制狀態追蹤
trigger_states = {
    'x10': {
        'active': False,
        'member_count': 0,
        'message_count': 0,
        'welcome_threshold': 3,  # 每3人入群發歡迎語
        'message_threshold': 3   # 發言3次後每個進來都發言
    },
    'x20': {
        'active': False,
        'member_count': 0,
        'message_count': 0,
        'welcome_threshold': 4,  # 每4人入群發歡迎語
        'message_threshold': 4   # 發言4次後每個進來都發言
    },
    'x30': {
        'active': False,
        'member_count': 0,
        'message_count': 0,
        'welcome_threshold': 5,  # 每5人入群發歡迎語
        'message_threshold': 5   # 發言5次後每個進來都發言
    }
}

def get_active_trigger():
    """取得目前啟動的觸發語模式"""
    for mode, state in trigger_states.items():
        if state['active']:
            return mode, state
    return None, None

def reset_all_triggers():
    """重置所有觸發語狀態"""
    for state in trigger_states.values():
        state['active'] = False
        state['member_count'] = 0
        state['message_count'] = 0

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
    
    # 檢查是否有啟動的觸發語模式
    active_mode, active_state = get_active_trigger()
    
    if active_state:
        # 增加入群人數計數
        active_state['member_count'] += 1
        print(f"[{active_mode}] Member joined. Count: {active_state['member_count']}")
        
        # 檢查是否達到歡迎語門檻或已達到發言門檻
        should_welcome = False
        
        if active_state['message_count'] >= active_state['message_threshold']:
            # 已達到發言門檻，每個進來都發歡迎語
            should_welcome = True
            print(f"[{active_mode}] Welcome every member (message threshold reached)")
        elif active_state['member_count'] >= active_state['welcome_threshold']:
            # 達到入群人數門檻
            should_welcome = True
            active_state['member_count'] = 0  # 重置計數
            print(f"[{active_mode}] Welcome threshold reached, resetting count")
        
        if should_welcome:
            if now - last_welcome_time >= WELCOME_COOLDOWN:
                send_welcome_message(event.reply_token)
                last_welcome_time = now
            else:
                print("Skip sending welcome message due to cooldown.")
    else:
        # 沒有啟動觸發語模式，使用一般歡迎語
        if now - last_welcome_time >= WELCOME_COOLDOWN:
            send_welcome_message(event.reply_token)
            last_welcome_time = now
        else:
            print("Skip sending welcome message due to cooldown.")

# 成員離開事件處理 (退群不計算)
@handler.add(MemberLeftEvent)
def handle_member_left(event):
    print("Member left - no action taken (as per requirement)")

def send_welcome_message(reply_token):
    """發送歡迎訊息"""
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
    line_bot_api.reply_message(reply_token, TextSendMessage(text=welcome_text))

# 訊息事件處理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.type == 'group':
        print("Current Group ID:", event.source.group_id)
    
    user_message = event.message.text.strip()
    
    # 檢查觸發語
    if user_message == "喵x10":
        reset_all_triggers()
        trigger_states['x10']['active'] = True
        reply_text = "🐱 觸發語 x10 已啟動！\n• 每3人入群發歡迎語一次\n• 發言3次後，每個進來的都發歡迎語"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print("Activated trigger mode: x10")
        return
    
    elif user_message == "喵x20":
        reset_all_triggers()
        trigger_states['x20']['active'] = True
        reply_text = "🐱 觸發語 x20 已啟動！\n• 每4人入群發歡迎語一次\n• 發言4次後，每個進來的都發歡迎語"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print("Activated trigger mode: x20")
        return
    
    elif user_message == "喵x30":
        reset_all_triggers()
        trigger_states['x30']['active'] = True
        reply_text = "🐱 觸發語 x30 已啟動！\n• 每5人入群發歡迎語一次\n• 發言5次後，每個進來的都發歡迎語"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print("Activated trigger mode: x30")
        return
    
    elif user_message == "關閉觸發語" or user_message == "停止觸發語":
        reset_all_triggers()
        reply_text = "🔕 所有觸發語模式已關閉，恢復正常運作"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print("All trigger modes deactivated")
        return
    
    elif user_message == "狀態查詢" or user_message == "觸發語狀態":
        active_mode, active_state = get_active_trigger()
        if active_state:
            status_text = f"""📊 當前觸發語狀態：{active_mode}

👥 入群人數計數：{active_state['member_count']}/{active_state['welcome_threshold']}
💬 發言次數計數：{active_state['message_count']}/{active_state['message_threshold']}

設定：
• 每{active_state['welcome_threshold']}人入群發歡迎語
• 發言{active_state['message_threshold']}次後每個進來都發歡迎語"""
        else:
            status_text = "📊 目前沒有啟動任何觸發語模式"
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=status_text))
        return
    
    # 如果有啟動的觸發語模式，增加發言計數
    active_mode, active_state = get_active_trigger()
    if active_state:
        active_state['message_count'] += 1
        print(f"[{active_mode}] Message count: {active_state['message_count']}/{active_state['message_threshold']}")

# 排程初始化
scheduler = BackgroundScheduler()

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