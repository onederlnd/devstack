# app/models/user.py

import sqlite3
import bcrypt
from app.models import get_db
from flask import current_app


def create_user(username, password, bio=""):
    db = get_db()
    rounds = current_app.config.get("BCRYPT_ROUNDS", 12)
    password_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(rounds=rounds)
    ).decode()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash, bio) VALUES (?, ?, ?)",
            (username, password_hash, bio),
        )
        db.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Username already taken"


def get_user_by_username(username):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def check_password(username, password):
    user = get_user_by_username(username)
    if not user:
        return None
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return user
    return None


# --- following
def follow_user(follower_id, followed_id):
    """Insert a follow relationship, returns False if already following"""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO follows (follower_id, followed_id) VALUES (?, ?)",
            (follower_id, followed_id),
        )
        db.connect()
        return True
    except Exception:
        # composite PK prevents duplicates
        return False


def unfollow_user(follower_id, followed_id):
    """Removes a follow relationship"""
    db = get_db()
    db.execute(
        "DELETE FROM follows WHERE follower_id=? AND followed_id=?",
        (follower_id, followed_id),
    )
    db.commit()


def is_following(follower_id, followed_id):
    """Returns True if follower_id follows followed_id"""
    db = get_db()
    result = db.execute(
        "SELECT 1 FROM follows WHERE follower_id=? AND followed_id=?",
        (follower_id, followed_id),
    ).fetchone()
    return result is not None


def get_followers_count(user_id):
    """Returns number of users following user_id"""
    db = get_db()
    return db.execute(
        "SELECT COUNT(*) FROM follows WHERE follower_id=?", (user_id,)
    ).fetchone()[0]


def get_following_count(user_id):
    """Returns the number of users user_id is following."""
    db = get_db()
    return db.execute(
        "SELECT COUNT(*) FROM follows WHERE followed_id=?", (user_id,)
    ).fetchone()[0]
