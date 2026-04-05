# Smart Food Delivery Dispatch System

A production-quality food delivery dispatch simulation built in Python (FastAPI) and React (Vite+Tailwind). It visualizes how modern food delivery giants (like Zomato, UberEats, DoorDash) algorithmically match incoming food orders to delivery riders using advanced data structures.

---

## 🎯 Core Functionality

This application handles the full lifecycle of food delivery tracking:
1. **Adding Delivery Partners**: Drivers log into the app globally.
2. **Placing Orders**: Customers request food with assigned "Priorities". Standard orders have a `Priority=1`. VIP/Urgent orders have a `Priority=10`.
3. **Dispatch Allocation**: The backend rapidly searches the geometric space to allocate orders to the perfect driver.
4. **Order Batching**: Automatically groups multiple normal orders into a single driver's bag if they are geographically close to each other, cutting down total travel overhead.

---

## 🧠 Behind the Scenes: How Nodes Get Assigned

The magic behind the dispatching is extremely fast allocation relying heavily on multi-layered custom data structures:

### 1. The Queue & The Search (KD-Tree & Max-Heap)
When a new order is received, it isn't assigned immediately. Instead, it is thrown into a **Max-Heap Priority Queue**. This guarantees that whenever the system scans for work, the highest priority order *always* bubbles to the top in $O(\log N)$ time. 

The system pops this top order and queries our custom **2D KD-Tree**. The KD-Tree stores every single `AVAILABLE` delivery partner on a grid map. Instead of doing an $O(N)$ lookup checking every single rider's location, the KD-Tree quickly partitions the map and executes a *Nearest Neighbor Search* $O(\log N)$ to find the driver closest to the restaurant!

### 2. Batching (The Sweep & Dynamic Add-ons)
Once the optimal driver is found, the system performs an optimization sweep to build a batch. A driver's maximum bag limit is capped strictly at **3 items** (`3/3 Capacity`). Batching operates on mathematically precise spatial rules:
1. **Initial Sweep (Order-to-Order)**: When an `AVAILABLE` driver is assigned a new request, the system measures distances between that assigned primary order and all other pending orders in the queue. Any orders found within a "20-unit Euclidean radius" of the *primary order* are scooped up simultaneously. 
2. **Dynamic Latching (Centroid Path Matching)**: If a driver is already `BUSY` running a delivery route, the system intelligently calculates the geometric "Center of Mass" (Centroid) between the driver's current moving location and ALL of the restaurants currently picked-up in their bag. If a brand new standard order pops up within a 20-unit radius of this Centroid, the system securely latches it onto their existing route. This dynamically shifts the batch window proportionally toward the density-center of the routing path.
3. **The Magnet Effect (Cascading Cluster Grab)**: Every time the Centroid shifts to absorb a new order, it executes a recursive "Fixed-Point Iteration" pass over all previously unassignable orders. If the Centroid crawls close enough to grab an old order that was previously declined, it elegantly snaps it up in real-time, functioning exactly like a sweeping magnet. 

*(Note: The React Frontend features a sleek **Show/Hide Centroid Rings** UI toggle to explicitly visualize these mathematical clustering radiuses shifting and interacting live on the map!)*

### 3. VIP Pre-emption (The Zomato Case)
If a critical **Priority 10** order comes in, but *every single driver on the map is BUSY*, the system executes dynamic reassignment. 
- It finds the absolute closest `BUSY` partner.
- If that partner's bag is at maximum capacity (3 items), the algorithm evaluates what they are carrying.
- It will forcefully **rip out** the lowest-priority standard order from their bag, push it back into the general unassigned pool, and jam the new VIP Priority Order into the partner's bag instead.

---

## 🗑️ How Removals and Network Cascades Work

The simulation allows you to manually delete Nodes by right-clicking on them via the frontend map. Deleting active data mid-transit requires strict "cascading updates" to ensure system integrity:

### When an Active Partner is Removed:
If a partner's phone dies or they are removed from the system while processing deliveries:
1. The **Dispatch Service** identifies all active batches linked to them.
2. All orders physically trapped in their batch are instantly revived. Their status is flipped back to `PENDING`, their `assigned_partner_id` is wiped clean, and they are shoved back into the Max-Heap. 
3. The partner's geographic nodes are hard-deleted out of the KD-Tree and Treap tracking systems.
4. The dispatch mechanism wakes up and re-assigns the dropped orders to the *next* closest available partner.

### When an Assigned Order is Removed:
If a customer cancels their food while it's inside the driver's bag:
1. The backend surgically locates the exact batch carrying the order.
2. It slices the node out of the batch array securely and decreases the driver's `current_capacity`.
3. **The Rollback**: If dropping this order emptied the driver's bag completely (capacity hits 0), the system will flip the driver's state from `BUSY` back to `AVAILABLE`. 
4. The driver is instantly re-injected into the geographic KD-Tree, allowing them to pull in brand new orders dynamically!

---

## ⚙️ Tech Stack & Architecture

- **Frontend (UI Presentation)**: React, Typescript, Vite. Custom CSS/Tailwind visualizations rendering geographic coordinates into responsive SVG connective graphs and map grids.
- **Backend API**: Python 3, FastAPI. Serving asynchronous state endpoints.
- **Data Structures (Built from scratch)**:
  - `KDTree`: Used for Euclidean space proximity clustering and $O(\log N)$ nearest neighbor allocation.
  - `PriorityQueue`: Max-Heap logic ensuring rigorous task prioritization.
  - `Treap`: Probabilistic balanced BST augmented with Heap logic used for maintaining rider availability timestamps cleanly.

## 🚀 How to Run locally

**Start the Backend**:
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*(The backend runs on http://localhost:3000)*

**Start the Frontend**:
```bash
cd frontend
npm install
npm run dev
```
*(The map simulation runs on http://localhost:5173)*
