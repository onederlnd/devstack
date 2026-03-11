# scripts/admin.py

import sys
import os
import bcrypt
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.models import get_db

app = create_app()

current_user_id = None
current_username = None


def menu():
    user_label = f" (acting as: {current_username})" if current_username else ""
    print(f"\n== SparK admin{user_label} ==")
    print("--- users ---")
    print("1.  list users & their posts")
    print("2.  create user")
    print("3.  delete user")
    print("4.  switch active user")
    print("--- posts ---")
    print("5.  create post")
    print("6.  delete post")
    print("7.  reply to post")
    print("--- social ---")
    print("8.  follow user")
    print("9.  unfollow user")
    print("10. list followers/following")
    print("--- topics ---")
    print("11. list topics")
    print("12. create topic")
    print("13. delete topic")
    print("--- db ---")
    print("14. reset database")
    print("15. auto-seed test data")
    print("--- testing ---")
    print("16. testing submenu")
    print("0.  exit")
    return input("\n> ").strip()


def testing_menu():
    while True:
        print("\n== testing submenu ==")
        print("1.  auto follow/unfollow with delay")
        print("2.  spam posts (bulk create)")
        print("3.  spam replies (bulk reply to post)")
        print("4.  bulk vote posts")
        print("5.  simulate notification flood")
        print("6.  create users with varied activity levels")
        print("7.  stress test: create N posts rapidly")
        print("0.  back")
        choice = input("\n> ").strip()

        with app.app_context():
            db = get_db()
            if choice == "1":
                test_follow_unfollow(db)
            elif choice == "2":
                test_spam_posts(db)
            elif choice == "3":
                test_spam_replies(db)
            elif choice == "4":
                test_bulk_vote(db)
            elif choice == "5":
                test_notification_flood(db)
            elif choice == "6":
                test_varied_users(db)
            elif choice == "7":
                test_stress_posts(db)
            elif choice == "0":
                break
            else:
                print("invalid option.")


def test_follow_unfollow(db):
    if not current_user_id:
        print("no active user. switch first.")
        return
    users = db.execute(
        "SELECT id, username FROM users WHERE id != ?", (current_user_id,)
    ).fetchall()
    if not users:
        print("no other users.")
        return
    for u in users:
        print(f"  [{u['id']}] {u['username']}")
    target_id = input("enter user id to follow/unfollow: ").strip()
    if not target_id.isdigit():
        print("invalid id.")
        return
    target_id = int(target_id)
    cycles = input("how many follow/unfollow cycles? (default 3): ").strip()
    cycles = int(cycles) if cycles.isdigit() else 3
    delay = input("delay between actions in seconds? (default 1): ").strip()
    delay = float(delay) if delay.replace(".", "").isdigit() else 1.0

    for i in range(cycles):
        print(f"  cycle {i + 1}/{cycles}: following...")
        db.execute(
            "INSERT OR IGNORE INTO follows (follower_id, followed_id) VALUES (?,?)",
            (current_user_id, target_id),
        )
        db.commit()
        time.sleep(delay)
        print(f"  cycle {i + 1}/{cycles}: unfollowing...")
        db.execute(
            "DELETE FROM follows WHERE follower_id=? AND followed_id=?",
            (current_user_id, target_id),
        )
        db.commit()
        time.sleep(delay)
    print(f"done. {cycles} follow/unfollow cycles completed.")


def test_spam_posts(db):
    if not current_user_id:
        print("no active user. switch first.")
        return
    count = input("how many posts to create? (default 5): ").strip()
    count = int(count) if count.isdigit() else 5
    topic = input("topic name (optional): ").strip()
    topic_id = None
    if topic:
        row = db.execute("SELECT id FROM topics WHERE name=?", (topic,)).fetchone()
        if row:
            topic_id = row["id"]
        else:
            print(f"topic '{topic}' not found, posting without topic.")

    for i in range(1, count + 1):
        title = f"[test] spam post {i} — {int(time.time())}"
        body = f"this is automated test post #{i}. created at {time.time()}."
        db.execute(
            "INSERT INTO posts (user_id, title, body, topic_id) VALUES (?,?,?,?)",
            (current_user_id, title, body, topic_id),
        )
        db.commit()
        print(f"  created post {i}/{count}")
    print(f"done. {count} posts created.")


