"""${message}.

Revision: ${up_revision}
Revises: ${down_revision | comma,n}
Creation Date: ${create_date}

"""  # noqa: N999
import typing

import sqlalchemy
from alembic import op as alembic_operations
${imports if imports else ""}

revision: typing.Final = ${repr(up_revision)}
down_revision: typing.Final = ${repr(down_revision)}
branch_labels: typing.Final = ${repr(branch_labels)}
depends_on: typing.Final = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades.replace("op.", "alembic_operations.").replace("sa.", "sqlalchemy.") if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades.replace("op.", "alembic_operations.").replace("sa.", "sqlalchemy.") if downgrades else "pass"}
