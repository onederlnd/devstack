from alembic import op
import sqlalchemy as sa

revision = "e68da2f64d61"
down_revision = "3795b90bf8f9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("role", sa.Text, server_default="user", nullable=False)
        )


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("role")