def test_spam_replies(db):
    if not current_user_id:
        print("no active user. switch first.")
        return
    posts = db.execute("""
        SELECT posts.id, users.username, posts.title FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.parent_id IS NULL ORDER BY posts.id DESC LIMIT 20
    """).fetchall()
    if not posts:
        print("no posts found.")
        return
    for p in posts:
        print(f"  [{p['id']}] {p['username']}: {p['title'][:50]}")
    post_id = input("enter post id to spam replies on: ").strip()
    if not post_id.isdigit():
        print("invalid id.")
        return
    count = input("how many replies? (default 5): ").strip()
    count = int(count) if count.isdigit() else 5
    for i in range(1, count + 1):
        body = f"[test] automated reply #{i} at {time.time()}"
        db.execute(
            "INSERT INTO posts (user_id, title, body, parent_id) VALUES (?,?,?,?)",
            (current_user_id, "", body, int(post_id)),
        )
        db.commit()
        print(f"  reply {i}/{count} posted")
    print(f"done. {count} replies created.")


def test_bulk_vote(db):
    if not current_user_id:
        print("no active user. switch first.")
        return
    posts = db.execute(
        """
        SELECT posts.id, users.username, posts.title, posts.votes FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.parent_id IS NULL AND posts.user_id != ?
        ORDER BY posts.id DESC LIMIT 20
    """,
        (current_user_id,),
    ).fetchall()
    if not posts:
        print("no posts found.")
        return
    for p in posts:
        print(f"  [{p['id']}] {p['username']}: {p['title'][:40]} (votes: {p['votes']})")
    value = input("vote value: 1 (upvote) or -1 (downvote)? (default 1): ").strip()
    value = -1 if value == "-1" else 1
    confirm = input(f"vote {value} on all {len(posts)} posts above? (y/n): ")
    if confirm.lower() != "y":
        print("cancelled.")
        return
    for p in posts:
        existing = db.execute(
            "SELECT value FROM votes WHERE user_id=? AND post_id=?",
            (current_user_id, p["id"]),
        ).fetchone()
        if existing:
            print(f"  post {p['id']}: already voted, skipping.")
            continue
        db.execute(
            "INSERT INTO votes (user_id, post_id, value) VALUES (?,?,?)",
            (current_user_id, p["id"], value),
        )
        db.execute("UPDATE posts SET votes = votes + ? WHERE id = ?", (value, p["id"]))
        db.commit()
        print(f"  voted {value} on post {p['id']}")
    print("done.")


def test_notification_flood(db):
    if not current_user_id:
        print("no active user. switch first.")
        return
    users = db.execute(
        "SELECT id, username FROM users WHERE id != ?", (current_user_id,)
    ).fetchall()
    if not users:
        print("no other users.")
        return
    for u in users:
        print(f"  [{u['id']}] {u['username']}")
    target_id = input("send notifications to user id: ").strip()
    if not target_id.isdigit():
        print("invalid id.")
        return
    count = input("how many notifications? (default 5): ").strip()
    count = int(count) if count.isdigit() else 5
    for i in range(1, count + 1):
        db.execute(
            "INSERT INTO notifications (user_id, type, message, link) VALUES (?,?,?,?)",
            (int(target_id), "test", f"[test] notification {i} of {count}", "/"),
        )
        db.commit()
        print(f"  notification {i}/{count} sent")
    print(f"done. {count} notifications created.")


def test_varied_users(db):
    seed = [
        ("ms_johnson", "pass123", "5th grade math teacher. Love making learning fun!"),
        ("student_alex", "pass123", "6th grader. Into coding and science experiments."),
        ("parent_mike", "pass123", "Dad of two, keeping an eye on things."),
        ("mr_patel", "pass123", "High school biology teacher. Science is life."),
        ("student_priya", "pass123", "8th grade. I love reading and creative writing."),
    ]
    for username, password, bio in seed:
        existing = db.execute(
            "SELECT id FROM users WHERE username=?", (username,)
        ).fetchone()
        if existing:
            print(f"  user '{username}' already exists, skipping.")
            continue
        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt(rounds=12)
        ).decode()
        db.execute(
            "INSERT INTO users (username, password_hash, bio) VALUES (?,?,?)",
            (username, password_hash, bio),
        )
        db.commit()
        print(f"  created user '{username}'.")
    print("done.")


