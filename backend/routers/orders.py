"""
Orders: customers place and view their orders; staff (admin) see all orders and move them
through the statuses pending -> confirmed -> preparing -> ready -> delivered (or cancelled).

Rules enforced here
  - An order needs at least one item, each with quantity >= 1, for a product that is
    still available.
  - Prices are taken from the database, never from the request, so a customer can't
    change what they pay. Each order item stores unit_price, so later price changes don't
    rewrite old orders.
  - Customers only ever see their own orders (403 for someone else's).

Logging: each new order (id, user, number of items, total) and every status change is
logged, which gives staff an audit trail of who ordered what and when it moved.

Reference:
  SQLAlchemy (2024) "Relationship Loading Techniques" (joinedload), SQLAlchemy 2.0 documentation.
  Available at: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html (Accessed: 12 November 2026).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from logging_config import get_logger
from routers.auth import get_current_user, require_admin
import models
import schemas

log = get_logger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

VALID_STATUSES = {"pending", "confirmed", "preparing", "ready", "delivered", "cancelled"}


@router.post("", response_model=schemas.OrderOut, status_code=201)
def create_order(
    payload: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Place an order for the signed-in customer and return it with its items."""
    if not payload.items:
        log.info("Order refused - no items user_id=%s", current_user.id)
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    total = 0.0
    order_items = []

    for item in payload.items:
        # Only products that exist AND are switched on (is_available) can be ordered.
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id,
            models.Product.is_available == True,  # noqa: E712 (SQLAlchemy needs == here)
        ).first()
        if not product:
            log.info("Order refused - product %s unavailable user_id=%s", item.product_id, current_user.id)
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found or unavailable")
        if item.quantity < 1:
            log.info("Order refused - quantity %s user_id=%s", item.quantity, current_user.id)
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")

        # Price comes from the database, not the request.
        total += product.price * item.quantity
        order_items.append(
            models.OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )

    order = models.Order(
        user_id=current_user.id,
        total=round(total, 2),
        delivery_address=payload.delivery_address,
        notes=payload.notes,
        status="pending",
    )
    db.add(order)
    db.flush()  # gives the order its id so the items can point to it

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    db.commit()
    db.refresh(order)
    log.info(
        "Order placed order_id=%s user_id=%s items=%d total=R%.2f",
        order.id, current_user.id, len(order_items), order.total,
    )

    # Reload with items and their products in one query, for the response.
    return db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.product)
    ).filter(models.Order.id == order.id).first()


@router.get("", response_model=List[schemas.OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Newest first. Admins see all orders; customers see only their own."""
    query = db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.product)
    )
    if current_user.role != "admin":
        query = query.filter(models.Order.user_id == current_user.id)
    orders = query.order_by(models.Order.created_at.desc()).all()
    log.debug("Listed %d orders for user_id=%s role=%s", len(orders), current_user.id, current_user.role)
    return orders


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """One order with its items. Customers can only open their own orders."""
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product))
        .filter(models.Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.user_id != current_user.id:
        log.warning("Blocked user_id=%s from viewing order_id=%s (not theirs)", current_user.id, order_id)
        raise HTTPException(status_code=403, detail="Not your order")
    return order


@router.put("/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_id: int,
    payload: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    """Staff only: move an order to a new status (e.g. preparing -> ready)."""
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {VALID_STATUSES}")

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = payload.status
    db.commit()
    db.refresh(order)
    log.info("Order status changed order_id=%s %s -> %s by admin user_id=%s",
             order_id, old_status, order.status, admin.id)
    return order
