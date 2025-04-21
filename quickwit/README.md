## Install Guide for Quickwit on Kubernetes

- [Quickwit Documentation](https://quickwit.io/docs/)
- [Quickwit Helm Chart](https://github.com/quickwit-oss/helm-charts)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).
- **S3-compatible Object Storage:** Quickwit requires object storage (like AWS S3, MinIO, Google Cloud Storage, Azure Blob Storage) for storing indexes and data. You need the endpoint, bucket name, access key, and secret key for your storage.

### Steps to Install Quickwit on Kubernetes using Helm

1.  **Add the Quickwit Helm Repository**
    Add the official Quickwit Helm chart repository:
    ```bash
    helm repo add quickwit https://quickwit-oss.github.io/helm-charts
    helm repo update
    ```

2.  **Configure Object Storage**
    Quickwit relies heavily on object storage. You **must** configure this. Create a `values.yaml` file to provide your object storage details.

    **Example `values.yaml` for MinIO/S3:**
    ```yaml
    # filepath: values.yaml
    # --- IMPORTANT: Configure your object storage ---
    config:
      # Default storage used for indexes, metastore, etc.
      default_object_storage:
        s3:
          # Replace with your S3-compatible endpoint
          # For AWS S3 in us-east-1, you might omit endpoint or use: https://s3.us-east-1.amazonaws.com
          endpoint: "http://minio.minio-namespace.svc.cluster.local:9000" # Example internal MinIO endpoint
          # Replace with your bucket name
          bucket: "quickwit-data"
          # Set region if required by your provider (e.g., "us-east-1")
          # region: ""
          # Set virtual_host_style to true if using path-style access (often needed for MinIO)
          virtual_host_style: false

      # Credentials for the object storage
      credentials:
        s3:
          # Replace with your access key ID
          access_key_id: "YOUR_ACCESS_KEY_ID"
          # Replace with your secret access key
          # Consider using Kubernetes secrets for production: https://quickwit.io/docs/configuration/credentials#kubernetes-secrets
          secret_access_key: "YOUR_SECRET_ACCESS_KEY"

    # --- Optional: Adjust resources, replicas, etc. ---
    # searcher:
    #   replicaCount: 2
    #   resources:
    #     requests:
    #       cpu: 500m
    #       memory: 1Gi
    #     limits:
    #       cpu: 1
    #       memory: 2Gi

    # indexer:
    #   replicaCount: 1
    #   resources:
    #     requests:
    #       cpu: 500m
    #       memory: 1Gi
    #     limits:
    #       cpu: 1
    #       memory: 2Gi

    # janitor:
    #   resources: {} # Adjust if needed

    # metastore:
    #   resources: {} # Adjust if needed

    # web_ui:
    #   resources: {} # Adjust if needed

    # Refer to the chart's default values.yaml for all options:
    # https://github.com/quickwit-oss/helm-charts/blob/main/charts/quickwit/values.yaml
    ```
    **Important:** Replace placeholder values (endpoint, bucket, keys) with your actual object storage details. For production, manage credentials securely using Kubernetes secrets as documented by Quickwit.

3.  **Install Quickwit Using Helm**
    Deploy Quickwit to your Kubernetes cluster using the Helm chart and your custom `values.yaml`:
    ```bash
    helm install quickwit quickwit/quickwit -f values.yaml -n quickwit --create-namespace
    ```
    *(Installs into the `quickwit` namespace, creating it if it doesn't exist)*

4.  **Verify the Installation**
    Check the status of the deployed pods in the `quickwit` namespace:
    ```bash
    kubectl get pods -n quickwit
    ```
    Look for pods related to the `quickwit` release (searcher, indexer, metastore, web-ui, janitor). They should eventually be in the `Running` state. This might take a few minutes.

5.  **Access Quickwit**
    To interact with the Quickwit UI and API (default port 7280), expose the `quickwit-web-ui` service. Use port-forwarding for quick access:
    ```bash
    kubectl port-forward svc/quickwit-web-ui 7280:7280 -n quickwit
    ```
    You can now access the Quickwit UI at `http://localhost:7280`.

    For production environments, configure a LoadBalancer or Ingress controller to expose the service.

### References
- [Quickwit Documentation](https://quickwit.io/docs/)
- [Quickwit Helm Chart Repository](https://github.com/quickwit-oss/helm-charts)
- [Quickwit Helm Chart `values.yaml`](https://github.com/quickwit-oss/helm-charts/blob/main/charts/quickwit/values.yaml)
- [Quickwit Configuration Options](https://quickwit.io/docs/reference/configuration)