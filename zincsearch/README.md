## Install Guide
- [ZincSearch Documentation](https://zincsearch-docs.zinc.dev/)
- [ZincSearch Helm Chart](https://github.com/zinclabs/helm-charts)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).

### Steps to Install ZincSearch on Kubernetes using Helm

1.  **Add the ZincSearch Helm Repository**
    Add the official ZincSearch Helm chart repository:
    ```bash
    helm repo add zincsearch https://zinclabs.github.io/helm-charts/
    helm repo update
    ```

2.  **Install ZincSearch Using Helm**
    Deploy ZincSearch to your Kubernetes cluster using the Helm chart.

    *   **Default Installation:**
        ```bash
        helm install zincsearch zincsearch/zincsearch
        ```
        *Note: The default installation might use ephemeral storage. For production, enable persistence (see step 5).*

    *   **Installation with Custom Values:**
        Create a `values.yaml` file to override default settings (e.g., for persistence, resources). See step 5 for an example.
        ```bash
        helm install zincsearch zincsearch/zincsearch -f values.yaml
        ```

3.  **Verify the Installation**
    Check the status of the deployed pods:
    ```bash
    kubectl get pods
    ```
    Look for pods related to the `zincsearch` release. They should be in the `Running` state.

4.  **Access ZincSearch**
    To interact with the ZincSearch API (default port 4080), expose the service. Use port-forwarding for quick access:
    ```bash
    # Replace 'zincsearch' with the actual service name if different (check `kubectl get svc`)
    kubectl port-forward svc/zincsearch 4080:4080
    ```
    You can now access the ZincSearch UI/API at `http://localhost:4080`. The default credentials are typically `admin` / `Complexpass#123`.
    ```bash
    # Example: Check health
    curl http://localhost:4080/healthz

    # Example: List indices (using default credentials)
    curl -u admin:Complexpass#123 http://localhost:4080/api/index
    ```
    For production, use a LoadBalancer or Ingress controller and configure authentication properly.

5.  **Custom Configuration (Optional)**
    Create a `values.yaml` file to customize your deployment. Example for enabling persistence and setting resources:
    ```yaml
    # filepath: values.yaml
    # Example custom values for ZincSearch Helm chart

    # --- Authentication ---
    # Consider changing default credentials or using a more secure method
    # auth:
    #   username: "your_admin_user"
    #   password: "your_secure_password" # Or manage via secrets

    # --- Persistence Settings ---
    persistence:
      enabled: true
      size: 10Gi
      # storageClassName: "your-storage-class" # Optional: Specify if needed

    # --- Resource Limits ---
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "500m"

    # Refer to the chart's default values.yaml for more options:
    # https://github.com/zinclabs/helm-charts/blob/main/charts/zincsearch/values.yaml
    ```
    Install or upgrade using this file:
    ```bash
    # Install
    helm install zincsearch zincsearch/zincsearch -f values.yaml

    # Upgrade an existing release
    helm upgrade zincsearch zincsearch/zincsearch -f values.yaml
    ```

### References
- [ZincSearch Documentation](https://zincsearch-docs.zinc.dev/)
- [ZincSearch Helm Chart Repository](https://github.com/zinclabs/helm-charts)
- [ZincSearch Helm Chart `values.yaml`](https://github.com/zinclabs/helm-charts/blob/main/charts/zincsearch/values.yaml)