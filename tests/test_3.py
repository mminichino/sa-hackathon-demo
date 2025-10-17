import redis
import os

def test_redis_connection():
    """Test connection to a Redis Cloud database"""
    hostname = os.environ.get("REDIS_HOST", "localhost")
    port = os.environ.get("REDIS_PORT", "6379")
    password = os.environ.get("REDIS_PASSWORD")
    
    # Redis Cloud connection configuration
    r = redis.Redis(
        host=hostname,
        port=int(port),
        decode_responses=True,
        password=password,
    )
    
    try:
        # Test connection with PING
        print("🔗 Testing Redis connection...")
        ping_result = r.ping()
        print(f"✅ PING successful: {ping_result}")
        
        # Test basic SET operation
        print("\n📝 Testing SET operation...")
        success = r.set('foo', 'bar')
        print(f"✅ SET 'foo' = 'bar': {success}")
        
        # Test basic GET operation
        print("\n📖 Testing GET operation...")
        result = r.get('foo')
        print(f"✅ GET 'foo': {result}")
        
        # Test database info
        print("\n📊 Database information:")
        db_size = r.dbsize()
        print(f"   Total keys: {db_size}")
        
        info = r.info('server')
        print(f"   Redis version: {info.get('redis_version', 'Unknown')}")
        print(f"   Redis mode: {info.get('redis_mode', 'Unknown')}")
        
        # Test some sample operations
        print("\n🧪 Testing additional operations...")
        
        # Hash operations
        r.hset('user:1001', mapping={
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        })
        user_data = r.hgetall('user:1001')
        print(f"✅ Hash operation - user:1001: {user_data}")
        
        # List operations
        r.lpush('tasks', 'task1', 'task2', 'task3')
        tasks = r.lrange('tasks', 0, -1)
        print(f"✅ List operation - tasks: {tasks}")
        
        # Set operations
        r.sadd('tags', 'redis', 'python', 'cloud')
        tags = r.smembers('tags')
        print(f"✅ Set operation - tags: {tags}")
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"📊 Final key count: {r.dbsize()}")

        assert r.dbsize() == 4

        r.delete('foo')
        r.delete('user:1001')
        r.delete('tasks')
        r.delete('tags')

    except redis.AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        return False
    except redis.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
