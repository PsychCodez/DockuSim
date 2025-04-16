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

![Screenshot Placeholder](https://via.placeholder.com/800x400.png?text=Cluster+Dashboard)

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

## ✍️ Author
G Dhanush R Reddy - PES2UG22CS193
G Manasa - PES2UG22CS208
J Raviteja - PES2UG22CS240
