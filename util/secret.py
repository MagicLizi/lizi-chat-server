import jwt
sk = "qCrbYcu5Z8rGf17mRDjyzzzkX36nKAJ2um53NZXhv2Ur15CcMPEjxPuuZCzVsmon"


def generate_user_token(user_id: int, mobile: str):
    payload = {'user_id': user_id, 'mobile': mobile}
    token = jwt.encode(payload, sk, algorithm='HS256')
    return token


def decode_user_token(token: str):
    try:
        payload = jwt.decode(token, sk, algorithms=["HS256"])
        return payload
    except jwt.exceptions.DecodeError:
        return None

