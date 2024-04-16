import asyncio, concurrent.futures, discord, hashlib, json, os, psutil, random, requests, string, subprocess, threading, time, queue
from threading import Thread
from flask import Flask, request, jsonify
from datetime import datetime
from cryptography.fernet import Fernet

# Only for the public
import keys

BOT_TOKEN = keys.BOT_TOKEN
BOT_INVITE = keys.BOT_INVITE
DISCORD_UPLOAD_CHANNEL_ID = keys.DISCORD_UPLOAD_CHANNEL_ID
SERVER_PASSWORD = keys.SERVER_PASSWORD
STAGE_WEBHOOK_URL = keys.WEBHOOK
UPLOAD_FOLDER = 'stages'
ALLOWED_EXTENSIONS = {'cw', 'json'}
SERVER_IP = "127.0.0.1"
SERVER_PORT = 14984
MODERATOR_TEAM = ["795013781607546931", "1102029166850867230", "1185758698975531099", "801458646914695218", "1142952460508483696"]
BETA_TESTERS = MODERATOR_TEAM

with open("database.json", "r") as db:
    DATABASE = json.loads(db.read())

print(DATABASE)

if not DATABASE:
    DATABASE = {
        "stages": [],
        "accounts": [
            {
                "id": 1,
                "username": "Server",
                "password": "123456",
                "discordid": "",
                "uploads": [],
                "banned": False
            }
        ],
        "sessions": []
    }

def webserver(): # Poder minimizar el código del servidor en el editor
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    def generate_id():
        id = ''
        for _ in range(4): # 1-2-3-4
            id += ''.join(random.choices(string.ascii_letters + string.digits, k=4)) # k= 1234-
            id += '-'
        return id[:-1].upper()  # Eliminar el último guion y hacer mayúscula
