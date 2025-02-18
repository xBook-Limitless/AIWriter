import jwt
from datetime import datetime, timedelta
import os

JWT_SECRET = os.getenv('APP_JWT_SECRET', 'your_fallback_secret')

def generate_jwt_token(device_id: str) -> str:
    """生成短期访问令牌"""
    payload = {
        "iss": "novel_writer",
        "sub": device_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "scopes": ["api:generate"]
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def validate_token(token: str) -> bool:
    """验证JWT令牌有效性"""
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return datetime.utcnow() < datetime.fromtimestamp(decoded["exp"])
    except jwt.PyJWTError:
        return False

# 示例JWT生成（有效期1小时）
token = generate_jwt_token("device_123")
print(validate_token(token))  # 输出True

# 过期测试
expired_payload = {"exp": datetime.utcnow() - timedelta(hours=1)}
expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")
print(validate_token(expired_token))  # 输出False 