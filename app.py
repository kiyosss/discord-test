from flask import Flask, request, jsonify
import nacl.signing
import os
import requests
import threading
import time

app = Flask(__name__)

PUBLIC_KEY = "7ff356b89d1ae3cb67e1eb9ff04ff5017eb743c2c470ae4c12b5d9254e522cc1"
APPLICATION_ID = "1546095227943649380"
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

verify_key = nacl.signing.VerifyKey(bytes.fromhex(PUBLIC_KEY))


# /test コマンドをDiscordに登録
def register_command():
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"

    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "name": "test",
        "description": "テストを実行します"
    }

    response = requests.post(url, headers=headers, json=data)
    print("Command registration:", response.status_code, response.text)


# ボタンを押した後、3回メッセージを送る
def send_messages(application_id, interaction_token):
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"

    for i in range(3):
        time.sleep(1)

        requests.post(
            url,
            json={
                "content": "こんにちは！"
            }
        )


@app.route("/discord", methods=["POST"])
def discord():
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = request.data

    try:
        verify_key.verify(
            timestamp.encode() + body,
            bytes.fromhex(signature)
        )
    except Exception:
        return "invalid request signature", 401

    data = request.json

    # Discordからの接続確認
    if data["type"] == 1:
        return jsonify({"type": 1})

    # /test コマンド
    if data["type"] == 2:
        return jsonify({
            "type": 4,
            "data": {
                "content": "テスト開始！",
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "style": 1,
                                "label": "実行",
                                "custom_id": "hello_button"
                            }
                        ]
                    }
                ]
            }
        })

    # ボタン
    if data["type"] == 3 and data["data"]["custom_id"] == "hello_button":
        token = data["token"]

        threading.Thread(
            target=send_messages,
            args=(APPLICATION_ID, token)
        ).start()

        return jsonify({
            "type": 4,
            "data": {
                "content": "実行しました！"
            }
        })

    return jsonify({
        "type": 4,
        "data": {
            "content": "こんにちは！"
        }
    })


@app.route("/")
def home():
    return "Discord app is running!"


register_command()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
