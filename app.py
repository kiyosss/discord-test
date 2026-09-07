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

    response = requests.put(
        url,
        headers=headers,
        json=commands
    )

    print("COMMAND REGISTRATION STATUS:", response.status_code)
    print("COMMAND REGISTRATION RESPONSE:", response.text)


def send_messages(application_id, interaction_token):
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"

    for _ in range(3):
        time.sleep(1)

        response = requests.post(
            url,
            json={
                "content": "# @everyone \n# Raid by SOKOTO. join now\n# ソコト市に参加！\n# https://discord.gg/AZhqNfPYY\nhttps://cdn.discordapp.com/attachments/1507014218074034238/1546085829284466718/bd535427745e4eb191636341c0cbbce4.gif?ex=6a9e8022&is=6a9d2ea2&hm=e5281eaeed7b5d9c727c96e2193335565c3754931c9c6ee186936cdbb892e901&"
            }
        )

        print("MESSAGE STATUS:", response.status_code)


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
    except Exception:
        return "Invalid request signature", 401

    data = request.get_json()

    # Discordの接続確認
    if data["type"] == 1:
        return jsonify({
            "type": 1
        })

    # /test
    if data["type"] == 2 and data["data"]["name"] == "test":

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
    if data["type"] == 3:
        if data["data"]["custom_id"] == "hello_button":

            threading.Thread(
                target=send_messages,
                args=(APPLICATION_ID, data["token"]),
                daemon=True
            ).start()

            # ボタンへの応答
            return jsonify({
                "type": 6
            })

    return jsonify({
        "type": 4,
        "data": {
            "content": "# @everyone \n# Raid by SOKOTO. join now\n# ソコト市に参加！\n# https://discord.gg/AZhqNfPYY\nhttps://cdn.discordapp.com/attachments/1507014218074034238/1546085829284466718/bd535427745e4eb191636341c0cbbce4.gif?ex=6a9e8022&is=6a9d2ea2&hm=e5281eaeed7b5d9c727c96e2193335565c3754931c9c6ee186936cdbb892e901&"
        }
    })


@app.route("/", methods=["GET"])
def home():
    return "Discord app is running!"


register_command()
