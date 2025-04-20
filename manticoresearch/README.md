## Install Guide
- [ManticoreSearch Installation Documentation](https://manticoresearch.com/install/)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).

### Steps to Install ManticoreSearch on Kubernetes

1.  **Add the ManticoreSearch Helm Repository**
    Add the official ManticoreSearch Helm chart repository to your Helm configuration:
    ```bash
    helm repo add manticoresearch https://manticoresearch.github.io/helm-charts
    helm repo update
    ```

2.  **Install ManticoreSearch Using Helm**
    Deploy ManticoreSearch to your Kubernetes cluster using the Helm chart.

    *   **Default Installation:**
        ```bash
        helm install manticoresearch manticoresearch/manticoresearch
        ```

    *   **Installation with Custom Values:**
        Create a `values.yaml` file to override default settings (see step 5 for an example). Then, install using your custom values:
        ```bash
        helm install manticoresearch manticoresearch/manticoresearch -f values.yaml
        ```

3.  **Verify the Installation**
    Check the status of the deployed pods to ensure ManticoreSearch is running correctly:
    ```bash
    kubectl get pods
    ```
    Look for pods related to the `manticoresearch` release. They should be in the `Running` state.

4.  **Access ManticoreSearch**
    To interact with ManticoreSearch, you need to expose the service. You can use port-forwarding for quick access to the SQL (9306) and HTTP (9308) ports:

    *   **SQL Port Forwarding:**
        ```bash
        kubectl port-forward svc/manticoresearch 9306:9306
        ```
        Connect using a MySQL client: `mysql -h127.0.0.1 -P9306 -protocol=tcp`

    *   **HTTP Port Forwarding:**
        ```bash
        kubectl port-forward svc/manticoresearch 9308:9308
        ```
        Access the HTTP API via `curl http://localhost:9308/search -d '{"index":"myindex","query":{"match":{"title":"test"}}}'` (replace `myindex` and query as needed).

    For production environments, consider using a LoadBalancer or Ingress controller.

5.  **Custom Configuration (Optional)**
    To customize your ManticoreSearch deployment (e.g., replica count, resource limits, persistence), create a `values.yaml` file. Here's an example:
    ```yaml
    # filepath: values.yaml
    # Example custom values for ManticoreSearch Helm chart
    replicaCount: 2 # Example: Increase replica count

    resources:
      requests:
        memory: "1Gi" # Example: Set memory request
        cpu: "500m"   # Example: Set CPU request
      limits:
        memory: "2Gi" # Example: Set memory limit
        cpu: "1"      # Example: Set CPU limit

    persistence:
      enabled: true
      size: 10Gi

    # Add other custom configurations as needed
    # Refer to the chart's default values.yaml for available options:
    # https://github.com/manticoresoftware/helm-charts/blob/main/charts/manticoresearch/values.yaml
    ```
    Then, use this file during installation as shown in step 2. If you've already installed ManticoreSearch, you can upgrade the release with your custom values:
    ```bash
    helm upgrade manticoresearch manticoresearch/manticoresearch -f values.yaml
    ```

### References
- [ManticoreSearch Installation Guide](https://manticoresearch.com/install/)
- [ManticoreSearch Helm Charts Repository](https://github.com/manticoresoftware/helm-charts)
- [ManticoreSearch Helm Chart `values.yaml`](https://github.com/manticoresoftware/helm-charts/blob/main/charts/manticoresearch/values.yaml)