def test_stress_posts(db):
    if not current_user_id:
        print("no active user. switch first.")
        return
    count = input("how many posts to create rapidly? (default 20): ").strip()
    count = int(count) if count.isdigit() else 20
    confirm = input(f"create {count} posts as {current_username}? (y/n): ")
    if confirm.lower() != "y":
        print("cancelled.")
        return
    start = time.time()
    for i in range(1, count + 1):
        db.execute(
            "INSERT INTO posts (user_id, title, body) VALUES (?,?,?)",
            (
                current_user_id,
                f"[stress] post {i}",
                f"stress test body {i} — {time.time()}",
            ),
        )
        db.commit()
    elapsed = time.time() - start
    print(f"done. {count} posts created in {elapsed:.2f}s.")


def list_users_and_posts(db):
    users = db.execute("SELECT id, username, bio FROM users ORDER BY id").fetchall()
    if not users:
        print("no users found.")
        return
    for u in users:
        marker = " *" if u["id"] == current_user_id else ""
        followers = db.execute(
            "SELECT COUNT(*) FROM follows WHERE followed_id=?", (u["id"],)
        ).fetchone()[0]
        following = db.execute(
            "SELECT COUNT(*) FROM follows WHERE follower_id=?", (u["id"],)
        ).fetchone()[0]
        print(f"\n┌─ [{u['id']}] {u['username']}{marker}")
        print(f"│  bio: {u['bio'] or '(none)'}")
        print(f"│  followers: {followers}  following: {following}")
        posts = db.execute(
            """
            SELECT id, title FROM posts
            WHERE user_id=? AND parent_id IS NULL
            ORDER BY id DESC LIMIT 10
        """,
            (u["id"],),
        ).fetchall()
        if posts:
            for p in posts:
                print(f"│    post [{p['id']}] {p['title'][:50]}")
        else:
            print("│    (no posts)")
    print()


def create_user(db):
    username = input("username: ").strip()
    if not username:
        print("username cannot be empty.")
        return
    password = input("password: ").strip()
    if not password:
        print("password cannot be empty.")
        return
    bio = input("bio (optional): ").strip()
    existing = db.execute(
        "SELECT id FROM users WHERE username=?", (username,)
    ).fetchone()
    if existing:
        print(f"user '{username}' already exists.")
        return
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    db.execute(
        "INSERT INTO users (username, password_hash, bio) VALUES (?,?,?)",
        (username, password_hash, bio),
    )
    db.commit()
    print(f"user '{username}' created.")


def delete_user(db):
    list_users_and_posts(db)
    user_id = input("enter user id to delete: ").strip()
    if not user_id.isdigit():
        print("invalid id.")
        return
    confirm = input(f"delete user {user_id} and all their data? (y/n): ")
    if confirm.lower() != "y":
        print("cancelled.")
        return
    for table in ("votes", "bookmarks", "follows", "notifications", "posts"):
        db.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
    db.execute("DELETE FROM follows WHERE followed_id=?", (user_id,))
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    print(f"user {user_id} deleted.")


def switch_user(db):
    global current_user_id, current_username
    users = db.execute("SELECT id, username FROM users ORDER BY id").fetchall()
    if not users:
        print("no users found.")
        return
    print()
    for u in users:
        marker = " *" if u["id"] == current_user_id else ""
        print(f"  [{u['id']}] {u['username']}{marker}")
    print()
    user_id = input("enter user id (or 0 to clear): ").strip()
    if user_id == "0":
        current_user_id = None
        current_username = None
        print("active user cleared.")
        return
    if not user_id.isdigit():
        print("invalid id.")
        return
    row = db.execute("SELECT id, username FROM users WHERE id=?", (user_id,)).fetchone()
    if not row:
        print("user not found.")
        return
    current_user_id = row["id"]
    current_username = row["username"]
    print(f"switched to '{current_username}'.")


