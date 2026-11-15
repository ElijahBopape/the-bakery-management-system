"""
Menu categories (Frappes, Cakes, Drinks & Extras). Read-only for everyone; the categories
themselves are created by seed.py. The website and app use them for the menu filter tabs.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from logging_config import get_logger
import models
import schemas

log = get_logger(__name__)
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """All menu categories."""
    cats = db.query(models.Category).all()
    log.debug("Listed %d categories", len(cats))
    return cats


@router.get("/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """One category by id (404 if it does not exist)."""
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat
