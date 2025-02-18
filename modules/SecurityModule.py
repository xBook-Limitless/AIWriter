import time

class KeyManager:
    _CACHE_TTL = 300  # 5分钟缓存
    
    @classmethod
    def get_key(cls):
        """带缓存的密钥获取"""
        if time.time() - cls._last_fetch < cls._CACHE_TTL:
            return cls._cached_key
        # 重新获取密钥逻辑... 