def create_post(db):
    if not current_user_id:
        print("no active user. use option 4 to switch user first.")
        return
    print(f"creating post as: {current_username}")
    title = input("title: ").strip()
    if not title:
        print("title cannot be empty.")
        return
    body = input("body: ").strip()
    if not body:
        print("body cannot be empty.")
        return
    topic = input("topic name (optional): ").strip()
    topic_id = None
    if topic:
        row = db.execute("SELECT id FROM topics WHERE name=?", (topic,)).fetchone()
        if row:
            topic_id = row["id"]
        else:
            create = input(f"topic '{topic}' not found. create it? (y/n): ")
            if create.lower() == "y":
                db.execute(
                    "INSERT INTO topics (name, description) VALUES (?,?)", (topic, "")
                )
                db.commit()
                topic_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                print(f"topic '{topic}' created.")
    db.execute(
        "INSERT INTO posts (user_id, title, body, topic_id) VALUES (?,?,?,?)",
        (current_user_id, title, body, topic_id),
    )
    db.commit()
    print(f"post '{title}' created.")


def delete_post(db):
    posts = db.execute("""
        SELECT posts.id, users.username, posts.title
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.parent_id IS NULL
        ORDER BY users.username, posts.id DESC
        LIMIT 50
    """).fetchall()
    if not posts:
        print("no posts found.")
        return
    current_author = None
    for p in posts:
        if p["username"] != current_author:
            current_author = p["username"]
            print(f"\n  {current_author}")
        print(f"    [{p['id']}] {p['title'][:50]}")
    print()
    post_id = input("enter post id to delete: ").strip()
    if not post_id.isdigit():
        print("invalid id.")
        return
    confirm = input(f"delete post {post_id} and all its replies? (y/n): ")
    if confirm.lower() != "y":
        print("cancelled.")
        return
    db.execute("DELETE FROM posts WHERE id=? OR parent_id=?", (post_id, post_id))
    db.commit()
    print(f"post {post_id} deleted.")


def reply_to_post(db):
    if not current_user_id:
        print("no active user. use option 4 to switch user first.")
        return
    posts = db.execute("""
        SELECT posts.id, users.username, posts.title
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.parent_id IS NULL
        ORDER BY posts.id DESC LIMIT 20
    """).fetchall()
    if not posts:
        print("no posts found.")
        return
    for p in posts:
        print(f"  [{p['id']}] {p['username']}: {p['title'][:50]}")
    print()
    post_id = input("enter post id to reply to: ").strip()
    if not post_id.isdigit():
        print("invalid id.")
        return
    body = input("reply: ").strip()
    if not body:
        print("reply cannot be empty.")
        return
    db.execute(
        "INSERT INTO posts (user_id, title, body, parent_id) VALUES (?,?,?,?)",
        (current_user_id, "", body, int(post_id)),
    )
    db.commit()
    print("reply posted.")


def follow_user(db):
    if not current_user_id:
        print("no active user. use option 4 to switch user first.")
        return
    users = db.execute(
        "SELECT id, username FROM users WHERE id != ? ORDER BY username",
        (current_user_id,),
    ).fetchall()
    if not users:
        print("no other users found.")
        return
    already_following = [
        r["followed_id"]
        for r in db.execute(
            "SELECT followed_id FROM follows WHERE follower_id=?", (current_user_id,)
        ).fetchall()
    ]
    for u in users:
        status = " (following)" if u["id"] in already_following else ""
        print(f"  [{u['id']}] {u['username']}{status}")
    print()
    user_id = input("enter user id to follow: ").strip()
    if not user_id.isdigit():
        print("invalid id.")
        return
    user_id = int(user_id)
    if user_id == current_user_id:
        print("can't follow yourself.")
        return
    existing = db.execute(
        "SELECT 1 FROM follows WHERE follower_id=? AND followed_id=?",
        (current_user_id, user_id),
    ).fetchone()
    if existing:
        print("already following.")
        return
    db.execute(
        "INSERT INTO follows (follower_id, followed_id) VALUES (?,?)",
        (current_user_id, user_id),
    )
    db.commit()
    print("followed.")


