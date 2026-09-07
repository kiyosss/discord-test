from flask import Flask, request, jsonify
import nacl.signing

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
        return jsonify({
            "type": 4,
            "data": {
                "content": " @everyone
Raid by SOKOTO. join now
ソコト市に参加！https://discord.gg/AZhqNfPYY
https://cdn.discordapp.com/attachments/1507014218074034238/1546085829284466718/bd535427745e4eb191636341c0cbbce4.gif?ex=6a9e8022&is=6a9d2ea2&hm=e5281eaeed7b5d9c727c96e2193335565c3754931c9c6ee186936cdbb892e901&""
            }
        })

    return jsonify({
        "type": 4,
        "data": {
            "content": " @everyone
Raid by SOKOTO. join now
ソコト市に参加！https://discord.gg/AZhqNfPYY
https://cdn.discordapp.com/attachments/1507014218074034238/1546085829284466718/bd535427745e4eb191636341c0cbbce4.gif?ex=6a9e8022&is=6a9d2ea2&hm=e5281eaeed7b5d9c727c96e2193335565c3754931c9c6ee186936cdbb892e901&""
        }
    })

@app.route("/")
def home():
    return "Discord app is running!"

app.run(host="0.0.0.0", port=10000)
