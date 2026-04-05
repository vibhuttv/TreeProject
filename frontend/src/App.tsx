import { useEffect, useState } from 'react';
import type { MouseEvent } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';
const MAX_CAP = 4; // Mirrors backend MAX_BATCH_CAPACITY in models/schemas.py

type Location = { x: number; y: number };

type Partner = {
  id: string;
  location: Location;
  status: string;
  current_capacity: number;
};

type Order = {
  id: string;
  location: Location;
  priority: number;
  status: string;
  assigned_partner_id: string | null;
};

function App() {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [clickMode, setClickMode] = useState<'PARTNER' | 'ORDER_NORMAL' | 'ORDER_PRIORITY'>('PARTNER');
  const [showCentroids, setShowCentroids] = useState(true);

  const fetchState = async () => {
    try {
      const [pRes, oRes] = await Promise.all([
        axios.get(`${API_URL}/partners`),
        axios.get(`${API_URL}/orders`)
      ]);
      setPartners(pRes.data);
      setOrders(oRes.data);
    } catch (e) {
      console.error("Error fetching state");
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSeed = async () => {
    await axios.post(`${API_URL}/simulation/seed`);
    fetchState();
  };

  const handleClearAll = async () => {
    if (window.confirm("Are you sure you want to clear the entire map?")) {
      await axios.post(`${API_URL}/simulation/reset`);
      fetchState();
    }
  };

  const handleMapClick = async (e: MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    if (clickMode === 'PARTNER') {
      await axios.post(`${API_URL}/partners`, { x, y });
    } else {
      const priority = clickMode === 'ORDER_PRIORITY' ? 10 : 1;
      await axios.post(`${API_URL}/orders`, { x, y, priority });
    }
    fetchState();
  };

  const handleDeletePartner = async (e: MouseEvent, id: string) => {
    e.stopPropagation();
    await axios.delete(`${API_URL}/partners/${id}`);
    fetchState();
  };

  const handleDeleteOrder = async (e: MouseEvent, id: string) => {
    e.stopPropagation();
    await axios.delete(`${API_URL}/orders/${id}`);
    fetchState();
  };

  const handleComplete = async (partnerId: string) => {
    await axios.post(`${API_URL}/partners/${partnerId}/complete`);
    fetchState();
  };

  return (
    <div className="flex flex-col h-screen p-6 gap-6">
      <header className="flex justify-between items-center bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent">
          Smart Food Delivery Simulation
        </h1>
        <div className="flex gap-3 bg-slate-900 p-1 rounded-lg border border-slate-700">
          <button
            onClick={() => setClickMode('PARTNER')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${clickMode === 'PARTNER' ? 'bg-teal-600 shadow-lg shadow-teal-500/20' : 'hover:bg-slate-800'}`}
          >
            + Partner
          </button>
          <button
            onClick={() => setClickMode('ORDER_NORMAL')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${clickMode === 'ORDER_NORMAL' ? 'bg-blue-600 shadow-lg shadow-blue-500/20' : 'hover:bg-slate-800'}`}
          >
            + Normal Order
          </button>
          <button
            onClick={() => setClickMode('ORDER_PRIORITY')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${clickMode === 'ORDER_PRIORITY' ? 'bg-orange-600 shadow-lg shadow-orange-500/20' : 'hover:bg-slate-800'}`}
          >
            + Priority Order
          </button>
        </div>
        <div className="flex ml-auto gap-3">
          <button
            onClick={() => setShowCentroids(!showCentroids)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors border ${showCentroids ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400' : 'bg-slate-700 hover:bg-slate-600 border-slate-600 text-slate-300'}`}
          >
            {showCentroids ? 'Hide Centroid Rings' : 'Show Centroid Rings'}
          </button>
          <button
            onClick={handleClearAll}
            className="px-4 py-2 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white rounded-lg font-medium transition-colors border border-red-500/50"
          >
            Clear All
          </button>
          <button
            onClick={handleSeed}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors border border-slate-600 text-slate-200"
          >
            Seed Random Partners
          </button>
        </div>
      </header>

      <div className="flex flex-1 gap-6 min-h-0">
        <div
          onClick={handleMapClick}
          className="w-2/3 bg-slate-800 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden map-grid cursor-crosshair"
        >
          <div className="absolute inset-0 p-4 font-mono text-sm text-slate-500 pointer-events-none">
            Spatial View (100x100 Grid)
          </div>
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {orders.filter(o => o.status === 'ASSIGNED' && o.assigned_partner_id).map(o => {
              const partner = partners.find(p => p.id === o.assigned_partner_id);
              if (!partner) return null;
              return (
                <line
                  key={`edge-${o.id}`}
                  x1={`${partner.location.x}%`}
                  y1={`${partner.location.y}%`}
                  x2={`${o.location.x}%`}
                  y2={`${o.location.y}%`}
                  stroke={o.priority >= 9 ? '#f97316' : '#0ea5e9'}
                  strokeWidth="2"
                  strokeDasharray="6,6"
                  opacity="0.5"
                  className="animate-pulse"
                />
              );
            })}

            {/* Centroid Batch Catchment Circles — exact 20-unit radius matching backend threshold */}
            {showCentroids && partners.map(p => {
              if (p.status !== 'BUSY' || p.current_capacity >= MAX_CAP) return null;

              // Build all batch nodes: partner + assigned orders
              const batchNodes = [{ x: p.location.x, y: p.location.y }];
              orders.filter(o => o.status === 'ASSIGNED' && o.assigned_partner_id === p.id)
                    .forEach(o => batchNodes.push({ x: o.location.x, y: o.location.y }));

              // Euclidean centroid — mirrors backend: centroid_x = total_x / nodes_count
              const centroidX = batchNodes.reduce((s, n) => s + n.x, 0) / batchNodes.length;
              const centroidY = batchNodes.reduce((s, n) => s + n.y, 0) / batchNodes.length;

              // Backend checks: dist_to_centroid <= 20.0
              // Map is 100x100 units, SVG uses %, so 20 units = 20%
              const CATCH_RADIUS = 20;

              return (
                <g key={`catch-centroid-${p.id}`}>
                  {/* Exact batchable zone: any order placed inside this circle will latch */}
                  <circle
                    cx={`${centroidX}%`}
                    cy={`${centroidY}%`}
                    r={`${CATCH_RADIUS}%`}
                    fill="rgba(234,179,8,0.05)"
                    stroke="rgba(234,179,8,0.35)"
                    strokeWidth="1.5"
                    strokeDasharray="5,4"
                  />
                  {/* Centroid marker dot */}
                  <circle
                    cx={`${centroidX}%`}
                    cy={`${centroidY}%`}
                    r="0.6%"
                    fill="rgba(234,179,8,0.6)"
                  />
                </g>
              );
            })}
          </svg>
          {/* Map Components */}
          {partners.map(p => (
            <div
              key={p.id}
              className={`absolute w-6 h-6 -ml-3 -mt-3 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500 shadow-lg cursor-pointer hover:scale-110 ${p.status === 'AVAILABLE' ? 'bg-teal-500 shadow-teal-500/50 text-white' : p.current_capacity === MAX_CAP ? 'bg-purple-600 shadow-purple-600/50 text-white ring-2 ring-purple-400' : 'bg-yellow-500 shadow-yellow-500/50 text-slate-900'}`}
              style={{ left: `${p.location.x}%`, top: `${p.location.y}%` }}
              title={`Partner ${p.id} | Cap: ${p.current_capacity}. Click = Complete. Right-Click = Delete`}
              onClick={(e) => { e.stopPropagation(); if (p.status === 'BUSY') handleComplete(p.id); }}
              onContextMenu={(e) => { e.preventDefault(); handleDeletePartner(e, p.id); }}
            >
              P
            </div>
          ))}
          {orders.map(o => o.status !== 'DELIVERED' && (
            <div
              key={o.id}
              className={`absolute w-4 h-4 -ml-2 -mt-2 rounded-sm transition-all duration-500 animate-pulse ${o.priority >= 9 ? 'bg-orange-500' : 'bg-blue-500'}`}
              style={{ left: `${o.location.x}%`, top: `${o.location.y}%` }}
              title={`Order ${o.id} | Priority ${o.priority}. Click to delete`}
              onClick={(e) => handleDeleteOrder(e, o.id)}
              onContextMenu={(e) => { e.preventDefault(); handleDeleteOrder(e, o.id); }}
            ></div>
          ))}
        </div>

        <div className="w-1/3 flex flex-col gap-6 overflow-y-auto pr-2">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 text-slate-300">Active Partners</h2>
            <div className="flex flex-col gap-2">
              {partners.length === 0 && <span className="text-slate-500 italic">No partners available</span>}
              {partners.map(p => (
                <div key={p.id} className="flex justify-between items-center p-3 rounded-lg bg-slate-750 border border-slate-700 hover:bg-slate-700 transition">
                  <div>
                    <div className="font-mono text-sm">{p.id}</div>
                    <div className="text-xs text-slate-400">Cap: {p.current_capacity}/{MAX_CAP}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-bold ${p.status === 'AVAILABLE' ? 'bg-teal-500/20 text-teal-400' : p.current_capacity === MAX_CAP ? 'bg-purple-500/20 text-purple-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                      {p.current_capacity === MAX_CAP ? 'FULL' : p.status}
                    </span>
                    {p.status === 'BUSY' && (
                      <button
                        onClick={(e) => { e.stopPropagation(); handleComplete(p.id); }}
                        className="text-xs bg-slate-600 hover:bg-slate-500 px-2 py-1 rounded"
                      >
                        Complete
                      </button>
                    )}
                    <button onClick={(e) => handleDeletePartner(e, p.id)} className="text-xs bg-red-600/20 text-red-400 flex items-center justify-center w-6 h-6 hover:bg-red-600 hover:text-white rounded transition-colors tooltip" title="Delete">✕</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 text-slate-300">Orders Status</h2>
            <div className="flex flex-col gap-2">
              {orders.length === 0 && <span className="text-slate-500 italic">No orders yet</span>}
              {orders.slice().reverse().map(o => (
                <div key={o.id} className="flex justify-between items-center p-3 rounded-lg bg-slate-750 border border-slate-700">
                  <div className="flex gap-2 items-center">
                    <div className={`w-2 h-2 rounded-full ${o.priority >= 9 ? 'bg-orange-500' : 'bg-blue-500'}`} />
                    <span className="font-mono text-sm">{o.id}</span>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">{o.status}</span>
                      <button onClick={(e) => handleDeleteOrder(e, o.id)} className="text-xs text-red-400 hover:bg-red-600 hover:text-white flex items-center justify-center w-5 h-5 rounded transition-colors">✕</button>
                    </div>
                    {o.assigned_partner_id && <span className="text-xs text-slate-500">Assigned: {o.assigned_partner_id}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
