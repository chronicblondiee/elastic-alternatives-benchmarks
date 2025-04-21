## Install Guide for Meilisearch on Kubernetes

- [Meilisearch Documentation](https://www.meilisearch.com/docs)
- [Meilisearch Helm Chart (Community)](https://github.com/meilisearch/meilisearch-kubernetes) - Note: This chart might be less frequently updated than official ones for other projects. Check for alternatives if needed.

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).
- Persistent storage configured in your cluster (recommended for production).

### Steps to Install Meilisearch on Kubernetes using Helm

1.  **Add the Meilisearch Helm Repository**
    Add the community-maintained Meilisearch Helm chart repository:
    ```bash
    helm repo add meilisearch https://meilisearch.github.io/meilisearch-kubernetes
    helm repo update
    ```

2.  **Install Meilisearch**
    Deploy Meilisearch to your Kubernetes environment.

    *   **Default Installation (No Persistence, Auto-Generated API Key):**
        ```bash
        # Installs a single Meilisearch instance without persistent storage.
        # An API key will be auto-generated and stored in a secret.
        helm install my-meilisearch meilisearch/meilisearch \
          -n meilisearch --create-namespace
        ```
        *Note: This default setup is **not recommended for production** due to lack of persistence and potentially insecure default key management.*

    *   **Installation with Custom Values (Recommended):**
        Create a `values.yaml` file to configure persistence, set a master key, adjust resources, etc. See step 6 for an example.
        ```bash
        helm install my-meilisearch meilisearch/meilisearch -f values.yaml -n meilisearch --create-namespace
        ```

3.  **Verify Meilisearch Installation**
    Check the status of the deployed Meilisearch pod(s) in the `meilisearch` namespace:
    ```bash
    kubectl get pods -n meilisearch -l app.kubernetes.io/instance=my-meilisearch
    ```
    Wait until the pod is in the `Running` state.

4.  **Retrieve the Master Key**
    Meilisearch requires a Master Key for administrative operations.

    *   **If you set `apiKey` in `values.yaml`:** Use the key you specified.
    *   **If using the default installation:** The key is auto-generated and stored in a secret. Retrieve it:
        ```bash
        kubectl get secret my-meilisearch -n meilisearch -o jsonpath='{.data.MEILI_MASTER_KEY}' | base64 -d ; echo
        ```
        *(Replace `my-meilisearch` if you used a different release name)*. **Store this key securely.**

5.  **Access Meilisearch**
    Use port-forwarding for quick access to the Meilisearch API (default port 7700):
    ```bash
    kubectl port-forward svc/my-meilisearch 7700:7700 -n meilisearch
    ```
    You can now interact with the API at `http://localhost:7700`. Use the Master Key in the `Authorization` header for protected endpoints.
    ```bash
    # Check health (no key needed)
    curl http://localhost:7700/health

    # Get stats (requires Master Key)
    curl -H "Authorization: Bearer YOUR_MASTER_KEY" http://localhost:7700/stats
    ```
    *(Replace `YOUR_MASTER_KEY` with the key retrieved in the previous step)*. For production, use a LoadBalancer or Ingress controller.

6.  **Custom Configuration (Example)**
    Create `values.yaml` for a more robust setup.

    **Example `values.yaml`:**
    ```yaml
    # filepath: values.yaml

    # --- IMPORTANT: Set a strong Master Key ---
    # Generate a secure key (e.g., using openssl rand -base64 32)
    apiKey: "YOUR_SECURE_MASTER_KEY" # Replace this!

    # --- Persistence Settings ---
    persistence:
      enabled: true
      size: "5Gi" # Adjust size as needed
      # storageClassName: "your-storage-class" # Optional: Specify if needed

    # --- Resource Limits ---
    # resources:
    #   requests:
    #     memory: "256Mi"
    #     cpu: "100m"
    #   limits:
    #     memory: "1Gi"
    #     cpu: "500m"

    # --- Environment ---
    # Set environment to 'production' for optimized settings
    env: "production" # Options: development, production

    # Refer to the chart's default values.yaml for all options:
    # https://github.com/meilisearch/meilisearch-kubernetes/blob/main/charts/meilisearch/values.yaml
    ```
    Install or upgrade using this file:
    ```bash
    # Install
    helm install my-meilisearch meilisearch/meilisearch -f values.yaml -n meilisearch --create-namespace

    # Upgrade an existing release
    helm upgrade my-meilisearch meilisearch/meilisearch -f values.yaml -n meilisearch
    ```
    **Security Note:** Always set a strong, unique `apiKey` (Master Key) in production and manage it securely. Avoid relying on the auto-generated key for long-term use.

### References
- [Meilisearch Documentation](https://www.meilisearch.com/docs)
- [Meilisearch Kubernetes Helm Chart Repository](https://github.com/meilisearch/meilisearch-kubernetes)
- [Meilisearch Helm Chart `values.yaml`](https://github.com/meilisearch/meilisearch-kubernetes/blob/main/charts/meilisearch/values.yaml)