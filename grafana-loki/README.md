## Install Guide for Grafana Loki on Kubernetes

- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Grafana Loki Helm Chart](https://github.com/grafana/helm-charts/tree/main/charts/loki)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).
- Persistent storage configured in your cluster (recommended for production, especially for the `simple-scalable` or `distributed` modes).
- **Optional:** S3-compatible Object Storage (recommended for production storage backend).

### Steps to Install Grafana Loki on Kubernetes using Helm

1.  **Add the Grafana Helm Repository**
    Add the official Grafana Helm chart repository:
    ```bash
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    ```

2.  **Install Grafana Loki**
    Deploy Loki to your Kubernetes environment. The Helm chart supports different deployment modes (`monolithic`, `simple-scalable`, `distributed`). The default is often `simple-scalable`.

    *   **Default Installation (Simple Scalable, No Persistence/Object Storage):**
        ```bash
        # Installs Loki in simple-scalable mode using filesystem storage (ephemeral).
        helm install loki grafana/loki \
          -n loki --create-namespace
        ```
        *Note: This default setup is **not recommended for production** due to ephemeral storage.*

    *   **Installation with Custom Values (Recommended):**
        Create a `values.yaml` file to configure persistence, object storage, deployment mode, resources, etc. See step 6 for an example.
        ```bash
        helm install loki grafana/loki -f values.yaml -n loki --create-namespace
        ```

3.  **Verify Loki Installation**
    Check the status of the deployed Loki pods in the `loki` namespace:
    ```bash
    kubectl get pods -n loki -l app.kubernetes.io/instance=loki
    ```
    Wait until all relevant pods (e.g., ingester, distributor, querier, query-frontend, gateway) are in the `Running` state. The exact pods depend on the chosen deployment mode.

4.  **Access Loki**
    Loki's API is typically exposed via a gateway service (default port 3100). Use port-forwarding for quick access:
    ```bash
    # Find the gateway service name (might vary slightly based on release name/chart version)
    kubectl get svc -n loki -l app.kubernetes.io/name=loki,app.kubernetes.io/component=gateway

    # Assuming the service is named 'loki-gateway'
    kubectl port-forward svc/loki-gateway 3100:80 -n loki
    # Note: The service port might be 80, forwarding to local port 3100
    ```
    You can now query Loki's API at `http://localhost:3100`.
    ```bash
    # Check readiness
    curl http://localhost:3100/ready

    # Example query (requires logs to be sent to Loki)
    # curl -G -s "http://localhost:3100/loki/api/v1/query_range" --data-urlencode 'query={job="mylogjob"}'
    ```
    For production, use a LoadBalancer or Ingress controller. You'll typically query Loki via Grafana or other clients like LogCLI.

5.  **Sending Logs to Loki**
    Loki itself doesn't collect logs. You need a log shipping agent like Promtail, Fluentd, or Fluent Bit configured to send logs to the Loki distributor or gateway service (e.g., `http://loki-gateway.loki.svc.cluster.local:80` or `http://loki-distributor.loki.svc.cluster.local:3100`). The Grafana Helm repository also includes a Promtail chart: `grafana/promtail`.

6.  **Custom Configuration (Example)**
    Create `values.yaml` for a more robust setup, e.g., using MinIO for storage.

    **Example `values.yaml` (Simple Scalable with MinIO):**
    ```yaml
    # filepath: values.yaml

    # Keep the simple-scalable mode (or choose 'monolithic' or 'distributed')
    # deploymentMode: SimpleScalable

    loki:
      # Configure storage backend (replace filesystem with S3/MinIO)
      storage:
        type: 's3'
        s3:
          # Replace with your S3-compatible endpoint
          endpoint: "http://minio.minio-namespace.svc.cluster.local:9000" # Example internal MinIO endpoint
          # Replace with your bucket name
          bucketnames: "loki-data"
          # Replace with your access key ID
          accessKeyId: "YOUR_ACCESS_KEY_ID"
          # Replace with your secret access key (use secrets in production)
          secretAccessKey: "YOUR_SECRET_ACCESS_KEY"
          # Set region if required (e.g., "us-east-1")
          # region: ""
          s3ForcePathStyle: true # Often needed for MinIO
          insecure: true # Set to false if using HTTPS with valid certs

    # Enable persistence for ingester/querier state if needed (depends on mode/setup)
    # ingester:
    #   persistence:
    #     enabled: true
    #     size: 10Gi
    #     storageClass: "your-storage-class"

    # Adjust resources as needed
    # ingester:
    #   resources:
    #     requests:
    #       cpu: 500m
    #       memory: 1Gi
    # distributor:
    #   resources: { ... }
    # querier:
    #   resources: { ... }

    # Refer to the chart's default values.yaml for all options:
    # https://github.com/grafana/helm-charts/blob/main/charts/loki/values.yaml
    ```
    Install or upgrade using this file:
    ```bash
    # Install
    helm install loki grafana/loki -f values.yaml -n loki --create-namespace

    # Upgrade an existing release
    helm upgrade loki grafana/loki -f values.yaml -n loki
    ```
    **Security Note:** Manage object storage credentials securely using Kubernetes secrets in production environments.

### References
- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Grafana Loki Helm Chart Repository](https://github.com/grafana/helm-charts/tree/main/charts/loki)
- [Grafana Loki Helm Chart `values.yaml`](https://github.com/grafana/helm-charts/blob/main/charts/loki/values.yaml)
- [Promtail Documentation (for log shipping)](https://grafana.com/docs/loki/latest/clients/promtail/)