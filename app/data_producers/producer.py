from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

# Kafka 설정
KAFKA_BROKER = [
    'kafka.kafka.svc.cluster.local:9092' # :30092'  # docker-compose 외부 실행 시
    # 'kafka-controller-0.kafka-controller-headless.kafka.svc.cluster.local:9092',
    # 'kafka-controller-1.kafka-controller-headless.kafka.svc.cluster.local:9092',
    # 'kafka-controller-2.kafka-controller-headless.kafka.svc.cluster.local:9092',
]
TOPIC = 'user-events'

# Kafka Producer 인스턴스 생성
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 이벤트 종류 정의
event_types = ['login', 'logout', 'purchase', 'click', 'scroll', 'view']

def generate_random_event():
    return {
        "user_id": random.randint(1, 1000),
        "event": random.choice(event_types),
        "timestamp": datetime.utcnow().isoformat()
    }

print("🔁 Kafka에 메시지를 계속 전송합니다. 중단하려면 Ctrl+C 를 누르세요.")

try:
    while True:
        message = generate_random_event()
        producer.send(TOPIC, message)
        print(f"✅ Sent: {message}")
        time.sleep(1)  # 1초 간격으로 전송
except KeyboardInterrupt:
    print("\n⛔ 메시지 전송을 중단합니다.")
finally:
    producer.flush()
    producer.close()
