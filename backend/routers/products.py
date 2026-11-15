"""
Products (the menu). Anyone can read the menu; only staff (admin) can add, edit, hide or
delete items - the website's staff dashboard (bake/admin.html) uses these endpoints.

Hiding vs deleting: a product that appears on past orders can't be deleted (that would
break those orders), so the API answers 409 and staff set is_available = false instead.
Hidden products disappear from the public menu but old orders still show them.

Logging: every change to the menu is logged with the admin's user id (audit trail).

Reference:
  FastAPI (2024) "Query Parameters and String Validations", FastAPI documentation.
  Available at: https://fastapi.tiangolo.com/tutorial/query-params-str-validations/ (Accessed: 12 November 2026).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from database import get_db
from logging_config import get_logger
from routers.auth import require_admin
import models
import schemas

log = get_logger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[schemas.ProductOut])
def list_products(
    category_id: Optional[int] = Query(None),
    available_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """The menu. ?category_id=2 filters one category; ?available_only=false includes hidden items (staff view)."""
    query = db.query(models.Product).options(joinedload(models.Product.category))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if available_only:
        query = query.filter(models.Product.is_available == True)  # noqa: E712
    products = query.all()
    log.debug("Listed %d products (category_id=%s, available_only=%s)", len(products), category_id, available_only)
    return products


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """One product with its category."""
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
    admin: models.User = Depends(require_admin),
):
    """Staff only: add a new menu item to an existing category."""
    cat = db.query(models.Category).filter(models.Category.id == payload.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    log.info("Product created product_id=%s '%s' R%.2f by admin user_id=%s",
             product.id, product.name, product.price, admin.id)
    return product


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    """Staff only: change some fields (only the fields sent are changed, e.g. just the price)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    log.info("Product updated product_id=%s fields=%s by admin user_id=%s",
             product_id, sorted(changes), admin.id)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    """Staff only: delete a product that has never been ordered (otherwise 409 - hide it instead)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # Orders keep a link to the product. Deleting it would break those orders, so hide it instead.
    on_order = db.query(models.OrderItem).filter(models.OrderItem.product_id == product_id).first()
    if on_order:
        log.info("Delete refused - product_id=%s is on existing orders", product_id)
        raise HTTPException(
            status_code=409,
            detail="This product is on existing orders, so it can't be deleted. Set it to unavailable instead.",
        )
    db.delete(product)
    db.commit()
    log.info("Product deleted product_id=%s by admin user_id=%s", product_id, admin.id)
