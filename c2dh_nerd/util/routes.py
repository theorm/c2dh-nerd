import json

json_dumps = lambda x: json.dumps(x, default=lambda o: {k: v for k, v in o.__dict__.items() if v is not None})
