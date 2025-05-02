import json
from datetime import datetime

def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"time": datetime.utcnow().isoformat() + "Z"})
    }
