#!/usr/bin/env python3

"""
Full SparK development seed script
Creates a realistic classroom environment.

Safe to run multiple times.
"""

import sqlite3
import os
import bcrypt
import random
from datetime import datetime, timedelta, timezone
from app import create_app
from app.models import init_db

app = create_app()

with app.app_context():
    init_db(app)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "spark-alpha-demo-seeded-full-school.db")


def random_past_date(days_back=30):
    """Return a random datetime within the past `days_back` days (UTC)"""
    now = datetime.now(timezone.utc)
    random_days = random.randint(0, days_back)
    random_seconds = random.randint(0, 86400)  # seconds in a day
    return now - timedelta(days=random_days, seconds=random_seconds)


def insert_user(db, username, password, bio, role):
    cur = db.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()

    if row:
        return row[0]

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    db.execute(
        "INSERT INTO users (username, password_hash, bio, role) VALUES (?, ?, ?, ?)",
        (username, hashed.decode(), bio, role),
    )

    db.commit()

    return db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()[0]


def insert_classroom(db, teacher_id, name, description, join_code):
    cur = db.execute("SELECT id FROM classrooms WHERE join_code = ?", (join_code,))
    row = cur.fetchone()

    if row:
        return row[0]

    db.execute(
        "INSERT INTO classrooms (teacher_id, name, description, join_code) VALUES (?, ?, ?, ?)",
        (teacher_id, name, description, join_code),
    )

    db.commit()

    return db.execute(
        "SELECT id FROM classrooms WHERE join_code = ?", (join_code,)
    ).fetchone()[0]


def add_member(db, classroom_id, user_id, role):
    cur = db.execute(
        "SELECT 1 FROM classroom_members WHERE classroom_id = ? AND user_id = ?",
        (classroom_id, user_id),
    )

    if not cur.fetchone():
        db.execute(
            "INSERT INTO classroom_members (classroom_id, user_id, role) VALUES (?, ?, ?)",
            (classroom_id, user_id, role),
        )
        db.commit()


def insert_topic(db, name, description=""):
    cur = db.execute("SELECT id FROM topics WHERE name = ?", (name,))
    row = cur.fetchone()

    if row:
        return row[0]

    db.execute(
        "INSERT INTO topics (name, description) VALUES (?, ?)",
        (name, description),
    )

    db.commit()

    return db.execute("SELECT id FROM topics WHERE name = ?", (name,)).fetchone()[0]


