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

SEND_COUNT = 2
SEND_INTERVAL = 1

verify_key = nacl.signing.VerifyKey(bytes.fromhex(PUBLIC_KEY))


def register_command():
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN is not set", flush=True)
        return

    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"

    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }

    commands = [
        {
            "name": "test",
            "description": "テストを実行します",
            "integration_types": [1],
            "contexts": [0, 1, 2]
        }
    ]

    response = requests.put(
        url,
        headers=headers,
        json=commands,
        timeout=10
    )

    print("COMMAND REGISTRATION STATUS:", response.status_code, flush=True)
    print("COMMAND REGISTRATION RESPONSE:", response.text, flush=True)


def send_messages(application_id, interaction_token):
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"

    for i in range(SEND_COUNT):
        response = requests.post(
            url,
            json={
                "content": "こんにちは！",
                "allowed_mentions": {
                    "parse": []
                }
            },
            timeout=10
        )

        print(
            f"MESSAGE {i + 1}/{SEND_COUNT} STATUS:",
            response.status_code,
            flush=True
        )

        print("MESSAGE RESPONSE:", response.text, flush=True)
        print("RETRY AFTER:", response.headers.get("Retry-After"), flush=True)

        if i < SEND_COUNT - 1:
            time.sleep(SEND_INTERVAL)


@app.route("/discord", methods=["POST"])
def discord():

    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = request.data

    if not signature or not timestamp:
        return "Bad Request", 401

    try:
        verify_key.verify(
            timestamp.encode() + body,
            bytes.fromhex(signature)
        )
    except Exception as e:
        print("INVALID SIGNATURE:", e, flush=True)
        return "Invalid request signature", 401

    data = request.get_json()

    print("RECEIVED TYPE:", data.get("type"), flush=True)

    # Discordの接続確認
    if data.get("type") == 1:
        return jsonify({
            "type": 1
        })

    # /test
    if data.get("type") == 2 and data.get("data", {}).get("name") == "test":

        return jsonify({
            "type": 4,
            "data": {
                "content": "テスト開始！",
                "flags": 64,
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

    # 実行ボタン
    if data.get("type") == 3:

        custom_id = data.get("data", {}).get("custom_id")

        print("CUSTOM ID:", custom_id, flush=True)

        if custom_id == "hello_button":

            print(
                f"=== SENDING {SEND_COUNT} MESSAGE(S) ===",
                flush=True
            )

            threading.Thread(
                target=send_messages,
                args=(APPLICATION_ID, data["token"]),
                daemon=True
            ).start()

            return jsonify({
                "type": 6
            })

    return jsonify({
        "type": 4,
        "data": {
            "content": "不明な操作です。",
            "allowed_mentions": {
                "parse": []
            }
        }
    })


@app.route("/", methods=["GET"])
def home():
    return "Discord app is running!"


# 429 / Error 1015対策
# register_command()


if __name__ == "__main__":
    print("=== SERVER STARTING ===", flush=True)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
