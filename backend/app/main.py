from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import engine, get_db, Base
from .models import User
from .schemas import UserResponse, QuizStartResponse

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Thai Drill Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/quiz/start", response_model=QuizStartResponse)
def start_quiz(nickname: str, db: Session = Depends(get_db)):
    """
    Increment the quiz start counter for a user.
    Creates the user if they don't exist yet.
    """
    # Try to get existing user
    user = db.query(User).filter(User.nickname == nickname).first()

    if not user:
        # Create new user with counter = 1
        user = User(nickname=nickname, quiz_starts=1)
    else:
        # Increment counter
        user.quiz_starts += 1

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        # Race condition: user was created by another request
        # Fetch and update again
        user = db.query(User).filter(User.nickname == nickname).first()
        if user:
            user.quiz_starts += 1
            db.add(user)
            db.commit()
            db.refresh(user)

    return QuizStartResponse(
        nickname=user.nickname,
        quiz_starts=user.quiz_starts
    )


@app.get("/api/user/{nickname}", response_model=UserResponse)
def get_user(nickname: str, db: Session = Depends(get_db)):
    """
    Get user information including their quiz start counter.
    """
    user = db.query(User).filter(User.nickname == nickname).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
