import requests
import json
import datetime

try:
    res = requests.get("http://127.0.0.1:8000/api/v1/attendance")
    data = res.json()
    if len(data) > 0:
        # Get the LAST record (most recent) to see current server behavior
        last = data[0] # Sorted by timestamp desc in backend
        print("Latest Record Timestamp:", last['timestamp'])
        print("System Time Now:", datetime.datetime.now())
except Exception as e:
    print(e)
