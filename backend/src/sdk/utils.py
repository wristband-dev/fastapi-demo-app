from fastapi import Request
import json

async def debug_request(request: Request, call_next):
    print("\n=== Incoming Request ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print("Headers:")
    for name, value in request.headers.items():
        print(f"  {name}: {value}")
    body: bytes = await request.body()
    if body:
        try:
            body_json = json.loads(body)
            print("Body:")
            print(json.dumps(body_json, indent=2))
        except:
            print(f"Body: {body.decode()}")
    print("=====================\n")
    
    response = await call_next(request)
    return response


def to_bool(env_val: str) -> bool:
        return env_val.strip().lower() in ["true", "1", "yes"]

