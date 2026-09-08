from flask import Flask, request, jsonify
import nacl.signing
import os
import requests

app = Flask(__name__)

PUBLIC_KEY = "7ff356b89d1ae3cb67e1eb9ff04ff5017eb743c2c470ae4c12b5d9254e522cc1"
APPLICATION_ID = "1546095227943649380"
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# ==============================
# 送信回数
# ==============================
SEND_COUNT = 1

# 送信間隔（秒）
SEND_INTERVAL = 1

verify_key = nacl.signing.VerifyKey(bytes.fromhex(PUBLIC_KEY))


@app.route("/discord", methods=["POST"])
def discord():

    print("=== DISCORD REQUEST RECEIVED ===", flush=True)

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

            return jsonify({
                "type": 4,
                "data": {
                    "content": "こんにちは！",
                    "allowed_mentions": {
                        "parse": []
                    }
                }
        
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


if __name__ == "__main__":
    print("=== SERVER STARTING ===", flush=True)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
    # register_command()
