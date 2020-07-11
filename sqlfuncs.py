from getstats import *
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
port = os.getenv("port")
database = os.getenv("database")

conn = psycopg2.connect(user=user,password=password,host=host,port=port,database=database)
cur = conn.cursor()

stats = getStats(playerURL("ironrok",'iron'))

print(stats)
