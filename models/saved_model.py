"""SQLAlchemy model for the saved_models table — Phase 7B."""
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base


class SavedModel(BaseModel, Base):
    """Stores metadata for persisted sklearn model bundles (SVM, KNN, GBM)."""
    __tablename__ = "saved_models"

    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id"), nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("projects.id"), nullable=False, index=True
    )
    # Path returned by save_sklearn_model() — e.g. "sklearn_models/knn_<id>.joblib"
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # JSON list of feature column names
    feature_cols: Mapped[list] = mapped_column(JSON, nullable=False)
    # Optional human-readable label
    label: Mapped[str] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="saved_models")
    project: Mapped["Project"] = relationship(back_populates="saved_models")
