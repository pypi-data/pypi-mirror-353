# Databricks notebook source
from typing import Union
import os
import json
import boto3

from ETL.ediscovery_bo_chat_pull.app import execute_query, decrypt_chat_messages, EncryptedChatMessage

bucket_name = os.environ.get('BUCKET')
s3 = boto3.resource('s3', region_name="eu-west-2")
client_ids = [
    "cf56dd91-0dd6-4ddb-9423-dbf1c939567a", "9c03b14e-b870-4ec8-8a97-f0a538043de5",
    "efeeab3b-0ef8-44bd-bb68-c38830d54415", "046da7c1-4e42-4593-9364-5d1b2443bb50",
    "94e2e9d3-b36f-4222-a249-24300d993e58", "6775506a-20de-4886-8bcb-9ec2a93c0124",
    "afa3df36-d886-4248-8c5c-12619a494b1e", "85f042c8-7b3d-4a7a-826b-feedd6fd9a7b",
    "f9f81705-4eeb-4593-9005-11312805aa36", "cb070cfe-45b9-4b70-b91e-8a459c88d54e",
]

chat_query = f"""
    SELECT id, channel_id, author_id, came_at, content, content_type FROM chat_v2.message
    WHERE channel_id in ({",".join(["'" + _id + "'" for _id in client_ids])})
    ORDER BY came_at DESC;
"""


def pull_chat():
    result_set = execute_query(chat_query)
    encrypted_chat_messages = [EncryptedChatMessage(result) for result in result_set]
    chat_messages = decrypt_chat_messages(encrypted_chat_messages)
    chat_messages_dict_list = [
        {
            "id": chat.id, "channel_id": chat.channel_id, "author_id": chat.author.id if chat.author else None,
            "author_name": chat.author.name if chat.author else None,
            "author_user_type": chat.author.user_type if chat.author else None,
            "author_class": chat.author.__class__.__name__, "came_at": chat.came_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "content": chat.content, "content_type": chat.content_type
        } for chat in chat_messages
    ]
    return chat_messages_dict_list


def partition_data(chat_messages_dict_list: list):
    data = {}

    for el in chat_messages_dict_list:
        msg_date = el["came_at"].split(" ")[0]
        channel_id = el["channel_id"]

        if msg_date not in data.keys():
            data[msg_date] = {}

        if channel_id not in data[msg_date].keys():
            data[msg_date][channel_id] = [el]
        else:
            data[msg_date][channel_id].append(el)

    return data


def write_data_to_s3(payload: Union[dict, list], channel_id: str, date_partition: str):
    s3_path = f'landing/ai-soft-facts/chat/{date_partition}/{channel_id}.json'
    object = s3.Object(bucket_name, s3_path)
    object.put(Body=json.dumps(payload).encode())


def run_chat_pull():
    chat_messages_dict_list = pull_chat()
    data = partition_data(chat_messages_dict_list)
    for _date, val in data.items():
        date_partition = _date.replace("-", "/")
        for channel_id, dict_list in val.items():
            write_data_to_s3(payload=dict_list, channel_id=channel_id, date_partition=date_partition)

        print(f"uploaded to {_date} chat files to s3")


if __name__ == "__main__":
    run_chat_pull()
