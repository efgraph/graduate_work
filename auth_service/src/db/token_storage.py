from datetime import timedelta
from typing import Optional

from redis import StrictRedis


class TokenStorage:
    def __init__(self, redis_host: str, redis_port: int) -> None:
        self.redis = StrictRedis(host=redis_host, port=redis_port, db=0)

    def get_value(self, key: str):
        return self.redis.get(key)

    def set_value(self, key: str, token_value: str, time_to_leave: Optional[timedelta] = None) -> None:
        self.redis.set(key, token_value, ex=time_to_leave)
