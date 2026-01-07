"""Import all models for Alembic."""
# This file ensures all models are imported for Alembic migrations
# Import this in alembic/env.py

from app.db.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.subtask import Subtask  # noqa: F401
from app.models.submission import Submission  # noqa: F401
from app.models.artifact import Artifact, ArtifactPurchase  # noqa: F401
from app.models.dispute import Dispute  # noqa: F401
