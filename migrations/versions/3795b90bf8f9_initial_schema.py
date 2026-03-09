"""initial schema

Revision ID: 3795b90bf8f9
Revises:
Create Date: 2026-03-09 01:20:49.141715

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3795b90bf8f9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.Text, unique=True, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("bio", sa.Text, server_default=""),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, unique=True, nullable=False),
        sa.Column("description", sa.Text, server_default=""),
    )

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic_id", sa.Integer, sa.ForeignKey("topics.id")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("votes", sa.Integer, server_default="0"),
        sa.Column("reply_count", sa.Integer, server_default="0"),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("posts.id")),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "votes",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("value", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("user_id", "post_id"),
    )

    op.create_table(
        "bookmarks",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("user_id", "post_id"),
    )

    op.create_table(
        "follows",
        sa.Column("follower_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("followed_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("follower_id", "followed_id"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("link", sa.Text),
        sa.Column("is_read", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # FTS tables must use raw SQL — SQLAlchemy doesn't support virtual tables
    op.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(title, body, content=posts, content_rowid=id)"
    )
    op.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS topics_fts USING fts5(name, description, content=topics, content_rowid=id)"
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS posts_fts")
    op.execute("DROP TABLE IF EXISTS topics_fts")
    op.drop_table("notifications")
    op.drop_table("follows")
    op.drop_table("bookmarks")
    op.drop_table("votes")
    op.drop_table("posts")
    op.drop_table("topics")
    op.drop_table("users")
