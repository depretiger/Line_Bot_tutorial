import os
import sys
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


def filerw(after):
    f = open("mode.txt","w")
    f.write(after)
    f.close()


app = Flask(__name__)

# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

talk = {
        "おこ" : "ごめんなさい",
        "おもしょ" : "おねしょ",
        "おねしょ" : "おもしょ"
}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    f = open("mode.txt")
    mode = f.read()
    f.close()
    
    if text == "モード":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(mode))
        return

    if text == "カウント" or text == "かうんと":
        line_bot_api.reply_message(event.reply_token, TextSendMessage("count on"))
        filerw("count");
        return 

    if text == "コピー" or text == "こぴー":
        line_bot_api.reply_message(event.reply_token, TextSendMessage("copy on"))
        filerw("copy");
        return 

    if text == "おわり":
        line_bot_api.reply_message(event.reply_token, TextSendMessage("finish"))
        filerw("nothing")
        return


    if text in talk:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(talk[text]))
        return
    
    if mode == "count":
        length = len(text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(str(length) + "文字"))
        return

    if mode == "copy":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text))


if __name__ == "__main__":
    app.run()
