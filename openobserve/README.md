## Install Guide
- [OpenObserve Enterprise Edition Installation Guide](https://openobserve.ai/docs/openobserve-enterprise-edition-installation-guide/)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).

### Steps to Install OpenObserve on Kubernetes

1.  **Add the OpenObserve Helm Repository**
    Add the official OpenObserve Helm chart repository to your Helm configuration:
    ```bash
    # https://github.com/openobserve/openobserve-helm-chart/blob/main/charts/openobserve/README.md
    kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.1.yaml
    helm repo add openobserve https://charts.openobserve.ai
    helm repo update
    ```

2.  **Install OpenObserve Using Helm**
    Deploy OpenObserve to your Kubernetes cluster using the Helm chart. You can install with default settings or provide a custom `values.yaml` file.

    *   **Default Installation:**
        ```bash
        helm install openobserve openobserve/openobserve
        ```

    *   **Installation with Custom Values:**
        Create a `values.yaml` file to override default settings (see step 5 for an example). Then, install using your custom values:
        ```bash
        helm install openobserve openobserve/openobserve -f values.yaml
        ```

3.  **Verify the Installation**
    Check the status of the deployed pods to ensure OpenObserve is running correctly:
    ```bash
    kubectl get pods
    ```
    Look for pods related to the `openobserve` release. They should be in the `Running` state.

4.  **Access OpenObserve**
    To access the OpenObserve UI, you need to expose the service. You can use port-forwarding for quick access:
    ```bash
    kubectl port-forward svc/openobserve 5080:5080
    ```
    Open your web browser and navigate to `http://localhost:5080`. For production environments, consider using a LoadBalancer or Ingress controller.

5.  **Custom Configuration (Optional)**
    To customize your OpenObserve deployment (e.g., replica count, resource limits), create a `values.yaml` file. Here's an example:
    ```yaml
    # filepath: values.yaml
    # Example custom values for OpenObserve Helm chart
    replicaCount: 2 # Example: Increase replica count

    resources:
      requests:
        memory: "1Gi" # Example: Set memory request
        cpu: "500m"   # Example: Set CPU request
      limits:
        memory: "2Gi" # Example: Set memory limit
        cpu: "1"      # Example: Set CPU limit

    # Add other custom configurations as needed
    # Refer to the chart's default values.yaml for available options:
    # https://github.com/openobserve/helm-charts/blob/main/charts/openobserve/values.yaml
    ```
    Then, use this file during installation as shown in step 2. If you've already installed OpenObserve, you can upgrade the release with your custom values:
    ```bash
    helm upgrade openobserve openobserve/openobserve -f values.yaml
    ```

### References
- [OpenObserve Installation Guide](https://openobserve.ai/docs/openobserve-enterprise-edition-installation-guide/)
- [OpenObserve Helm Charts Repository](https://github.com/openobserve/helm-charts)
- [OpenObserve Helm Chart `values.yaml`](https://github.com/openobserve/helm-charts/blob/main/charts/openobserve/values.yaml)