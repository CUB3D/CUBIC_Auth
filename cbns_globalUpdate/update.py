import redis
import time

redis_server = redis.Redis(host='redis', port=6379, password='')

while True:
    redis_server.publish("channel_device_common", "device_update_status")
    print("Global update done")
    time.sleep(15 * 60)
