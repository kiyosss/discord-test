from flask import Flask, request, jsonify
import nacl.signing
import time
import threading

app = Flask(__name__)

PUBLIC_KEY = "7ff356b89d1ae3cb67e1eb9ff04ff5017eb743c2c470ae4c12b5d9254e522cc1"
verify_key = nacl.signing.VerifyKey(bytes.fromhex(PUBLIC_KEY))


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

    # ボタンが押された
    if data["type"] == 3:
        threading.Thread(target=send_messages).start()

        return jsonify({
            "type": 4,
            "data": {
                "content": "開始！"
            }
        })

    return jsonify({
        "type": 4,
        "data": {
            "content": "こんにちは！"
        }
    })


def send_messages():
    # 今はテスト用
    # 実際のDiscordへの3回送信処理は次の段階で追加
    for i in range(3):
        time.sleep(1)


@app.route("/")
def home():
    return "Discord app is running!"


app.run(host="0.0.0.0", port=10000)