def insert_post(db, user_id, topic_id, title, body, parent_id=None):

    db.execute(
        """
        INSERT INTO posts (user_id, topic_id, title, body, parent_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, topic_id, title, body, parent_id, random_past_date()),
    )

    db.commit()

    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def insert_assignment(db, classroom_id, title, instructions, due_date=None):

    cur = db.execute(
        "SELECT id FROM assignments WHERE classroom_id = ? AND title = ?",
        (classroom_id, title),
    )

    row = cur.fetchone()

    if row:
        return row[0]

    db.execute(
        """
        INSERT INTO assignments (classroom_id, title, instructions, due_date)
        VALUES (?, ?, ?, ?)
        """,
        (classroom_id, title, instructions, due_date),
    )

    db.commit()

    return db.execute(
        "SELECT id FROM assignments WHERE classroom_id = ? AND title = ?",
        (classroom_id, title),
    ).fetchone()[0]


def insert_submission(db, assignment_id, user_id, body):

    cur = db.execute(
        """
        SELECT 1 FROM submissions
        WHERE assignment_id = ? AND user_id = ?
        """,
        (assignment_id, user_id),
    )

    if cur.fetchone():
        return

    db.execute(
        """
        INSERT INTO submissions (assignment_id, user_id, body, submitted_at)
        VALUES (?, ?, ?, ?)
        """,
        (assignment_id, user_id, body, random_past_date()),
    )

    db.commit()


def grade_submission(db, assignment_id, user_id):

    score = random.randint(70, 100)

    db.execute(
        """
        UPDATE submissions
        SET grade = ?, graded_at = ?
        WHERE assignment_id = ? AND user_id = ?
        """,
        (score, random_past_date(), assignment_id, user_id),
    )

    db.commit()


def insert_vote(db, user_id, post_id, value):

    cur = db.execute(
        "SELECT 1 FROM votes WHERE user_id = ? AND post_id = ?",
        (user_id, post_id),
    )

    if not cur.fetchone():
        db.execute(
            "INSERT INTO votes (user_id, post_id, value) VALUES (?, ?, ?)",
            (user_id, post_id, value),
        )
        db.commit()


def insert_bookmark(db, user_id, post_id):

    cur = db.execute(
        "SELECT 1 FROM bookmarks WHERE user_id = ? AND post_id = ?",
        (user_id, post_id),
    )

    if not cur.fetchone():
        db.execute(
            "INSERT INTO bookmarks (user_id, post_id) VALUES (?, ?)",
            (user_id, post_id),
        )
        db.commit()


def insert_notification(db, user_id, message, ntype="system", link=None):

    (
        db.execute(
            "INSERT INTO notifications (user_id, type, message, link, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, ntype, message, link, datetime.now(timezone.utc)),
        )
    )
    db.commit()


# --------------------------------------------------
# Begin seeding
# --------------------------------------------------

with sqlite3.connect(DB_PATH) as db:
    db.row_factory = sqlite3.Row

    # --------------------------
    # Students
    # --------------------------

    first_names = [
        "Alice",
        "Ben",
        "Cara",
        "David",
        "Eva",
        "Finn",
        "Grace",
        "Henry",
        "Ivy",
        "Jack",
        "Kara",
        "Liam",
        "Maya",
        "Nate",
        "Olivia",
        "Paul",
        "Quinn",
        "Rosa",
        "Sam",
        "Tina",
        "Uma",
        "Vince",
        "Willa",
        "Xander",
        "Yara",
        "Zane",
    ]

    students = [f"{name} {chr(65 + i)}" for i, name in enumerate(first_names)]

    student_ids = [
        insert_user(db, s.lower().replace(" ", "_"), "pass123", s, "student")
        for s in students
    ]

    # --------------------------
    # Teachers
    # --------------------------

    teachers = ["Mr Smith", "Mrs Johnson"]

    teacher_ids = [
        insert_user(db, t.lower().replace(" ", "_"), "pass123", t, "teacher")
        for t in teachers
    ]

    # --------------------------
    # Admin
    # --------------------------

    admin_id = insert_user(db, "rchristenhusz", "pass123", "Admin User", "teacher")

    # --------------------------
    # Topics
    # --------------------------

    topic_ids = [
        insert_topic(db, "General"),
        insert_topic(db, "Homework Help"),
        insert_topic(db, "Announcements"),
        insert_topic(db, "Off Topic"),
    ]

    # --------------------------
    # Classrooms
    # --------------------------

    classroom_data = [
        ("5th Grade Homeroom", "General classroom discussion", "HOME123"),
        ("5th Grade Math", "Math assignments and help", "MATH123"),
        ("Science Lab", "Experiments and observations", "SCI123"),
    ]

    classroom_ids = []

    for name, desc, code in classroom_data:
        cid = insert_classroom(db, random.choice(teacher_ids), name, desc, code)

        classroom_ids.append(cid)

        for sid in student_ids:
            add_member(db, cid, sid, "student")

        for tid in teacher_ids:
            add_member(db, cid, tid, "teacher")

        add_member(db, cid, admin_id, "teacher")

    # --------------------------
    # Discussion posts
    # --------------------------

    post_ids = []
    post_dates = []

    discussion_topics = [
        "Homework help",
        "Science project ideas",
        "Math questions",
        "Favorite books",
        "Study tips",
    ]

    for _ in range(20):
        title = random.choice(discussion_topics)

        post_id = insert_post(
            db,
            random.choice(student_ids),
            topic_ids[0],
            title,
            "What does everyone think about this?",
        )

        post_ids.append(post_id)
        post_dates.append(random_past_date())
        for _ in range(random.randint(2, 8)):
            insert_post(
                db,
                random.choice(student_ids),
                None,
                "Re:",
                random.choice(
                    [
                        "I think it's easier if you draw it.",
                        "The teacher explained it earlier.",
                        "I'm stuck on this too.",
                        "Try breaking it into steps.",
                        "Check the example in the book.",
                    ]
                ),
                parent_id=post_id,
            )

    # --------------------------
    # Announcements
    # --------------------------

    announcements = [
        "Homework due tomorrow.",
        "Science fair signups open.",
        "Field trip permission slips needed.",
        "Parent teacher conferences next week.",
    ]

    for msg in announcements:
        insert_post(db, random.choice(teacher_ids), topic_ids[2], "Announcement", msg)

    # --------------------------
    # Assignments
    # --------------------------

    assignment_templates = [
        ("Reading Response", "Read chapter 3 and summarize."),
        ("Math Practice", "Complete worksheet pages 12–15."),
        ("Science Observation", "Observe weather patterns."),
    ]

    assignment_ids = []

    for cid in classroom_ids:
        for title, text in assignment_templates:
            aid = insert_assignment(db, cid, title, text, random_past_date())

            assignment_ids.append(aid)

    # --------------------------
    # Submissions
    # --------------------------

    for aid in assignment_ids:
        submitters = random.sample(student_ids, random.randint(10, 20))

        for sid in submitters:
            insert_submission(db, aid, sid, "Here is my completed assignment.")

    # --------------------------
    # Grades
    # --------------------------

    for aid in assignment_ids:
        for sid in student_ids[:10]:
            grade_submission(db, aid, sid)

    # --------------------------
    # Votes
    # --------------------------

    for pid in post_ids:
        voters = random.sample(student_ids, random.randint(5, 15))

        for v in voters:
            insert_vote(db, v, pid, random.choice([1, 1, 1, -1]))

    # --------------------------
    # Bookmarks
    # --------------------------

    for sid in student_ids[:10]:
        insert_bookmark(db, sid, random.choice(post_ids))

    # --------------------------
    # Notifications
    # --------------------------

    for sid in student_ids[:10]:
        insert_notification(db, sid, "Your assignment was graded.")

    print("Seeding complete!")
    print("Students:", len(student_ids))
    print("Teachers:", len(teacher_ids) + 1)
    print("Classrooms:", len(classroom_ids))
    print("Assignments:", len(assignment_ids))
