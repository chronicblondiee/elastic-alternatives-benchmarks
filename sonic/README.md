## Install Guide for Sonic on Kubernetes

- [Sonic GitHub Repository](https://github.com/valeriansaliou/sonic)
- [Sonic Protocol Documentation](https://github.com/valeriansaliou/sonic/blob/master/PROTOCOL.md)

**Note:** Sonic is primarily a backend service/library. Unlike many other search solutions, there isn't an official Helm chart provided by the maintainers. This guide outlines the steps to manually deploy Sonic on Kubernetes using Docker and standard Kubernetes manifests.

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Docker installed locally for building the container image.
- A container registry (like Docker Hub, GCR, ECR, etc.) to push your Sonic image.
- Persistent storage configured in your cluster.

### Steps to Install Sonic on Kubernetes

1.  **Create a Dockerfile for Sonic**
    Create a file named `Dockerfile` to build a container image for Sonic. This example uses a Rust base image.
    ```dockerfile
    # filepath: Dockerfile
    # Use an appropriate Rust base image
    FROM rust:1.77-slim as builder

    # Install build dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends build-essential pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

    # Set working directory
    WORKDIR /usr/src/sonic

    # Clone the Sonic repository (or download a specific release)
    RUN apt-get update && apt-get install -y --no-install-recommends git && \
        git clone https://github.com/valeriansaliou/sonic.git . && \
        rm -rf /var/lib/apt/lists/*

    # Build Sonic
    # Adjust target architecture if needed (e.g., --target=aarch64-unknown-linux-gnu for ARM64)
    RUN cargo build --release

    # --- Create final, smaller image ---
    FROM debian:12-slim

    # Install runtime dependencies (only libssl)
    RUN apt-get update && apt-get install -y --no-install-recommends libssl3 && rm -rf /var/lib/apt/lists/*

    # Copy the built Sonic binary from the builder stage
    COPY --from=builder /usr/src/sonic/target/release/sonic /usr/local/bin/sonic

    # Copy the default config (we'll override with a ConfigMap later)
    COPY --from=builder /usr/src/sonic/config.cfg /etc/sonic/config.cfg

    # Create directory for Sonic store
    RUN mkdir -p /var/lib/sonic/store

    # Expose the default Sonic port
    EXPOSE 1491

    # Set the entrypoint
    ENTRYPOINT ["sonic", "-c", "/etc/sonic/config.cfg"]
    ```

2.  **Build and Push the Docker Image**
    Build the Docker image and push it to your container registry. Replace `<your-registry>/<your-sonic-image>:<tag>` with your actual image name and tag.
    ```bash
    docker build -t <your-registry>/<your-sonic-image>:<tag> .
    docker push <your-registry>/<your-sonic-image>:<tag>
    ```

3.  **Create Sonic Configuration File**
    Create a local configuration file `config.cfg`. Adjust settings as needed, especially the password.
    ```ini
    # filepath: config.cfg
    # Example Sonic Configuration

    [server]
    log_level = "info"

    [channel]
    inet = "0.0.0.0:1491"
    tcp_timeout = 300
    auth_password = "YourSecurePassword" # CHANGE THIS!

    [store]
    kv_path = "/var/lib/sonic/store/kv/"
    fst_path = "/var/lib/sonic/store/fst/"

    [store.kv]
    database_path = "/var/lib/sonic/store/kv/db/"
    pool_size = 20
    write_buffer_size = 16777216 # 16MB
    max_open_files = 1000

    [store.fst]
    pool_size = 20
    graph_path = "/var/lib/sonic/store/fst/graph/"
    ```
    **Important:** Change `auth_password` to a strong, unique password.

4.  **Create Kubernetes ConfigMap**
    Create a ConfigMap in Kubernetes from your local `config.cfg`.
    ```bash
    kubectl create configmap sonic-config --from-file=config.cfg -n sonic --create-namespace
    ```
    *(Creates the ConfigMap in the `sonic` namespace, creating the namespace if needed)*

5.  **Create Kubernetes PersistentVolumeClaim (PVC)**
    Define a PVC for Sonic's data storage. Create `sonic-pvc.yaml`:
    ```yaml
    # filepath: sonic-pvc.yaml
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: sonic-data
      namespace: sonic # Ensure this matches the namespace used elsewhere
    spec:
      accessModes:
        - ReadWriteOnce # Suitable for a single Sonic instance
      resources:
        requests:
          storage: 5Gi # Adjust storage size as needed
      # Optional: Specify a storageClassName if required by your cluster
      # storageClassName: your-storage-class
    ```
    Apply the PVC manifest:
    ```bash
    kubectl apply -f sonic-pvc.yaml
    ```

6.  **Create Kubernetes Deployment**
    Define a Deployment to run your Sonic container. Create `sonic-deployment.yaml`:
    ```yaml
    # filepath: sonic-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: sonic
      namespace: sonic
      labels:
        app: sonic
    spec:
      replicas: 1 # Sonic doesn't inherently support clustering; run a single replica
      selector:
        matchLabels:
          app: sonic
      template:
        metadata:
          labels:
            app: sonic
        spec:
          containers:
          - name: sonic
            # Replace with your actual image pushed in Step 2
            image: <your-registry>/<your-sonic-image>:<tag>
            ports:
            - containerPort: 1491
              name: sonic-port
            volumeMounts:
            - name: config-volume
              mountPath: /etc/sonic # Mount the directory containing the config
            - name: data-volume
              mountPath: /var/lib/sonic/store # Mount the persistent data directory
            # Optional: Add resource requests/limits
            # resources:
            #   requests:
            #     memory: "256Mi"
            #     cpu: "100m"
            #   limits:
            #     memory: "1Gi"
            #     cpu: "500m"
          volumes:
          - name: config-volume
            configMap:
              name: sonic-config # Reference the ConfigMap created in Step 4
          - name: data-volume
            persistentVolumeClaim:
              claimName: sonic-data # Reference the PVC created in Step 5
    ```
    Apply the Deployment manifest:
    ```bash
    kubectl apply -f sonic-deployment.yaml
    ```

7.  **Create Kubernetes Service**
    Define a Service to expose the Sonic Deployment within the cluster. Create `sonic-service.yaml`:
    ```yaml
    # filepath: sonic-service.yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: sonic-service
      namespace: sonic
      labels:
        app: sonic
    spec:
      selector:
        app: sonic # Selects pods managed by the Deployment
      ports:
      - protocol: TCP
        port: 1491 # Port the service listens on
        targetPort: sonic-port # Port on the pod (references the containerPort name)
      type: ClusterIP # Exposes the service only within the cluster
    ```
    Apply the Service manifest:
    ```bash
    kubectl apply -f sonic-service.yaml
    ```

8.  **Verify Installation**
    Check the status of the deployed resources:
    ```bash
    kubectl get pods -n sonic -l app=sonic
    kubectl get svc -n sonic sonic-service
    kubectl get pvc -n sonic sonic-data
    kubectl logs deployment/sonic -n sonic # Check logs for errors
    ```
    Wait until the pod is in the `Running` state.

9.  **Accessing Sonic**
    Your applications running within the Kubernetes cluster can now connect to Sonic using the service DNS name: `sonic-service.sonic.svc.cluster.local:1491`. Use a Sonic client library for your application's language and configure it with this address and the `auth_password` you set in `config.cfg`.

    For testing from your local machine, you can use port-forwarding:
    ```bash
    kubectl port-forward svc/sonic-service 1491:1491 -n sonic
    ```
    You can then connect a local Sonic client to `localhost:1491`.

### References
- [Sonic GitHub Repository](https://github.com/valeriansaliou/sonic)
- [Sonic Protocol Documentation](https://github.com/valeriansaliou/sonic/blob/master/PROTOCOL.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)