def unfollow_user(db):
    if not current_user_id:
        print("no active user. use option 4 to switch user first.")
        return
    following = db.execute(
        """
        SELECT users.id, users.username FROM follows
        JOIN users ON follows.followed_id = users.id
        WHERE follows.follower_id=?
        ORDER BY users.username
    """,
        (current_user_id,),
    ).fetchall()
    if not following:
        print("not following anyone.")
        return
    for u in following:
        print(f"  [{u['id']}] {u['username']}")
    print()
    user_id = input("enter user id to unfollow: ").strip()
    if not user_id.isdigit():
        print("invalid id.")
        return
    db.execute(
        "DELETE FROM follows WHERE follower_id=? AND followed_id=?",
        (current_user_id, int(user_id)),
    )
    db.commit()
    print("unfollowed.")


def list_follows(db):
    if not current_user_id:
        print("no active user. use option 4 to switch user first.")
        return
    followers = db.execute(
        """
        SELECT users.username FROM follows
        JOIN users ON follows.follower_id = users.id
        WHERE follows.followed_id=?
    """,
        (current_user_id,),
    ).fetchall()
    following = db.execute(
        """
        SELECT users.username FROM follows
        JOIN users ON follows.followed_id = users.id
        WHERE follows.follower_id=?
    """,
        (current_user_id,),
    ).fetchall()
    print(f"\nfollowers of {current_username}:")
    for f in followers:
        print(f"  {f['username']}")
    if not followers:
        print("  (none)")
    print(f"\n{current_username} is following:")
    for f in following:
        print(f"  {f['username']}")
    if not following:
        print("  (none)")


def list_topics(db):
    topics = db.execute("""
        SELECT topics.id, topics.name, topics.description, COUNT(posts.id) as post_count
        FROM topics
        LEFT JOIN posts ON posts.topic_id = topics.id AND posts.parent_id IS NULL
        GROUP BY topics.id
        ORDER BY topics.name
    """).fetchall()
    if not topics:
        print("no topics found.")
        return
    print(f"\n{'id':<6} {'name':<20} {'posts':<8} {'description'}")
    print("-" * 60)
    for t in topics:
        print(
            f"{t['id']:<6} {t['name']:<20} {t['post_count']:<8} {t['description'] or ''}"
        )


def create_topic(db):
    name = input("topic name: ").strip()
    if not name:
        print("name cannot be empty.")
        return
    existing = db.execute("SELECT id FROM topics WHERE name=?", (name,)).fetchone()
    if existing:
        print(f"topic '{name}' already exists.")
        return
    description = input("description (optional): ").strip()
    db.execute(
        "INSERT INTO topics (name, description) VALUES (?,?)", (name, description)
    )
    db.commit()
    print(f"topic '{name}' created.")


def delete_topic(db):
    list_topics(db)
    topic_id = input("\nenter topic id to delete: ").strip()
    if not topic_id.isdigit():
        print("invalid id.")
        return
    confirm = input(
        f"delete topic {topic_id}? posts will keep their content but lose the topic. (y/n): "
    )
    if confirm.lower() != "y":
        print("cancelled.")
        return
    db.execute("UPDATE posts SET topic_id=NULL WHERE topic_id=?", (topic_id,))
    db.execute("DELETE FROM topics WHERE id=?", (topic_id,))
    db.commit()
    print(f"topic {topic_id} deleted.")


def reset_database(db):
    confirm = input("this will delete ALL data. type 'reset' to confirm: ").strip()
    if confirm != "reset":
        print("cancelled.")
        return
    for table in (
        "votes",
        "bookmarks",
        "follows",
        "notifications",
        "posts",
        "topics",
        "users",
    ):
        db.execute(f"DELETE FROM {table}")
    db.commit()
    print("database reset.")


