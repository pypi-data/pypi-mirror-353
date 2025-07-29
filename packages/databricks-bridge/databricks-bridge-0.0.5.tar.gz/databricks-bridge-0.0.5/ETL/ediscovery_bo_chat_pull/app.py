import csv
import datetime
import json
import logging
import os
from abc import ABC
from typing import Dict
from typing import List

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# BEFORE RUNNING THIS SCRIPT, READ THE README


class DecryptPayload:
    text: str
    salt: str

    def __init__(self, text, salt):
        self.text = text
        self.salt = salt


def decrypt_multiple(decrypt_payloads: Dict[str, DecryptPayload]) -> Dict[str, str]:
    data = {
        payload_id: {'data': payload.text, 'salt': payload.salt, 'dataType': 'string'}
        for payload_id, payload in decrypt_payloads.items()
    }

    for payload_id, payload in decrypt_payloads.items():
        data[payload_id] = {
            'data': payload.text,
            'salt': payload.salt,
            'dataType': 'string'
        }

    response = requests.post(
        url=MS_CRYPTO_ENDPOINT,
        data=json.dumps(data),
        headers={
            'Content-Type': 'application/json'
        }
    )
    response_body = json.loads(response.text)

    return {key: value['data'] for key, value in response_body.items()}


class User(ABC):
    id: str
    name: str
    user_type: str

    def __init__(self, id, name, user_type):
        self.id = id
        self.name = name
        self.user_type = user_type

    def __str__(self):
        return f"{self.user_type}: {self.name}"


class Adviser(User):
    def __init__(self, result):
        super().__init__(
            id=result['id'],
            name=result['first_name'] + ' ' + result['last_name'],
            user_type='YTREE'
        )


class EncryptedClient:
    id: str
    encrypted_name: str

    def __init__(self, result):
        self.id = result['id']
        self.encrypted_name = result['name']


class Client(User):
    def __init__(self, id, name):
        super().__init__(
            id=id,
            name=name,
            user_type='CLIENT'
        )


def execute_query(query):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def get_advisers():
    result_set = execute_query("SELECT * FROM profiles.bo_user")
    return [Adviser(result) for result in result_set]


def get_clients():
    result_set = execute_query("SELECT * FROM profiles.client_user")
    return [EncryptedClient(result) for result in result_set]


def decrypt_clients(encrypted_clients: List[EncryptedClient]) -> List[Client]:
    decrypt_payloads = []
    decrypted_payloads = decrypt_multiple(
        {
            client.id: DecryptPayload(text=client.encrypted_name, salt=client.id)
            for client in encrypted_clients
        }
    )
    return [Client(id=key, name=value) for key, value in decrypted_payloads.items()]


class EncryptedChatMessage:
    id: str
    channel_id: str
    author_id: str
    came_at: str
    encrypted_content: str
    content_type: str

    def __init__(self, result):
        self.id = result['id']
        self.channel_id = result["channel_id"]
        self.author_id = result['author_id']
        self.came_at = result['came_at']
        self.encrypted_content = result['content']
        self.content_type = result['content_type']


class ChatMessage:
    id: str
    channel_id: str
    author: str
    came_at: str
    content: str
    content_type: str

    def __init__(self, id, channel_id, author, came_at, content, content_type):
        self.id = id
        self.channel_id = channel_id
        self.author = author
        self.came_at = came_at
        self.content = content
        self.content_type = content_type


def get_chat_messages(query: str):
    result_set = execute_query(query)
    return [EncryptedChatMessage(result) for result in result_set]


def decrypt_chat_messages(encrypted_chat_messages: List[EncryptedChatMessage]) -> List[ChatMessage]:
    encrypted_chat_messages_by_id = {
        message.id: message
        for message in encrypted_chat_messages
    }
    decrypt_payloads = {
        message.id: DecryptPayload(text=message.encrypted_content, salt=None)
        for message in encrypted_chat_messages
    }
    decrypted_payloads = decrypt_multiple(decrypt_payloads)
    return [
        ChatMessage(
            id=id,
            channel_id=encrypted_message.channel_id,
            author=users_by_id.get(encrypted_message.author_id),
            came_at=encrypted_message.came_at,
            content_type=encrypted_message.content_type,
            content=decrypted_payloads[id]
        )
        for id, encrypted_message in encrypted_chat_messages_by_id.items()
    ]


