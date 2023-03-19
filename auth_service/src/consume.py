import sys

from flask import Flask

from confluent_kafka import KafkaError, KafkaException
from db.config import db, migrate
from kafka.consumer import get_kafka_consumer
from kafka.events import event_registry
from settings import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.db.dsn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate.init_app(app, db)
app.app_context().push()

def consume():
    running = True
    consumer = get_kafka_consumer()

    try:
        consumer.subscribe(list(event_registry.topic_dispatcher.keys()))

        msg_count = 0
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write(
                        "%% %s [%d] reached end at offset %d\n"
                        % (msg.topic(), msg.partition(), msg.offset())
                    )
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                event_registry.topic_dispatcher[msg.topic()].handle(msg)
                msg_count += 1
                if msg_count % 1 == 0:
                    consumer.commit(asynchronous=False)
    finally:
        consumer.close()


if __name__ == "__main__":
    consume()