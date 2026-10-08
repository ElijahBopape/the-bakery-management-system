from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from database import get_db
from routers.auth import get_current_user, require_admin
import models
import schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[schemas.ProductOut])
def list_products(
    category_id: Optional[int] = Query(None),
    available_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    query = db.query(models.Product).options(joinedload(models.Product.category))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if available_only:
        query = query.filter(models.Product.is_available == True)
    return query.all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.category))
        .filter(models.Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(
    payload: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    cat = db.query(models.Category).filter(models.Category.id == payload.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # Orders keep a link to the product. Deleting it would break those orders, so hide it instead.
    on_order = db.query(models.OrderItem).filter(models.OrderItem.product_id == product_id).first()
    if on_order:
        raise HTTPException(
            status_code=409,
            detail="This product is on existing orders, so it can't be deleted. Set it to unavailable instead.",
        )
    db.delete(product)
    db.commit()
