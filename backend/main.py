from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
import os
import secrets
from dotenv import load_dotenv
load_dotenv()
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./calculator.db")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/auth/google/callback"
)

# Handle Render PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Base
class Base(DeclarativeBase):
    pass

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    google_id = Column(String, unique=True, nullable=True, index=True)
    is_oauth_user = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# Migration: Add OAuth columns if they don't exist
def migrate_database():
    """Add OAuth columns to existing users table"""
    try:
        with engine.connect() as conn:
            # Check if we're using PostgreSQL or SQLite
            if "postgresql" in str(engine.url):
                # PostgreSQL syntax
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS google_id VARCHAR;
                """))
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS is_oauth_user BOOLEAN DEFAULT FALSE;
                """))
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id 
                    ON users (google_id);
                """))
            else:
                # SQLite syntax - need to check if column exists first
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'google_id' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR"))
                if 'is_oauth_user' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_oauth_user BOOLEAN DEFAULT 0"))
                
                # SQLite unique index
                try:
                    conn.execute(text("""
                        CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id 
                        ON users (google_id)
                    """))
                except:
                    pass  # Index might already exist
            
            conn.commit()
            print("✅ Database migration completed successfully")
    except Exception as e:
        print(f"⚠️  Database migration note: {e}")

# Run migration
migrate_database()

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class BMIRequest(BaseModel):
    weight: float  # in kg
    height: float  # in cm

class AgeRequest(BaseModel):
    birth_date: str  # format: YYYY-MM-DD

class GSTRequest(BaseModel):
    amount: float
    gst_rate: float  # percentage

class EBBillRequest(BaseModel):
    units: float
    rate_per_unit: float

# FastAPI app
app = FastAPI(title="Calculator API", version="1.0.0")

# Session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth setup
oauth = OAuth()
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str):
    return db.query(User).filter(User.google_id == google_id).first()

def create_oauth_user(db: Session, email: str, username: str, google_id: str):
    """Create a user from OAuth login"""
    db_user = User(
        email=email,
        username=username,
        google_id=google_id,
        is_oauth_user=True,
        hashed_password=None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.get("/")
def read_root():
    return {"message": "Calculator API is running", "version": "1.0.0"}

@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Google OAuth Routes
@app.get("/auth/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    return await oauth.google.authorize_redirect(
    request,
    GOOGLE_REDIRECT_URI
)

@app.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    try:
        # Get the token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # Check if user exists by google_id
        user = get_user_by_google_id(db, google_id)
        
        if not user:
            # Check if user exists by email (linking accounts)
            user = get_user_by_email(db, email)
            
            if user:
                # Link existing account with Google
                user.google_id = google_id
                user.is_oauth_user = True
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                # Generate unique username from email
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while get_user_by_username(db, username):
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = create_oauth_user(db, email, username, google_id)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={access_token}")
        
    except Exception as e:
        print(f"OAuth error: {str(e)}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=oauth_failed")

# Calculator endpoints (protected)
@app.post("/calculate/bmi")
async def calculate_bmi(request: BMIRequest, current_user: User = Depends(get_current_user)):
    """Calculate BMI (Body Mass Index)"""
    height_m = request.height / 100  # Convert cm to meters
    bmi = request.weight / (height_m ** 2)
    
    # Determine category
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category,
        "weight": request.weight,
        "height": request.height
    }

@app.post("/calculate/age")
async def calculate_age(request: AgeRequest, current_user: User = Depends(get_current_user)):
    """Calculate age from birth date"""
    try:
        birth_date = datetime.strptime(request.birth_date, "%Y-%m-%d")
        today = datetime.now()
        
        years = today.year - birth_date.year
        months = today.month - birth_date.month
        days = today.day - birth_date.day
        
        # Adjust for negative days
        if days < 0:
            months -= 1
            # Get days in previous month
            if today.month == 1:
                prev_month = 12
                prev_year = today.year - 1
            else:
                prev_month = today.month - 1
                prev_year = today.year
            days_in_prev_month = (datetime(prev_year, prev_month + 1, 1) - timedelta(days=1)).day if prev_month < 12 else 31
            days += days_in_prev_month
        
        # Adjust for negative months
        if months < 0:
            years -= 1
            months += 12
        
        total_days = (today - birth_date).days
        
        return {
            "years": years,
            "months": months,
            "days": days,
            "total_days": total_days,
            "birth_date": request.birth_date
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@app.post("/calculate/gst")
async def calculate_gst(request: GSTRequest, current_user: User = Depends(get_current_user)):
    """Calculate GST (Goods and Services Tax)"""
    gst_amount = request.amount * (request.gst_rate / 100)
    total_amount = request.amount + gst_amount
    
    return {
        "original_amount": round(request.amount, 2),
        "gst_rate": request.gst_rate,
        "gst_amount": round(gst_amount, 2),
        "total_amount": round(total_amount, 2)
    }

@app.post("/calculate/eb-bill")
async def calculate_eb_bill(request: EBBillRequest, current_user: User = Depends(get_current_user)):
    """Calculate Electricity Bill"""
    total_cost = request.units * request.rate_per_unit
    
    # Add fixed charges (example: 5% of total)
    fixed_charges = total_cost * 0.05
    final_amount = total_cost + fixed_charges
    
    return {
        "units": request.units,
        "rate_per_unit": request.rate_per_unit,
        "energy_charges": round(total_cost, 2),
        "fixed_charges": round(fixed_charges, 2),
        "total_amount": round(final_amount, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
