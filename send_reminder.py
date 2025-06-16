from linebot import LineBotApi
from linebot.models import TextSendMessage
import os

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def scheduled_message():
    try:
        line_bot_api.push_message(GROUP_ID, TextSendMessage(text='Scheduled reminder: Don’t forget to complete your tasks!'))
        print("Successfully sent scheduled message.")
    except Exception as e:
        print("Failed to send scheduled message:", e)

if __name__ == "__main__":
    scheduled_message()
