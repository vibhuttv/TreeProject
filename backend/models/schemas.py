from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# Global system configuration
MAX_BATCH_CAPACITY = 4  # Maximum number of orders a single delivery partner can carry

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    DELIVERED = "DELIVERED"

class PartnerStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"

class Location(BaseModel):
    x: float
    y: float

class Order(BaseModel):
    id: str
    location: Location
    priority: int # Lower number means higher priority, or vice versa? Let's say higher number = higher priority
    status: OrderStatus = OrderStatus.PENDING
    assigned_partner_id: Optional[str] = None

class Partner(BaseModel):
    id: str
    location: Location
    status: PartnerStatus = PartnerStatus.AVAILABLE
    current_capacity: int = 0  # Tracks against MAX_BATCH_CAPACITY

class Batch(BaseModel):
    id: str
    order_ids: List[str]
    partner_id: Optional[str] = None
