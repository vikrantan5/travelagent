import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import jwt
from loguru import logger
from services.db_service import get_db_pool
from models.user import UserCreate, UserResponse


JWT_SECRET = os.getenv("JWT_SECRET", "tripcraft_jwt_secret_key_2025_secure_random_string")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30


def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, pwd_hash = hashed.split("$")
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False


def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    expires = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expires
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


async def create_user(user_data: UserCreate) -> Optional[UserResponse]:
    """Create a new user in the database"""
    pool = get_db_pool()
    user_id = secrets.token_urlsafe(16)
    hashed_password = hash_password(user_data.password)
    
    try:
        async with pool.acquire() as conn:
            # Check if user already exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1",
                user_data.email
            )
            
            if existing:
                logger.warning(f"User with email {user_data.email} already exists")
                return None
            
            # Insert user
            await conn.execute(
                """
                INSERT INTO users (id, email, password, name, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                user_id, user_data.email, hashed_password, user_data.name,
                datetime.utcnow(), datetime.utcnow()
            )
            
            # Create user planner status
            await conn.execute(
                """
                INSERT INTO user_planner_status (user_id, has_used_free_planner, total_planners_created, is_premium)
                VALUES ($1, $2, $3, $4)
                """,
                user_id, False, 0, False
            )
            
            # Fetch created user
            user = await conn.fetchrow(
                """
                SELECT u.id, u.email, u.name, u.created_at,
                       ups.has_used_free_planner, ups.total_planners_created, ups.is_premium
                FROM users u
                LEFT JOIN user_planner_status ups ON u.id = ups.user_id
                WHERE u.id = $1
                """,
                user_id
            )
            
            return UserResponse(
                id=user['id'],
                email=user['email'],
                name=user['name'],
                created_at=user['created_at'],
                subscription_type="premium" if user['is_premium'] else "free",
                has_used_free_planner=user['has_used_free_planner'],
                total_planners_created=user['total_planners_created'],
                is_premium=user['is_premium']
            )
            
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise


async def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
    """Authenticate user with email and password"""
    pool = get_db_pool()
    
    try:
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT u.id, u.email, u.password, u.name, u.created_at,
                       ups.has_used_free_planner, ups.total_planners_created, ups.is_premium
                FROM users u
                LEFT JOIN user_planner_status ups ON u.id = ups.user_id
                WHERE u.email = $1
                """,
                email
            )
            
            if not user:
                logger.warning(f"User not found: {email}")
                return None
            
            if not verify_password(password, user['password']):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            return UserResponse(
                id=user['id'],
                email=user['email'],
                name=user['name'],
                created_at=user['created_at'],
                subscription_type="premium" if user['is_premium'] else "free",
                has_used_free_planner=user['has_used_free_planner'],
                total_planners_created=user['total_planners_created'],
                is_premium=user['is_premium']
            )
            
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        raise


async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    """Get user by ID"""
    pool = get_db_pool()
    
    try:
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT u.id, u.email, u.name, u.created_at,
                       ups.has_used_free_planner, ups.total_planners_created, ups.is_premium
                FROM users u
                LEFT JOIN user_planner_status ups ON u.id = ups.user_id
                WHERE u.id = $1
                """,
                user_id
            )
            
            if not user:
                return None
            
            return UserResponse(
                id=user['id'],
                email=user['email'],
                name=user['name'],
                created_at=user['created_at'],
                subscription_type="premium" if user['is_premium'] else "free",
                has_used_free_planner=user['has_used_free_planner'],
                total_planners_created=user['total_planners_created'],
                is_premium=user['is_premium']
            )
            
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise
