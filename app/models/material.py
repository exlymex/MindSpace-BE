from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime, func, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.db.base import Base

material_category = Table(
    "material_category",
    Base.metadata,
    Column("material_id", Integer, ForeignKey("materials.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, comment='article, exercise, etc.')
    image_url = Column(String(512), nullable=True)
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Зв'язки
    categories = relationship("Category", secondary=material_category, back_populates="materials")
    author = relationship("User", back_populates="materials")

    @hybrid_property
    def excerpt(self):
        """Повертає короткий уривок контенту для попереднього перегляду"""
        if len(self.content) <= 150:
            return self.content
        return self.content[:150] + "..."


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Зв'язки
    materials = relationship("Material", secondary=material_category, back_populates="categories")
