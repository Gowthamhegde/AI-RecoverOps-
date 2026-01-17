"""
Redis Client for Caching and Message Queues
"""

import logging
import json
from typing import Optional, Any, List
import aioredis
from config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper with connection management"""
    
    def __init__(self):
        self.redis = None
        self.connected = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis.ping()
            self.connected = True
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("✅ Redis connection closed")
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            if not self.redis:
                return False
            await self.redis.ping()
            return True
        except Exception:
            return False
    
    # Queue operations
    async def lpush(self, key: str, value: str) -> int:
        """Push to left of list"""
        if not self.connected:
            await self.connect()
        return await self.redis.lpush(key, value)
    
    async def rpush(self, key: str, value: str) -> int:
        """Push to right of list"""
        if not self.connected:
            await self.connect()
        return await self.redis.rpush(key, value)
    
    async def lpop(self, key: str) -> Optional[str]:
        """Pop from left of list"""
        if not self.connected:
            await self.connect()
        return await self.redis.lpop(key)
    
    async def rpop(self, key: str) -> Optional[str]:
        """Pop from right of list"""
        if not self.connected:
            await self.connect()
        return await self.redis.rpop(key)
    
    async def llen(self, key: str) -> int:
        """Get list length"""
        if not self.connected:
            await self.connect()
        return await self.redis.llen(key)
    
    # Key-value operations
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set key-value pair"""
        if not self.connected:
            await self.connect()
        return await self.redis.set(key, value, ex=ex)
    
    async def setex(self, key: str, time: int, value: str) -> bool:
        """Set key-value pair with expiration"""
        if not self.connected:
            await self.connect()
        return await self.redis.setex(key, time, value)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self.connected:
            await self.connect()
        return await self.redis.get(key)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        if not self.connected:
            await self.connect()
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.connected:
            await self.connect()
        return bool(await self.redis.exists(key))
    
    async def expire(self, key: str, time: int) -> bool:
        """Set key expiration"""
        if not self.connected:
            await self.connect()
        return await self.redis.expire(key, time)
    
    # Hash operations
    async def hset(self, name: str, key: str, value: str) -> int:
        """Set hash field"""
        if not self.connected:
            await self.connect()
        return await self.redis.hset(name, key, value)
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field"""
        if not self.connected:
            await self.connect()
        return await self.redis.hget(name, key)
    
    async def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        if not self.connected:
            await self.connect()
        return await self.redis.hgetall(name)
    
    # Set operations
    async def sadd(self, name: str, *values: str) -> int:
        """Add to set"""
        if not self.connected:
            await self.connect()
        return await self.redis.sadd(name, *values)
    
    async def smembers(self, name: str) -> set:
        """Get set members"""
        if not self.connected:
            await self.connect()
        return await self.redis.smembers(name)
    
    async def srem(self, name: str, *values: str) -> int:
        """Remove from set"""
        if not self.connected:
            await self.connect()
        return await self.redis.srem(name, *values)
    
    # JSON operations
    async def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set JSON value"""
        json_str = json.dumps(value)
        return await self.set(key, json_str, ex=ex)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value"""
        json_str = await self.get(key)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON for key: {key}")
                return None
        return None
    
    # Pub/Sub operations
    async def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        if not self.connected:
            await self.connect()
        return await self.redis.publish(channel, message)
    
    async def subscribe(self, *channels: str):
        """Subscribe to channels"""
        if not self.connected:
            await self.connect()
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub
    
    # Utility methods
    async def flushdb(self) -> bool:
        """Flush current database"""
        if not self.connected:
            await self.connect()
        return await self.redis.flushdb()
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        if not self.connected:
            await self.connect()
        return await self.redis.keys(pattern)
    
    async def ttl(self, key: str) -> int:
        """Get key time to live"""
        if not self.connected:
            await self.connect()
        return await self.redis.ttl(key)

# Global Redis client instance
redis_client = RedisClient()

async def init_redis():
    """Initialize Redis connection"""
    await redis_client.connect()

async def close_redis():
    """Close Redis connection"""
    await redis_client.disconnect()