def auto_seed(db):
    confirm = input(
        "seed test users, topics, posts, follows, votes, and replies? (y/n): "
    )
    if confirm.lower() != "y":
        print("cancelled.")
        return

    # --- users ---
    seed_users = [
        (
            "rchristenhusz",
            "pass123",
            "Admin and platform builder. Here to keep things running.",
        ),
        ("ms_johnson", "pass123", "5th grade math teacher. Love making numbers fun!"),
        ("mr_patel", "pass123", "High school biology teacher. Science is everywhere."),
        ("student_alex", "pass123", "6th grader. I love coding and building things."),
        ("student_priya", "pass123", "8th grade. Into creative writing and reading."),
        ("parent_mike", "pass123", "Dad of two SparK users. Love seeing them learn."),
    ]

    user_ids = {}
    for username, password, bio in seed_users:
        existing = db.execute(
            "SELECT id FROM users WHERE username=?", (username,)
        ).fetchone()
        if existing:
            user_ids[username] = existing["id"]
            print(f"  user '{username}' already exists, skipping.")
        else:
            password_hash = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt(rounds=12)
            ).decode()
            db.execute(
                "INSERT INTO users (username, password_hash, bio) VALUES (?,?,?)",
                (username, password_hash, bio),
            )
            db.commit()
            user_ids[username] = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            print(f"  created user '{username}'.")

    rc_id = user_ids["rchristenhusz"]
    ms_j_id = user_ids["ms_johnson"]
    mr_p_id = user_ids["mr_patel"]
    alex_id = user_ids["student_alex"]
    priya_id = user_ids["student_priya"]
    mike_id = user_ids["parent_mike"]

    # --- follows: students follow teachers, teachers follow each other ---
    follow_pairs = [
        (alex_id, ms_j_id),
        (alex_id, mr_p_id),
        (priya_id, ms_j_id),
        (priya_id, mr_p_id),
        (mike_id, ms_j_id),
        (mike_id, mr_p_id),
        (ms_j_id, mr_p_id),
        (mr_p_id, ms_j_id),
        (alex_id, priya_id),
        (priya_id, alex_id),
        (rc_id, ms_j_id),
        (rc_id, mr_p_id),
    ]
    for follower, followed in follow_pairs:
        exists = db.execute(
            "SELECT 1 FROM follows WHERE follower_id=? AND followed_id=?",
            (follower, followed),
        ).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO follows (follower_id, followed_id) VALUES (?,?)",
                (follower, followed),
            )
    db.commit()
    print("  follows set.")

    # --- topics ---
    topic_data = [
        ("math", "Numbers, equations, geometry, and problem solving."),
        ("science", "Biology, chemistry, physics, and experiments."),
        ("reading", "Books, stories, poetry, and creative writing."),
        ("coding", "Programming, projects, and tech questions."),
        ("general", "Anything that doesn't fit elsewhere."),
    ]
    topic_ids = {}
    for name, description in topic_data:
        row = db.execute("SELECT id FROM topics WHERE name=?", (name,)).fetchone()
        if row:
            topic_ids[name] = row["id"]
            print(f"  topic '{name}' already exists, skipping.")
        else:
            db.execute(
                "INSERT INTO topics (name, description) VALUES (?,?)",
                (name, description),
            )
            db.commit()
            topic_ids[name] = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            print(f"  created topic '{name}'.")

    # --- posts ---
    seed_posts = [
        (
            ms_j_id,
            "math",
            "How to find the least common multiple — explained simply",
            "The LCM is the smallest number that two numbers both divide into evenly. "
            "Start by listing multiples of each number until you find one they share. "
            "For 4 and 6: multiples of 4 are 4, 8, 12... multiples of 6 are 6, 12... "
            "so the LCM is 12. There's also a faster method using prime factorization!",
        ),
        (
            ms_j_id,
            "math",
            "Why does order of operations matter? (PEMDAS explained)",
            "Without a standard order of operations, the same equation could give "
            "different answers depending on who solves it. PEMDAS (Parentheses, "
            "Exponents, Multiplication/Division, Addition/Subtraction) is the agreed "
            "rule everyone follows. Try this: what is 2 + 3 × 4? It's 14, not 20!",
        ),
        (
            mr_p_id,
            "science",
            "What actually happens during photosynthesis?",
            "Plants use sunlight, water, and carbon dioxide to make glucose and oxygen. "
            "The chlorophyll in leaves absorbs light energy to power this reaction. "
            "The equation is: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. "
            "Essentially, plants are making their own food while cleaning our air!",
        ),
        (
            mr_p_id,
            "science",
            "The difference between a hypothesis and a theory",
            "A hypothesis is an educated guess you can test. A theory is a well-tested "
            "explanation supported by a lot of evidence. In science, a theory isn't "
            "just a guess — it's one of the strongest conclusions we can make. "
            "Evolution and gravity are both theories. That means they're extremely "
            "well supported, not uncertain!",
        ),
        (
            alex_id,
            "coding",
            "I built my first Python program — a number guessing game!",
            "After a few weeks in our school coding club I finally built something "
            "that actually works. You guess a number between 1 and 100 and it tells "
            "you if you're too high or too low. Used a while loop and if/elif/else. "
            "Really proud of this one. Happy to share the code if anyone wants to see it!",
        ),
        (
            alex_id,
            "coding",
            "Can someone explain what a variable is in plain English?",
            "I know what variables are in math class but in coding it feels different. "
            "Like in Python when I write x = 5, is x actually storing the number 5 "
            "somewhere? Or is it more like a label? My teacher tried to explain it "
            "but I'm still a little confused. Any help appreciated!",
        ),
        (
            priya_id,
            "reading",
            "Book review: The Giver by Lois Lowry",
            "I just finished The Giver for English class and I can't stop thinking "
            "about it. The idea of a society that removes all pain but also all choice "
            "is really unsettling. Jonas seeing colour for the first time felt magical. "
            "The ending left me with so many questions. Has anyone else read it? "
            "What did you think Jonas found at the end?",
        ),
        (
            priya_id,
            "reading",
            "Tips for writing a strong story opening?",
            "I'm working on a short story for class and my teacher said my opening "
            "is too slow. She said to 'start in the action' but I don't really know "
            "what that means. Do I just skip the background info entirely? "
            "How do you hook the reader from the very first sentence?",
        ),
        (
            mike_id,
            "general",
            "How do I help my kid who's struggling with fractions?",
            "My daughter is in 5th grade and really struggling with adding fractions "
            "with different denominators. She understands same-denominator fractions "
            "fine but gets totally lost when they're different. We've tried a few "
            "YouTube videos but nothing has clicked yet. Any teachers or students "
            "here have advice or resources that worked for you?",
        ),
        (
            rc_id,
            "general",
            "Welcome to SparK — a few things to know",
            "Hi everyone, welcome to SparK! This is a community built for students, "
            "teachers, and parents to learn and connect safely. A few guidelines: "
            "be kind, be helpful, and stay on topic. Teachers have a blue badge. "
            "If you see something that doesn't belong, use the report button. "
            "We're glad you're here — now go explore the topics and jump in!",
        ),
    ]

    post_ids = {}
    for user_id, topic, title, body in seed_posts:
        existing = db.execute(
            "SELECT id FROM posts WHERE user_id=? AND title=?", (user_id, title)
        ).fetchone()
        if existing:
            post_ids[title] = existing["id"]
            print(f"  post '{title[:45]}' already exists, skipping.")
        else:
            db.execute(
                "INSERT INTO posts (user_id, title, body, topic_id) VALUES (?,?,?,?)",
                (user_id, title, body, topic_ids[topic]),
            )
            db.commit()
            pid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            post_ids[title] = pid
            print(f"  created post '{title[:45]}'.")

    # --- replies ---
    seed_replies = [
        (
            alex_id,
            post_ids["How to find the least common multiple — explained simply"],
            "This actually helped a lot! I was always confused about why we needed "
            "the LCM. The multiples list method makes way more sense to me than "
            "what my textbook showed.",
        ),
        (
            priya_id,
            post_ids["How to find the least common multiple — explained simply"],
            "We just covered this in class! The prime factorization method is faster "
            "once you get the hang of it. Great explanation Ms. Johnson!",
        ),
        (
            ms_j_id,
            post_ids["Can someone explain what a variable is in plain English?"],
            "Great question Alex! Think of a variable like a labelled box. The box "
            "has a name (like x) and you can put a value inside it. When you write "
            "x = 5, you're putting 5 into the box called x. You can change what's "
            "inside anytime — that's why it's called a variable!",
        ),
        (
            mr_p_id,
            post_ids["Can someone explain what a variable is in plain English?"],
            "To add to Ms. Johnson's explanation — in science we use variables too! "
            "In an experiment, the variable is what you're measuring or changing. "
            "Same idea: a container for a value that can change.",
        ),
        (
            priya_id,
            post_ids["I built my first Python program — a number guessing game!"],
            "That's so cool Alex! I want to try coding. What app do you use to write "
            "Python? Is it hard to get started?",
        ),
        (
            ms_j_id,
            post_ids["How do I help my kid who's struggling with fractions?"],
            "Hi! One thing that really helps is using physical objects — pizza slices, "
            "Lego bricks, or even paper folding. Seeing fractions visually before "
            "working with numbers abstractly makes a big difference. Feel free to "
            "reach out if you'd like some printable resources!",
        ),
        (
            alex_id,
            post_ids["How do I help my kid who's struggling with fractions?"],
            "Khan Academy fraction videos helped me a lot! They have practice problems "
            "too and it goes at your own pace.",
        ),
        (
            mr_p_id,
            post_ids["Book review: The Giver by Lois Lowry"],
            "Excellent review Priya! The ending is intentionally ambiguous — Lowry "
            "wanted readers to decide for themselves. What do you think Jonas found? "
            "There's actually a sequel called Gathering Blue set in the same world.",
        ),
        (
            alex_id,
            post_ids["Tips for writing a strong story opening?"],
            "My English teacher said to imagine the reader is standing outside the "
            "story looking in through a window. Your first line should make them "
            "want to open the door. Start with something happening, not explaining.",
        ),
    ]

    for user_id, parent_id, body in seed_replies:
        if not parent_id:
            continue
        exists = db.execute(
            "SELECT 1 FROM posts WHERE user_id=? AND parent_id=? AND body=?",
            (user_id, parent_id, body),
        ).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO posts (user_id, title, body, parent_id) VALUES (?,?,?,?)",
                (user_id, "", body, parent_id),
            )
            db.commit()
            print(f"  reply added to post {parent_id}.")

    # --- votes: upvote teacher posts from students/parents ---
    vote_targets = [
        post_ids["How to find the least common multiple — explained simply"],
        post_ids["Why does order of operations matter? (PEMDAS explained)"],
        post_ids["What actually happens during photosynthesis?"],
        post_ids["The difference between a hypothesis and a theory"],
        post_ids["Welcome to SparK — a few things to know"],
    ]
    voters = [alex_id, priya_id, mike_id]
    for voter in voters:
        for pid in vote_targets:
            exists = db.execute(
                "SELECT 1 FROM votes WHERE user_id=? AND post_id=?", (voter, pid)
            ).fetchone()
            if not exists:
                db.execute(
                    "INSERT INTO votes (user_id, post_id, value) VALUES (?,?,1)",
                    (voter, pid),
                )
                db.execute("UPDATE posts SET votes = votes + 1 WHERE id = ?", (pid,))
    db.commit()
    print("  votes added.")
    print("\nauto-seed complete.")


with app.app_context():
    db = get_db()
    while True:
        choice = menu()
        if choice == "1":
            list_users_and_posts(db)
        elif choice == "2":
            create_user(db)
        elif choice == "3":
            delete_user(db)
        elif choice == "4":
            switch_user(db)
        elif choice == "5":
            create_post(db)
        elif choice == "6":
            delete_post(db)
        elif choice == "7":
            reply_to_post(db)
        elif choice == "8":
            follow_user(db)
        elif choice == "9":
            unfollow_user(db)
        elif choice == "10":
            list_follows(db)
        elif choice == "11":
            list_topics(db)
        elif choice == "12":
            create_topic(db)
        elif choice == "13":
            delete_topic(db)
        elif choice == "14":
            reset_database(db)
        elif choice == "15":
            auto_seed(db)
        elif choice == "16":
            testing_menu()
        elif choice == "0":
            print("bye.")
            break
        else:
            print("invalid option.")
