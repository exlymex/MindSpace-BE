from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.material import Material, Category
from app.schemas.materials import MaterialCreate

class MaterialService:
    @staticmethod
    async def get_all_materials(db: AsyncSession, category_id: Optional[int] = None):
        """Get all materials, optionally filtered by category"""
        query = select(Material).options(selectinload(Material.categories))
        
        if category_id:
            query = query.join(Material.categories).filter(Category.id == category_id)
            
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_material_by_id(db: AsyncSession, material_id: int):
        """Get a material by ID"""
        query = select(Material).where(Material.id == material_id).options(selectinload(Material.categories))
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create_material(db: AsyncSession, material_data: MaterialCreate):
        """Create a new material"""
        # Get categories
        category_ids = material_data.category_ids
        query = select(Category).where(Category.id.in_(category_ids))
        result = await db.execute(query)
        categories = result.scalars().all()
        
        # Create material
        material_dict = material_data.dict(exclude={"category_ids"})
        material = Material(**material_dict, categories=categories)
        
        db.add(material)
        await db.commit()
        await db.refresh(material)
        return material

    @staticmethod
    async def get_all_categories(db: AsyncSession):
        """Get all categories"""
        query = select(Category)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_category(db: AsyncSession, name: str, description: Optional[str] = None):
        """Create a new category"""
        category = Category(name=name, description=description)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category 