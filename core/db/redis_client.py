from redis.asyncio import Redis

# Initialize the Redis client
redis_client = Redis(host='localhost', port=6379, db=0)