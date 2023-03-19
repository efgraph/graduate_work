import os
from functools import lru_cache

from confluent_kafka.cimpl import Consumer


@lru_cache()
def get_kafka_consumer() -> Consumer:
    conf = {
        "bootstrap.servers": f"{os.environ['KAFKA_HOST']}:{os.environ['KAFKA_PORT']}",
        "group.id": "user_subscription_group",
        "auto.offset.reset": "smallest",
        "enable.auto.commit": False,
    }

    return Consumer(conf)
