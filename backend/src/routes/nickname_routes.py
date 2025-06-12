from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
import logging
import random

from models.session_data import SessionData

from clients.wristband_client import WristbandApiClient

router = APIRouter()
logger = logging.getLogger(__name__)
wristband_client = WristbandApiClient()

# Simple lists for generating nicknames
ADJECTIVES = [
    "Big", "Little", "Fat", "Thin", "Crazy", "Mad", "Wild", "Smooth", 
    "Sharp", "Lucky", "Fast", "Slow", "Cold", "Hot", "Wise", "Young",
    "Deadly", "Silent", "Fierce", "Slick", "Tough", "Clever", "Bold", "Sneaky",
    "Quick", "Heavy", "Silver", "Golden", "Dark", "Bright", "Iron", "Steel"
]
NICKNAMES = [
    "Tony", "Sal", "Vinny", "Joey", "Frankie", "Rocco", "Gino", "Marco",
    "Carlo", "Nico", "Luca", "Dante", "Angelo", "Bruno", "Rico", "Vito",
    "Jimmy", "Sophia", "Isabella", "Maria", "Lucia", "Carmela", "Rosa", "Bianca",
    "Valentina", "Francesca", "Stella", "Gabriella", "Adriana", "Elena", "Caterina", "Alessandra",
    "Salvatore", "Giovanni", "Antonio", "Giuseppe", "Matteo", "Lorenzo", "Leonardo", "Francesco",
    "Alessandro", "Stefano", "Roberto", "Michele", "Fabio", "Domenico", "Emilio", "Sergio",
    "Giulia", "Chiara", "Federica", "Martina", "Silvia", "Paola", "Laura", "Anna",
    "Cristina", "Monica", "Simona", "Valeria", "Claudia", "Barbara", "Teresa", "Giovanna"
]
TITLES = [
    "The Bull", "The Fish", "The Hammer", "The Knife", "The Shadow",
    "The Snake", "The Wolf", "The Fox", "The Eagle", "The Lion",
    "The Tiger", "The Bear", "The Shark", "The Cat", "The Dog", "The Rat",
    "The Boss", "The Ghost", "The Blade", "The Ice", "The Fire", "The Rock",
    "The Machine", "The Storm", "The Thunder", "The Lightning", "The Tornado", "The Hurricane",
    "The Bullet", "The Cannon", "The Bomb", "The Enforcer"
]


@router.get('')
def get_nickname(request: Request) -> Response:
    try:
        # Get the Wristband user's existing nickaname
        session_data: SessionData = request.state.session
        nickname: str = wristband_client.get_user_nickname(session_data.user_id, session_data.access_token)
        return JSONResponse(content={ "nickname": nickname })
    except Exception as e:
        logger.exception(f"Unexpected Get Nickname Endpoint error: {str(e)}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post('')
def generate_new_nickname(request: Request) -> Response:
    try:
        nickname: str = random.choice([
            f"{random.choice(ADJECTIVES)} {random.choice(NICKNAMES)}",
            f"{random.choice(NICKNAMES)} {random.choice(TITLES)}",
            f"{random.choice(ADJECTIVES)} {random.choice(NICKNAMES)} {random.choice(TITLES)}"
        ])

        # Update the Wristband user with the new nickaname
        session_data: SessionData = request.state.session
        wristband_client.update_user_nickname(session_data.user_id, nickname, session_data.access_token)
        return JSONResponse(content={ "nickname": nickname })
    except Exception as e:
        logger.exception(f"Unexpected Generate New Nickname Endpoint error: {str(e)}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
