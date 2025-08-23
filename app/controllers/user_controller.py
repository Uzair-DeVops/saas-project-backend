"""
User controller with functional approach for user management
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user_model import UserSignUp, UserSignIn, UserResponse
from ..utils.auth_utils import verify_password, get_password_hash, create_access_token, get_current_user_from_token
from ..utils.database_dependency import get_database_session
from ..utils.my_logger import get_logger

logger = get_logger("USER_CONTROLLER")

security = HTTPBearer()
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_database_session)) -> UserSignUp:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        username = get_current_user_from_token(token)
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user by username
        user = get_user_by_username(username, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
def create_user(user_data: UserSignUp, db: Session) -> UserResponse:
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user_data.email, db)
        if existing_user:
            logger.warning(f"User creation failed: email {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = get_user_by_username(user_data.username, db)
        if existing_username:
            logger.warning(f"User creation failed: username {user_data.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user object
        user = UserSignUp(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            password=hashed_password
        )
        
        # Save to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created successfully: {user.email}")
        
        # Return user response without password
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

def authenticate_user(email: str, password: str, db: Session) -> Optional[UserSignUp]:
    """Authenticate user with email and password"""
    try:
        user = get_user_by_email(email, db)
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            return None
        
        if not verify_password(password, user.password):
            logger.warning(f"Authentication failed: invalid password for email {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: inactive user {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

def login_user(user_data: UserSignIn, db: Session) -> dict:
    """Login user and return access token"""
    try:
        user = authenticate_user(user_data.email, user_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

def get_user_by_email(email: str, db: Session) -> Optional[UserSignUp]:
    """Get user by email"""
    try:
        statement = select(UserSignUp).where(UserSignUp.email == email)
        return db.exec(statement).first()
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def get_user_by_username(username: str, db: Session) -> Optional[UserSignUp]:
    """Get user by username"""
    try:
        statement = select(UserSignUp).where(UserSignUp.username == username)
        return db.exec(statement).first()
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None

def get_user_by_id(user_id: str, db: Session) -> Optional[UserResponse]:
    """Get user by ID"""
    try:
        # Convert string to UUID
        user_uuid = UUID(user_id)
        statement = select(UserSignUp).where(UserSignUp.id == user_uuid)
        user = db.exec(statement).first()
        
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

def get_all_users(db: Session) -> List[UserResponse]:
    """Get all users"""
    try:
        statement = select(UserSignUp)
        users = db.exec(statement).all()
        
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

def update_user(user_id: str, user_data: dict, db: Session) -> UserResponse:
    """Update user information"""
    try:
        # Convert string to UUID
        user_uuid = UUID(user_id)
        statement = select(UserSignUp).where(UserSignUp.id == user_uuid)
        user = db.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        for field, value in user_data.items():
            if hasattr(user, field) and field != "id" and field != "password":
                setattr(user, field, value)
        
        # Update timestamp
        from datetime import datetime
        user.updated_at = datetime.utcnow()
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated successfully: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

def delete_user(user_id: str, db: Session) -> bool:
    """Delete user"""
    try:
        # Convert string to UUID
        user_uuid = UUID(user_id)
        statement = select(UserSignUp).where(UserSignUp.id == user_uuid)
        user = db.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"User deleted successfully: {user.email}")
        return True
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        ) 