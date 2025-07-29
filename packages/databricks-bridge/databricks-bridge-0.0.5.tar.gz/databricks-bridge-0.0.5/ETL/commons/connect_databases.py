import os

from pymongo.mongo_client import MongoClient


class MongoDBConn:
    def __init__(self, env, cluster: str = "", hostname: str = "", db_user: str = "", db_password: str = ""):
        self.env = env
        self.cluster = cluster
        self.hostname = hostname
        self.db_user = db_user
        self.db_password = db_password

    def get_mongodb_connection_uri(self):
        if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
            self.db_user = self.db_user if self.db_user else self.env["dbutils"].secrets.get(scope="atlas_mongodb_secrets", key="db_user")
            self.db_password = self.db_password if self.db_password else self.env["dbutils"].secrets.get(scope="atlas_mongodb_secrets", key="db_password")
            self.cluster = self.cluster if self.cluster else self.env["dbutils"].secrets.get(scope="atlas_mongodb_secrets", key="cluster")
            self.hostname = self.hostname if self.hostname else self.env["dbutils"].secrets.get(scope="atlas_mongodb_secrets", key="hostname")

        uri = f"mongodb+srv://{self.db_user}:{self.db_password}@{self.cluster}.{self.hostname}/?retryWrites=true&w=majority&appName={self.cluster}"
        return uri

    def mongodb_connect(self):
        uri = self.get_mongodb_connection_uri()
        client = MongoClient(uri)
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
            client = None

        return client
