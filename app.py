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


def register_command():
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN is not set")
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

    try:
        response = requests.put(
            url,
            headers=headers,
            json=commands,
            timeout=10
        )

        print("COMMAND REGISTRATION STATUS:", response.status_code)
        print("COMMAND REGISTRATION RESPONSE:", response.text)

    except Exception as e:
        print("COMMAND REGISTRATION ERROR:", repr(e))


def send_messages(application_id, interaction_token):

    print("SEND_MESSAGES START")

    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"

    for i in range(3):

        print("SENDING MESSAGE:", i + 1)

        try:
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

            print("MESSAGE STATUS:", response.status_code)
            print("MESSAGE RESPONSE:", response.text)

        except Exception as e:
            print("SEND ERROR:", repr(e))

        if i < 2:
            time.sleep(1)

    print("SEND_MESSAGES END")


@app.route("/discord", methods=["POST"])
def discord():

    print("DISCORD REQUEST RECEIVED")

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
        print("SIGNATURE ERROR:", repr(e))
        return "Invalid request signature", 401

    data = request.get_json()

    if data.get("type") == 1:
        print("PING RECEIVED")
        return jsonify({"type": 1})

    if (
        data.get("type") == 2
        and data.get("data", {}).get("name") == "test"
    ):
        print("TEST COMMAND RECEIVED")

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
                ],
                "allowed_mentions": {
                    "parse": []
                }
            }
        })

    if data.get("type") == 3:

        custom_id = data.get("data", {}).get("custom_id")

        print("BUTTON CUSTOM ID:", custom_id)

        if custom_id == "hello_button":

            print("BUTTON CLICKED")

            threading.Thread(
                target=send_messages,
                args=(
                    APPLICATION_ID,
                    data["token"]
                )
            ).start()

            return jsonify({"type": 6})

    return jsonify({
        "type": 4,
        "data": {
            "content": "テスト用の応答です。",
            "allowed_mentions": {
                "parse": []
            }
        }
    })


@app.route("/", methods=["GET"])
def home():
    return "Discord app is running!"


# 1015対策
# 起動時のコマンド登録は停止中
# register_command()
