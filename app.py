import subprocess
import uuid
import time
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import docker
import psutil
import json
import os

app = Flask(__name__)
app.secret_key = 'secret_key_here'

client = docker.from_env()

total_host_cpus = psutil.cpu_count(logical=False)
MAX_NODE_CPU_ALLOCATION = int(total_host_cpus * 1.0)

nodes = []
heartbeat_status = {}
all_pods = []

# ---------------------- Node Management ----------------------

def get_total_allocated_cpu():
    return sum(node['cpu_cores'] for node in nodes)

@app.route('/')
def index():
    for node in nodes:
        node_id = node['id']
        try:
            container = client.containers.get(node['container_id'])
            if container.status != 'running':
                raise Exception("Stopped")

            if node['used_cpu'] == 0:
                node['status'] = "Healthy"
            elif node['used_cpu'] == node['cpu_cores']:
                node['status'] = "Busy"
            else:
                node['status'] = "Partially Busy"
        except:
            node['status'] = "Unhealthy"
    return render_template('index.html', nodes=nodes)

@app.route('/add_node', methods=['POST'])
def add_node():
    cpu_cores = int(request.form['cpu_cores'])

    if get_total_allocated_cpu() + cpu_cores > MAX_NODE_CPU_ALLOCATION:
        flash("Cannot add node: Exceeds system CPU capacity limit.")
        return redirect(url_for('index'))

    node_id = str(uuid.uuid4())[:8]
    container = client.containers.run(
        "ubuntu",
        command="tail -f /dev/null",  # ✅ This runs a background shell instead of sleeping
        detach=True,
        tty=True,
        labels={"type": "node", "node_id": node_id},
        name=f"node_{node_id}"
    )
    node = {
        "id": node_id,
        "container_id": container.name,
        "cpu_cores": cpu_cores,
        "used_cpu": 0,
        "pods": [],
        "heartbeat_count": 0
    }
    nodes.append(node)
    heartbeat_status[node_id] = time.time()
    save_state()
    return redirect(url_for('index'))

@app.route('/delete_node/<node_id>')
def delete_node(node_id):
    for node in nodes:
        if node['id'] == node_id:
            try:
                container = client.containers.get(node['container_id'])
                container.kill()
                container.remove()
            except:
                pass
            nodes.remove(node)
            heartbeat_status.pop(node_id, None)
            save_state()
            break
    return redirect(url_for('index'))

# ---------------------- Pod Management ----------------------

def schedule_pod_best_fit(pod_cpu):
    suitable_nodes = sorted(
        [node for node in nodes if (node['cpu_cores'] - node['used_cpu']) >= pod_cpu],
        key=lambda n: (n['cpu_cores'] - n['used_cpu']) - pod_cpu
    )
    return suitable_nodes[0] if suitable_nodes else None

@app.route('/launch_pod', methods=['POST'])
def launch_pod():
    pod_cpu = int(request.form['cpu'])
    mode = request.form['mode']
    duration = int(request.form['duration']) if mode == 'timed' else None

    node = schedule_pod_best_fit(pod_cpu)
    if not node:
        flash("No suitable node available for scheduling this pod.")
        return redirect(url_for('index'))

    pod_id = f"pod_{str(uuid.uuid4())[:8]}"

    if mode == "infinite":
        command = f"bash -c 'while true; do echo \"[INFINITE POD] Still running at $(date)\"; sleep 1; done'"
    else:
        command = f"bash -c 'for i in $(seq 1 {duration}); do echo \"[TIMED POD] Tick $i at $(date)\"; sleep 1; done'"

    subprocess.Popen([
        "docker", "exec", node['container_id'], "bash", "-c", f"{command} &"
    ])

    node['used_cpu'] += pod_cpu
    pod_info = {"id": pod_id, "cpu": pod_cpu, "mode": mode}
    node['pods'].append(pod_info)

    all_pods.append({
        "id": pod_id,
        "cpu": pod_cpu,
        "mode": mode,
        "node_id": node['id']
    })
    save_state()
    if mode == 'timed':
        threading.Thread(target=auto_cleanup_pod, args=(node['id'], pod_id, pod_cpu, duration)).start()

    print(f"Launched pod {pod_id} on node {node['id']} (CPU used: {node['used_cpu']}/{node['cpu_cores']})")
    return redirect(url_for('index'))

def auto_cleanup_pod(node_id, pod_id, cpu, duration):
    time.sleep(duration)
    for node in nodes:
        if node['id'] == node_id:
            for pod in node['pods']:
                if pod['id'] == pod_id:
                    node['used_cpu'] -= pod['cpu']
            node['pods'] = [p for p in node['pods'] if p['id'] != pod_id]
            break

# ---------------------- Heartbeat + Pod Recovery ----------------------

