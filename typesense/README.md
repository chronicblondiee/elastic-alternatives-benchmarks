## Install Guide
- [Typesense Installation Documentation](https://typesense.org/docs/guide/install-typesense.html)
- [Typesense Kubernetes Operator (Community)](https://github.com/sai3010/Typesense-Kubernetes-Operator)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- **Typesense Kubernetes Operator installed** in your cluster.

### Steps to Install Typesense on Kubernetes using the Operator

1.  **Install the Typesense Kubernetes Operator**
    Follow the instructions from the [Typesense Kubernetes Operator repository](https://github.com/sai3010/Typesense-Kubernetes-Operator) to install the operator itself. This typically involves applying YAML manifests:
    ```bash
    # Example command - refer to the operator's documentation for the correct manifests https://sai3010.github.io/Typesense-Kubernetes-Operator/deployment/
    kubectl apply -f https://raw.githubusercontent.com/sai3010/Typesense-Kubernetes-Operator/refs/heads/main/operator-config.yaml
    ```
    Verify the operator pod is running:
    ```bash
    kubectl get pods -n typesense-operator # Or the namespace where the operator was installed
    ```

2.  **Create a Typesense API Key Secret**
    Securely generate a strong API key for Typesense. Create a Kubernetes secret to store it:
    ```bash
    # Replace YOUR_SECURE_API_KEY with your generated key
    kubectl create secret generic typesense-api-key --from-literal=key=YOUR_SECURE_API_KEY -n default # Or your target namespace
    ```

3.  **Define and Deploy a Typesense Cluster**
    Create a YAML manifest file (e.g., `typesense-cluster.yaml`) using the `Typesense` Custom Resource Definition (CRD) provided by the operator.

    **Example `typesense-cluster.yaml` (Single Node with Persistence):**
    ```yaml
    # filepath: typesense-cluster.yaml
    apiVersion: typesense.com/v1alpha1
    kind: Typesense
    metadata:
      name: my-typesense-cluster # Name of your Typesense instance
      namespace: default # Namespace where you want to deploy Typesense
    spec:
      # Reference the secret containing the API key
      apiKeySecretName: typesense-api-key

      # Number of nodes (1 for single node, >=3 for HA)
      nodes: 1

      # Image settings (optional, defaults usually work)
      # image: typesense/typesense:0.25.2

      # Persistence settings
      persistence:
        enabled: true
        accessMode: ReadWriteOnce
        storageClassName: "standard" # Adjust if needed
        size: 10Gi # Adjust size as needed

      # Resource settings (optional)
      # resources:
      #   requests:
      #     memory: "1Gi"
      #     cpu: "500m"
      #   limits:
      #     memory: "2Gi"
      #     cpu: "1"

      # Refer to the Operator's documentation for all available spec options
    ```
    Apply the manifest to create the Typesense cluster:
    ```bash
    kubectl apply -f typesense-cluster.yaml
    ```

4.  **Verify the Installation**
    Check the status of the deployed Typesense pods managed by the operator:
    ```bash
    kubectl get pods -n default -l app.kubernetes.io/instance=my-typesense-cluster # Adjust namespace and name if needed
    ```
    Look for the pod(s) related to `my-typesense-cluster`. They should be in the `Running` state. Also check the status of the CRD:
    ```bash
    kubectl get typesense my-typesense-cluster -n default -o yaml
    ```

5.  **Access Typesense**
    The operator typically creates a Service for your Typesense cluster. Find the service name:
    ```bash
    kubectl get svc -n default -l app.kubernetes.io/instance=my-typesense-cluster
    ```
    Assuming the service is named `my-typesense-cluster`, use port-forwarding for quick access (default port 8108):
    ```bash
    kubectl port-forward svc/my-typesense-cluster 8108:8108 -n default
    ```
    You can now access the Typesense API at `http://localhost:8108`. Use your API key (from the secret) for authentication.
    ```bash
    # Replace YOUR_SECURE_API_KEY with the key from the secret
    curl -H "X-TYPESENSE-API-KEY: YOUR_SECURE_API_KEY" http://localhost:8108/health
    ```
    For production, use a LoadBalancer or Ingress controller pointing to the service.

6.  **Custom Configuration (Optional)**
    Modify the `typesense-cluster.yaml` manifest to customize your deployment. You can adjust `spec.nodes` for High Availability (requires >= 3), change persistence settings, define resources, specify node selectors, etc. Refer to the [Typesense Kubernetes Operator documentation](https://github.com/sai3010/Typesense-Kubernetes-Operator) for all available fields within the `spec`. Apply changes using `kubectl apply -f typesense-cluster.yaml`.

### References
- [Typesense Installation Guide](https://typesense.org/docs/guide/install-typesense.html)
- [Typesense Kubernetes Operator (Community)](https://github.com/sai3010/Typesense-Kubernetes-Operator)
- [Typesense Operator CRD Definition (Check Operator Repo)](https://github.com/sai3010/Typesense-Kubernetes-Operator/blob/main/deploy/crds/typesense.com_typesenses_crd.yaml)