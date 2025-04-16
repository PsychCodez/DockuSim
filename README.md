# PES2UG22CS193_PES2UG22CS208_PES2UG22CS240_Distributed_System_Cluster

# Distributed Cluster Simulation

## 📌 Overview
Simulates a Kubernetes-like cluster using Flask + Docker.
Supports:
- Node management (add/delete)
- Pod scheduling (timed or infinite)
- Node health monitoring + rescheduling
- Real-time web UI

## 🚀 How to Run
1. Clone repo
2. `cd distributed-cluster`
3. `python3 app.py`
4. Visit `http://localhost:5000`

## 🛠️ Project Structure
- `app.py` → Backend Flask app
- `index.html` → Web UI
- `heartbeat_monitor` → Tracks node health
- `docker` containers → Simulate nodes

## ✅ Features
- Dynamic pod scheduling using best-fit
- Logs visible using `docker logs <container>`
- Reschedules pods on node failure
- UI auto-refreshes

## ✍️ Author
G Dhanush R Reddy - PES2UG22CS193
G Manasa - PES2UG22CS208
J Raviteja - PES2UG22CS240