def heartbeat_monitor():
    while True:
        current_time = time.time()
        for node in list(nodes):
            node_id = node['id']
            container_id = node['container_id']
            try:
                container = client.containers.get(container_id)
                if container.status != 'running':
                    raise Exception("Stopped")
                heartbeat_status[node_id] = current_time
                node['heartbeat_count'] = node.get('heartbeat_count', 0) + 1
            except:
                print(f"Node {node_id} is dead. Deassigned all pods.")
                dead_pods = node['pods'][:]
                node['pods'].clear()
                node['used_cpu'] = 0

                for pod in dead_pods:
                    target_node = schedule_pod_best_fit(pod['cpu'])
                    if target_node:
                        if pod['mode'] == "infinite":
                            command = "bash -c 'trap \"echo Pod Ended (infinite)\" EXIT; echo Pod Restarted (infinite); while true; do echo running infinite pod...; sleep 1; done'"
                        else:
                            command = f"bash -c 'echo Pod Restarted (timed); for i in $(seq 1 5); do echo Timed Pod Second $i; sleep 1; done; echo Pod Ended (timed)'"

                        subprocess.Popen([
                            "docker", "exec", target_node['container_id'], "bash", "-c", command
                        ])

                        target_node['used_cpu'] += pod['cpu']
                        target_node['pods'].append(pod)

                        for p in all_pods:
                            if p['id'] == pod['id']:
                                p['node_id'] = target_node['id']

                        print(f"Pod {pod['id']} rescheduled to node {target_node['id']}")
                    else:
                        print(f"Pod {pod['id']} could not be rescheduled.")
        time.sleep(5)

threading.Thread(target=heartbeat_monitor, daemon=True).start()

# ---------------------- Heartbeat API ----------------------

@app.route('/heartbeat_data')
def heartbeat_data():
    data = []
    current_time = time.time()
    for node in nodes:
        node_id = node['id']
        last_beat = heartbeat_status.get(node_id, 0)
        heartbeat_count = node.get('heartbeat_count', 0)
        data.append({
            'id': node_id,
            'heartbeat_count': heartbeat_count,
            'last_heartbeat': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_beat)),
            'spike': current_time - last_beat < 6
        })
    return jsonify(data)
# ---------------------- Enhanced Fault Recovery ----------------------

# Track failed pods for retry
failed_pod_queue = []

def retry_pod_reschedule():
    while True:
        if failed_pod_queue:
            retry_list = failed_pod_queue[:]
            failed_pod_queue.clear()

            for pod in retry_list:
                target_node = schedule_pod_best_fit(pod['cpu'])
                if target_node:
                    print(f"Retrying pod {pod['id']} -> Found target node {target_node['id']}")

                    if pod['mode'] == "infinite":
                        command = "bash -c 'echo Pod Restarted (retry infinite); while true; do echo running infinite pod...; sleep 1; done'"
                    else:
                        command = f"bash -c 'echo Pod Restarted (retry timed); for i in $(seq 1 5); do echo Retried Timed Pod $i; sleep 1; done'"

                    subprocess.Popen([
                        "docker", "exec", target_node['container_id'], "bash", "-c", command
                    ])

                    target_node['used_cpu'] += pod['cpu']
                    target_node['pods'].append(pod)

                    for p in all_pods:
                        if p['id'] == pod['id']:
                            p['node_id'] = target_node['id']
                    print(f"Pod {pod['id']} successfully re-assigned to node {target_node['id']}")
                else:
                    print(f"Retry failed again for pod {pod['id']}. Re-adding to queue.")
                    failed_pod_queue.append(pod)

        time.sleep(10)

def enhanced_heartbeat_monitor():
    while True:
        current_time = time.time()
        for node in list(nodes):
            node_id = node['id']
            container_id = node['container_id']
            try:
                container = client.containers.get(container_id)
                if container.status != 'running':
                    raise Exception("Container stopped")
                heartbeat_status[node_id] = current_time
                node['heartbeat_count'] += 1
            except:
                print(f"[RECOVERY] Node {node_id} DEAD. Terminating container and rescheduling pods.")
                try:
                    client.containers.get(container_id).remove(force=True)
                except: pass

                dead_pods = node['pods'][:]
                node['pods'].clear()
                node['used_cpu'] = 0
                nodes.remove(node)
                heartbeat_status.pop(node_id, None)

                for pod in dead_pods:
                    target_node = schedule_pod_best_fit(pod['cpu'])
                    if target_node:
                        if pod['mode'] == "infinite":
                            command = "bash -c 'echo Pod Restarted (auto); while true; do echo running...; sleep 1; done'"
                        else:
                            command = f"bash -c 'echo Pod Restarted (auto timed); for i in $(seq 1 5); do echo Retried Pod $i; sleep 1; done'"

                        subprocess.Popen([
                            "docker", "exec", target_node['container_id'], "bash", "-c", command
                        ])

                        target_node['used_cpu'] += pod['cpu']
                        target_node['pods'].append(pod)

                        for p in all_pods:
                            if p['id'] == pod['id']:
                                p['node_id'] = target_node['id']

                        print(f"[RECOVERY] Pod {pod['id']} rescheduled to node {target_node['id']}")
                    else:
                        print(f"[RECOVERY] Pod {pod['id']} could NOT be rescheduled. Queuing for retry.")
                        failed_pod_queue.append(pod)

        time.sleep(5)

# Disable original monitor and replace with enhanced version
heartbeat_thread = threading.Thread(target=enhanced_heartbeat_monitor, daemon=True)
heartbeat_thread.start()

# Start retry mechanism in background
retry_thread = threading.Thread(target=retry_pod_reschedule, daemon=True)
retry_thread.start()

STATE_FILE = "cluster_state.json"

def save_state():
    state = {
        "nodes": nodes,
        "all_pods": all_pods
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_state():
    global nodes, all_pods
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            nodes.extend(state.get("nodes", []))
            all_pods.extend(state.get("all_pods", []))

load_state()
# ---------------------- Run ----------------------

if __name__ == '__main__':
    app.run(debug=True)
