from sqlalchemy.orm import Session
from models import Item
from schemas import ItemCreate, ItemUpdate
from typing import List, Optional
from datetime import datetime

def create_item(db: Session, item: ItemCreate) -> Item:
    """Create a new item in the database"""
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get a single item by ID"""
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
    """Get all items with pagination"""
    return db.query(Item).offset(skip).limit(limit).all()

def update_item(db: Session, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
    """Update an existing item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        update_data = item_update.dict(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            for field, value in update_data.items():
                setattr(db_item, field, value)
            db.commit()
            db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item from the database"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def search_items(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Item]:
    """Search items by name or description"""
    return db.query(Item).filter(
        (Item.name.contains(query)) | (Item.description.contains(query))
    ).offset(skip).limit(limit).all()
