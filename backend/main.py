from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import random

from models.schemas import Order, Partner, Location, OrderStatus, PartnerStatus
from services.dispatch_service import DispatchService

app = FastAPI(title="Smart Food Delivery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dispatch_service = DispatchService()

class PlaceOrderRequest(BaseModel):
    x: float
    y: float
    priority: int

class AddPartnerRequest(BaseModel):
    x: float
    y: float

@app.post("/partners")
def add_partner(req: AddPartnerRequest):
    partner = Partner(
        id=str(uuid.uuid4())[:8],
        location=Location(x=req.x, y=req.y)
    )
    dispatch_service.add_partner(partner)
    return {"message": "Partner added", "partner": partner}

@app.get("/partners")
def get_partners():
    return dispatch_service.get_partners()

@app.post("/orders")
def place_order(req: PlaceOrderRequest):
    order_id = "ORD_" + str(uuid.uuid4())[:4].upper()
    order = Order(
        id=order_id,
        location=Location(x=req.x, y=req.y),
        priority=req.priority
    )
    dispatch_service.place_order(order)
    return {"message": "Order placed", "order": order}

@app.get("/orders")
def get_orders():
    return dispatch_service.get_orders()

@app.post("/partners/{partner_id}/complete")
def complete_delivery(partner_id: str):
    dispatch_service.complete_delivery(partner_id)
    return {"message": f"Partner {partner_id} completed delivery"}

@app.delete("/partners/{partner_id}")
def delete_partner(partner_id: str):
    dispatch_service.remove_partner(partner_id)
    return {"message": "Partner deleted"}

@app.delete("/orders/{order_id}")
def delete_order(order_id: str):
    dispatch_service.remove_order(order_id)
    return {"message": "Order deleted"}

@app.post("/simulation/seed")
def seed_simulation():
    # Helper to add a bunch of data
    for _ in range(5):
        dispatch_service.add_partner(Partner(
            id="P_" + str(uuid.uuid4())[:4],
            location=Location(x=random.uniform(0, 100), y=random.uniform(0, 100))
        ))
    return {"message": "Seeded partners"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
