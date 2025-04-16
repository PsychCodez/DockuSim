# PES2UG22CS193_PES2UG22CS208_PES2UG22CS240_Distributed_System_Cluster

# Distributed Systems Cluster Simulation Framework

This project simulates a lightweight distributed system that mimics core functionalities of a Kubernetes-like cluster, including **node management**, **pod scheduling**, **health monitoring**, and **fault tolerance** — all using **Docker**, **Flask**, and a modern **Bootstrap-based UI**.

## 📦 Project Overview

This system acts as a teaching tool or prototype framework to understand the fundamentals of distributed system orchestration and resource scheduling. It supports:

- Adding/removing nodes (simulated using Docker containers)
- Launching pods with defined CPU requirements
- Monitoring node health via heartbeat signals
- Automatic pod rescheduling on node failure
- Visual interface for cluster overview and control
- Simulated scheduling advisor for pod placement

## 🚀 Features

| Feature | Description |
|--------|-------------|
| **Add Node** | Launches a new Docker container to simulate a node. CPU cores are assigned to represent node resources. |
| **Launch Pod** | Creates a pod that requires CPU resources. Scheduler assigns it to a suitable node using **Best-Fit** algorithm. |
| **Health Monitor** | Nodes send periodic heartbeats. Missed heartbeats trigger node failure detection. |
| **Pod Rescheduling** | Pods from failed nodes are automatically migrated to healthy nodes, if resources are available. |
| **Simulation Mode** | Simulate pod scheduling outcomes without actually launching a pod. |
| **Retry Mechanism** | Failed pod assignments are retried until successful placement. |

## 🖥️ Interface

Built using **Flask** and a responsive **Bootstrap 5 UI**, the web dashboard allows users to:

- View real-time cluster CPU usage
- Monitor live heartbeat status per node
- Launch new pods (timed or infinite)
- Simulate pod scheduling risks
- Track running containers and their pods

## 🛠️ Tech Stack

- **Flask** — Backend server & API
- **Docker SDK** — Manage containerized nodes
- **Bootstrap 5** — Responsive front-end
- **psutil / threading / uuid / json** — System operations and state handling

## 📂 Directory Structure

```plaintext
.
├── app.py               # Main Flask application with API and logic
├── index.html           # Web UI template
├── cluster_state.json   # Persistent state for nodes and pods
├── README.md            # Project documentation
```
## ⚙️ Setup Instructions

**Prerequisites**: Docker, Python 3.8+, pip

### 🔧 Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```
📦 Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
🚀 Run the application
bash
Copy
Edit
python app.py
🌐 Open in Browser
Visit: http://127.0.0.1:5000

📦 Node Simulation
Each time you add a node via the interface:

A new Ubuntu-based Docker container is spun up.

It runs a shell to simulate an idle node.

It is registered with the cluster along with its CPU allocation.

🧪 Testing and Evaluation Checklist
 Add node functionality

 Pod scheduling with CPU resource checks

 Heartbeat & failure detection

 Pod rescheduling on node death

 Cluster visualization

 Pod advisor simulation feature

🔮 Enhancements (Future Scope)
 Auto-scaling of nodes based on load

 Real-time resource graphs

 Pod networking policies and isolation

 CLI client for managing cluster remotely

## ✍️ Author
G Dhanush R Reddy - PES2UG22CS193
G Manasa - PES2UG22CS208
J Raviteja - PES2UG22CS240
