## Install Guide
- [Typesense Installation Documentation](https://typesense.org/docs/guide/install-typesense.html)
- [Typesense Kubernetes Operator (Community)](https://github.com/sai3010/Typesense-Kubernetes-Operator)
- [Typesense Helm Chart (Community)](https://github.com/typesense/helm-chart)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).

### Steps to Install Typesense on Kubernetes using Helm

1.  **Add the Typesense Helm Repository**
    Add the official Typesense Helm chart repository:
    ```bash
    helm repo add typesense https://typesense.github.io/helm-chart/
    helm repo update
    ```

2.  **Install Typesense Using Helm**
    Deploy Typesense to your Kubernetes cluster using the Helm chart.

    *   **Default Installation (Single Node):**
        ```bash
        # Note: Requires a Typesense API Key. Generate one securely.
        helm install typesense typesense/typesense \
          --set apiKey=<YOUR_TYPESENSE_API_KEY> \
          --set existingSecret=typesense-api-key # Optional: Use if you created a secret manually
        ```
        *Replace `<YOUR_TYPESENSE_API_KEY>` with your actual key.*

    *   **Installation with Custom Values:**
        Create a `values.yaml` file to override default settings (e.g., for High Availability, persistence). See step 5 for an example.
        ```bash
        # Ensure apiKey is set in your values.yaml or via --set
        helm install typesense typesense/typesense -f values.yaml
        ```

3.  **Verify the Installation**
    Check the status of the deployed pods:
    ```bash
    kubectl get pods
    ```
    Look for pods related to the `typesense` release. They should be in the `Running` state.

4.  **Access Typesense**
    To interact with the Typesense API (default port 8108), expose the service. Use port-forwarding for quick access:
    ```bash
    kubectl port-forward svc/typesense 8108:8108
    ```
    You can now access the Typesense API at `http://localhost:8108`. Use your API key for authentication.
    ```bash
    curl -H "X-TYPESENSE-API-KEY: <YOUR_TYPESENSE_API_KEY>" http://localhost:8108/health
    ```
    For production, use a LoadBalancer or Ingress controller.

5.  **Custom Configuration (Optional)**
    Create a `values.yaml` file to customize your deployment. Example for enabling High Availability (HA) and persistence:
    ```yaml
    # filepath: values.yaml
    # Example custom values for Typesense Helm chart

    # --- IMPORTANT: Set your API Key securely ---
    apiKey: "<YOUR_TYPESENSE_API_KEY>"
    # Or manage via existingSecret:
    # existingSecret: typesense-api-key

    # --- High Availability Settings ---
    replicaCount: 3 # Minimum 3 for HA

    # --- Persistence Settings ---
    persistence:
      enabled: true
      size: 10Gi
      # storageClassName: "your-storage-class" # Optional: Specify if needed

    # --- Resource Limits ---
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1"

    # Refer to the chart's default values.yaml for more options:
    # https://github.com/typesense/helm-chart/blob/main/charts/typesense/values.yaml
    ```
    Install or upgrade using this file:
    ```bash
    # Install
    helm install typesense typesense/typesense -f values.yaml

    # Upgrade an existing release
    helm upgrade typesense typesense/typesense -f values.yaml
    ```

### References
- [Typesense Installation Guide](https://typesense.org/docs/guide/install-typesense.html)
- [Typesense Helm Chart Repository](https://github.com/typesense/helm-chart)
- [Typesense Helm Chart `values.yaml`](https://github.com/typesense/helm-chart/blob/main/charts/typesense/values.yaml)
- [Typesense Kubernetes Operator (Community)](https://github.com/sai3010/Typesense-Kubernetes-Operator)