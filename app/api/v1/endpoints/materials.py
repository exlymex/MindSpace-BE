from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.sessions import get_db
from app.models.user import User
from app.schemas.materials import MaterialOut, CategoryOut, MaterialCreate, CategoryCreate
from app.services.material_service import MaterialService

router = APIRouter(tags=["materials"])

@router.get("/", response_model=List[MaterialOut])
async def get_materials(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all materials, optionally filtered by category"""
    return await MaterialService.get_all_materials(db, category_id)

@router.get("/{material_id}", response_model=MaterialOut)
async def get_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a material by ID"""
    material = await MaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return material

@router.post("/", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
async def create_material(
    material_data: MaterialCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new material (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return await MaterialService.create_material(db, material_data)

@router.get("/categories/", response_model=List[CategoryOut])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all categories"""
    return await MaterialService.get_all_categories(db)

@router.post("/categories/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return await MaterialService.create_category(db, category_data.name, category_data.description) 