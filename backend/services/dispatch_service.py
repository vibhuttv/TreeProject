import math
import uuid
from typing import Dict, List, Optional
from models.schemas import Order, Partner, OrderStatus, PartnerStatus, Batch
from data_structures.kd_tree import KDTree
from data_structures.priority_queue import PriorityQueue
from data_structures.treap import Treap

class DispatchService:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.partners: Dict[str, Partner] = {}
        self.batches: Dict[str, Batch] = {}
        
        # Spatial indexing for partners
        self.partner_tree = KDTree()
        
        # Priority queue for prioritizing higher important orders (e.g., higher value means higher priority)
        # Assuming order value is passed as priority. 10 is high priority, 1 is low.
        self.priority_queue = PriorityQueue()
        
        # Treap for specific ordering/management, e.g., partner availability capacity
        self.partner_treap = Treap()
        
    def add_partner(self, partner: Partner):
        self.partners[partner.id] = partner
        if partner.status == PartnerStatus.AVAILABLE:
            self.partner_tree.insert((partner.location.x, partner.location.y), partner)
            self.partner_treap.insert(hash(partner.id), partner)
        self._process_dispatch()
            
    def get_partners(self):
        return [p.model_dump() for p in self.partners.values()]

    def get_orders(self):
        # We also want to return orders in priority queue?
        return [o.model_dump() for o in self.orders.values()]

    def place_order(self, order: Order):
        self.orders[order.id] = order
        # Add to priority queue
        self.priority_queue.push(order.priority, order)
        self._process_dispatch()
        
    def _process_dispatch(self):
        made_progress = True
        while made_progress:
            made_progress = False
            unassignable_orders = []
            
            while not self.priority_queue.is_empty():
                order: Order = self.priority_queue.peek()
                nearest_partner = self.partner_tree.nearest_neighbor((order.location.x, order.location.y))
                
                if nearest_partner and nearest_partner.status == PartnerStatus.AVAILABLE:
                    self.priority_queue.pop()
                    order.status = OrderStatus.ASSIGNED
                    order.assigned_partner_id = nearest_partner.id
                    
                    batched_orders = [order]
                    all_pending = self.priority_queue.to_list()
                    
                    new_pq = PriorityQueue()
                    for pending_order in all_pending:
                        dist = math.hypot(pending_order.location.x - order.location.x, 
                                          pending_order.location.y - order.location.y)
                        if dist <= 20.0 and len(batched_orders) < 3 and pending_order.status == OrderStatus.PENDING:
                            batched_orders.append(pending_order)
                        else:
                            new_pq.push(pending_order.priority, pending_order)
                            
                    self.priority_queue = new_pq
                    
                    nearest_partner.status = PartnerStatus.BUSY
                    nearest_partner.current_capacity += len(batched_orders)
                    
                    self.partner_tree.remove(nearest_partner.id)
                    self.partner_treap.remove(hash(nearest_partner.id))
                    
                    batch_order_ids = []
                    for b_order in batched_orders:
                        b_order.status = OrderStatus.ASSIGNED
                        b_order.assigned_partner_id = nearest_partner.id
                        batch_order_ids.append(b_order.id)
                        
                    batch = Batch(id=str(uuid.uuid4()), order_ids=batch_order_ids, partner_id=nearest_partner.id)
                    self.batches[batch.id] = batch
                    made_progress = True
                else:
                    reassigned = False
                    best_partner = None
                    best_dist = float('inf')
                    for p in self.partners.values():
                        if p.status == PartnerStatus.BUSY:
                            # Calculate Euclidean geometric centroid context of the batch
                            total_x = p.location.x
                            total_y = p.location.y
                            nodes_count = 1
                            
                            for b in self.batches.values():
                                if b.partner_id == p.id:
                                    for oid in b.order_ids:
                                        existing_order = self.orders.get(oid)
                                        if existing_order:
                                            total_x += existing_order.location.x
                                            total_y += existing_order.location.y
                                            nodes_count += 1
                                    break
                                    
                            centroid_x = total_x / nodes_count
                            centroid_y = total_y / nodes_count
                            
                            dist_to_centroid = math.hypot(centroid_x - order.location.x, centroid_y - order.location.y)
                            
                            if dist_to_centroid < best_dist:
                                best_dist = dist_to_centroid
                                best_partner = p
                    
                    if best_partner:
                        target_batch = None
                        for b in self.batches.values():
                            if b.partner_id == best_partner.id:
                                target_batch = b
                                break
                                
                        if target_batch:
                            if best_dist <= 20.0 and best_partner.current_capacity < 3:
                                self.priority_queue.pop()
                                order.status = OrderStatus.ASSIGNED
                                order.assigned_partner_id = best_partner.id
                                target_batch.order_ids.append(order.id)
                                best_partner.current_capacity += 1
                                reassigned = True
                                made_progress = True
                            elif order.priority >= 9:
                                if best_partner.current_capacity < 3:
                                    self.priority_queue.pop()
                                    order.status = OrderStatus.ASSIGNED
                                    order.assigned_partner_id = best_partner.id
                                    target_batch.order_ids.append(order.id)
                                    best_partner.current_capacity += 1
                                    reassigned = True
                                    made_progress = True
                                else:
                                    lowest_order = None
                                    lowest_prio = float('inf')
                                    for oid in target_batch.order_ids:
                                        o = self.orders.get(oid)
                                        if o and o.priority < lowest_prio:
                                            lowest_prio = o.priority
                                            lowest_order = o
                                    
                                    if lowest_order and lowest_order.priority < order.priority:
                                        self.priority_queue.pop()
                                        target_batch.order_ids.remove(lowest_order.id)
                                        lowest_order.status = OrderStatus.PENDING
                                        lowest_order.assigned_partner_id = None
                                        self.priority_queue.push(lowest_order.priority, lowest_order)
                                        
                                        order.status = OrderStatus.ASSIGNED
                                        order.assigned_partner_id = best_partner.id
                                        target_batch.order_ids.append(order.id)
                                        reassigned = True
                                        made_progress = True
    
                    if not reassigned:
                        popped_order = self.priority_queue.pop()
                        unassignable_orders.append(popped_order)
                        
            # Put back all orders that couldn't be routed or dynamically batched
            for u_ord in unassignable_orders:
                self.priority_queue.push(u_ord.priority, u_ord)

    def complete_delivery(self, partner_id: str):
        partner = self.partners.get(partner_id)
        if partner:
            partner.status = PartnerStatus.AVAILABLE
            partner.current_capacity = 0
            # Update orders
            for b in self.batches.values():
                if b.partner_id == partner_id:
                    for oid in b.order_ids:
                        self.orders[oid].status = OrderStatus.DELIVERED
            # Re-add to structures
            self.partner_tree.insert((partner.location.x, partner.location.y), partner)
            self.partner_treap.insert(hash(partner.id), partner)
            self._process_dispatch()

    def remove_partner(self, partner_id: str):
        if partner_id in self.partners:
            batches_to_remove = []
            for batch_id, batch in self.batches.items():
                if batch.partner_id == partner_id:
                    batches_to_remove.append(batch_id)
                    for oid in batch.order_ids:
                        if oid in self.orders:
                            order = self.orders[oid]
                            if order.status != OrderStatus.DELIVERED:
                                order.status = OrderStatus.PENDING
                                order.assigned_partner_id = None
                                self.priority_queue.push(order.priority, order)
                                
            for bid in batches_to_remove:
                del self.batches[bid]

            self.partner_tree.remove(partner_id)
            self.partner_treap.remove(hash(partner_id))
            del self.partners[partner_id]
            self._process_dispatch()

    def remove_order(self, order_id: str):
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status == OrderStatus.PENDING:
                all_pending = self.priority_queue.to_list()
                self.priority_queue = PriorityQueue()
                for pending_order in all_pending:
                    if pending_order.id != order_id:
                        self.priority_queue.push(pending_order.priority, pending_order)
            elif order.status == OrderStatus.ASSIGNED:
                partner_id = order.assigned_partner_id
                if partner_id and partner_id in self.partners:
                    partner = self.partners[partner_id]
                    for batch in self.batches.values():
                        if order_id in batch.order_ids:
                            batch.order_ids.remove(order_id)
                            partner.current_capacity -= 1
                            if partner.current_capacity <= 0:
                                partner.current_capacity = 0
                                partner.status = PartnerStatus.AVAILABLE
                                self.partner_tree.insert((partner.location.x, partner.location.y), partner)
                                self.partner_treap.insert(hash(partner.id), partner)
                            break
            del self.orders[order_id]
            self._process_dispatch()

    def reset_simulation(self):
        """Wipes all state and reinstantiates the data structures."""
        self.orders.clear()
        self.partners.clear()
        self.batches.clear()
        self.priority_queue = PriorityQueue()
        self.partner_tree = KDTree()
        self.partner_treap = Treap()