def get_connection():
    connection = psycopg2.connect(DB_CREDS)
    connection.set_session(readonly=True, autocommit=False)
    logger.info(f"Successfully connected to the database '{DB_NAME}' on host '{DB_HOST}'.")
    return connection

# Logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

load_dotenv()

# Load ENV vars
DB_USER = os.getenv('RDS_USERNAME')
DB_PASSWORD = os.getenv('RDS_PASSWORD')

DB_HOST = os.getenv('RDS_HOST')
DB_NAME = os.getenv('RDS_DATABASE')

MS_CRYPTO_URL = os.getenv('MS_CRYPTO_URL')
MS_CRYPTO_ENDPOINT = f"{MS_CRYPTO_URL}/v1/decrypt"

# Establish DB connection
logger.info(f"Connecting to the database '{DB_NAME}' on host '{DB_HOST}'...")
DB_CREDS=f"dbname='{DB_NAME}' " \
         f"user='{DB_USER}' " \
         f"host='{DB_HOST}' " \
         f"password='{DB_PASSWORD}'"
# connection = psycopg2.connect(DB_CREDS)
# connection.set_session(readonly=True, autocommit=False)
logger.info(f"Successfully connected to the database '{DB_NAME}' on host '{DB_HOST}'.")

# Get advisers from DB
logging.info("Getting advisers from DB...")
advisers: List[Adviser] = get_advisers()
logging.info(f"Got {len(advisers)} advisers from DB.")

# Get clients from DB
logging.info("Getting clients from DB...")
encrypted_clients: List[EncryptedClient] = get_clients()
logging.info(f"Got {len(encrypted_clients)} clients with encrypted names from DB")

# Decrypt client names
logging.info(f"Decrypting names for {len(encrypted_clients)} clients...")
clients: List[Client] = decrypt_clients(encrypted_clients)
logging.info(f"Decrypted names for {len(encrypted_clients)} clients.")

# Both - Advisers and Clients - are users who can send messages in the chat.
users: List[User] = advisers + clients
users_by_id = {
    user.id: user
    for user in users
}

parent_dir = "/dbfs/FileStore/etl_files/ediscovery_bo_chat_pull_export"


def get_chat_query(profile_id: str, from_date: str, to_date: str):
    return f"""
        SELECT id, channel_id, author_id, came_at, content, content_type
        FROM chat_v2.message
        WHERE came_at >= '{from_date}' and came_at <= '{to_date if to_date else 'current_date'}'
          AND channel_id = '{profile_id}'
        ORDER BY came_at DESC
    """


def execute_pull_steps(profile_id: str, from_date: str, to_date: str):
    # Get chat messages with encrypted content
    logging.info(f"Getting encrypted chat messages for the Back Office Profile with ID '{profile_id}'...")
    query = get_chat_query(profile_id=profile_id, from_date=from_date, to_date=to_date)
    encrypted_chat_messages = get_chat_messages(query)
    logging.info(f"Got {len(encrypted_chat_messages)} chat messages with encrypted content.")

    # Decrypt chat message content
    logging.info(f"Decrypting content for {len(encrypted_chat_messages)} chat messages...")
    chat_messages = decrypt_chat_messages(encrypted_chat_messages)
    logging.info(f"Decrypted content for {len(encrypted_chat_messages)} chat messages.")

    # Create and populate CSV file
    file_name = f"{parent_dir}/{datetime.date.today().isoformat()} ({from_date}_{to_date}) - Chat Dump for Profile {profile_id}.csv"

    logging.info(f"Creating a file named '{file_name}' and populating it with decrypted chat messages...")
    with open(file=file_name, mode="w+") as file:
        csv_file = csv.writer(file)
        csv_file.writerow(["Timestamp", "Author", "Content Type", "Content"])
        for chat_message in chat_messages:
            csv_file.writerow([chat_message.came_at, chat_message.author, chat_message.content_type, chat_message.content])
    logging.info(f"Successfully created and populated a file called '{file_name}'")
