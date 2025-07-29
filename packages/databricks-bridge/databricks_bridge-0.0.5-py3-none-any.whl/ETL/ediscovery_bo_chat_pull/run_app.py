# Databricks notebook source
import time
from datetime import datetime, timedelta

from ETL.ediscovery_bo_chat_pull.app import execute_pull_steps


def run_app():
    ids_n_dates = [
        {"id": "88eb87a5-36ea-42df-969b-fe50994cab94", "date": "2024-04-03"},
        {"id": "47a95f82-66ec-46a7-b31c-37297e7560b7", "date": "2023-07-19"},
        {"id": "3eeb0111-26a5-47a4-9b2f-fb7f5fe83bca", "date": "2024-05-02"},
        {"id": "3eeb0111-26a5-47a4-9b2f-fb7f5fe83bca", "date": "2023-06-19"},
        {"id": "c98190b0-efe9-4c71-ab12-8110ba91032c", "date": "2024-05-24"},
        {"id": "2fb994ca-0a64-441a-a56d-3fb5a8ce329d", "date": "2023-07-11"},
        {"id": "58a40a06-798a-4c99-80d4-b7a26f321e15", "date": "2023-08-29"},
        {"id": "8ecb41e4-c035-4042-9fa3-b41624dd5caa", "date": "2024-02-01"},
        {"id": "8ecb41e4-c035-4042-9fa3-b41624dd5caa", "date": "2024-02-01"},
        {"id": "20425198-75c6-4fe3-96b8-30ae55e5a25f", "date": "2023-11-23"},
        {"id": "cfae51ac-5af0-4ce7-84de-bfc1d852e9e6", "date": "2024-01-17"},
        {"id": "bc420850-1002-40c8-9b79-1ea07842a2dd", "date": "2024-05-08"},
        {"id": "b13d2700-d1a4-4952-9470-4f287767611f", "date": "2023-11-06"},
        {"id": "18b8adda-1a0e-400b-b01c-5d817d3e164a", "date": "2023-08-21"},
        {"id": "d4501973-d421-49b7-b8ae-bf191c4ce9c1", "date": "2023-12-12"},
        {"id": "487a7539-987a-4347-83a0-65ef10265603", "date": "2024-02-21"},
        {"id": "7a0ad31e-0488-49a7-80a6-bdce7d5b35fe", "date": "2024-04-16"},
        {"id": "c6bad6f0-f1ef-4efc-80b3-afac3f4a53d1", "date": "2023-06-19"},
        {"id": "50bc48f9-d5ce-4b47-89de-6d2dc1e54d9d", "date": "2023-08-01"},
        {"id": "74fac493-126e-4e24-afae-6d1aed1d8dae", "date": "2024-05-24"},
        {"id": "970da146-04d0-4589-b4de-1975beeacf58", "date": "2024-06-26"},
        {"id": "d81c8e14-9468-4d78-afa9-416ae3d9f87f", "date": "2024-06-11"},
        {"id": "54316ccf-4c12-4070-9445-f22994174d1d", "date": "2024-07-22"},
        {"id": "7973fb1a-ecf1-42b2-a8bf-8a9e8cc7217e", "date": "2023-07-20"},
        {"id": "48f6d62a-e3d6-4ea6-87f4-f7f95d609416", "date": "2023-10-31"},
    ]

    for el in ids_n_dates:
        BO_PROFILE_ID = el["id"]
        FROM_DATE = (datetime.strptime(el["date"], "%Y-%m-%d") + timedelta(days=-15)).strftime("%Y-%m-%d")
        TO_DATE = (datetime.strptime(el["date"], "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")
        execute_pull_steps(profile_id=BO_PROFILE_ID, from_date=FROM_DATE, to_date=TO_DATE)

        time.sleep(2)


if __name__ == "__main__":
    run_app()

# COMMAND ----------
# MAGIC %run ./chat_messages_export
