from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# 환경 변수 불러오기
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
uri = f"mongodb+srv://{db_username}:{db_password}@{db_host}/?retryWrites=true&w=majority&appName=Cluster0"

print(f"::: 디비URI [{uri}]")

client = MongoClient(uri)
print("::: 디비연결 성공")
mimi = client[db_name]

memberCollection = mimi["member"]
eventCollection = mimi["event"]
