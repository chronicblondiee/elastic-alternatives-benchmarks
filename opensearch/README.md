## Install Guide for OpenSearch on Kubernetes

- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [OpenSearch Helm Charts](https://github.com/opensearch-project/helm-charts)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).
- Persistent storage configured in your cluster (required for production deployments).

### Steps to Install OpenSearch and OpenSearch Dashboards on Kubernetes using Helm

1.  **Add the OpenSearch Helm Repository**
    Add the official OpenSearch Helm chart repository:
    ```bash
    helm repo add opensearch https://opensearch-project.github.io/helm-charts/
    helm repo update
    ```

2.  **Install OpenSearch Cluster**
    Deploy an OpenSearch cluster to your Kubernetes environment.

    *   **Default Installation (Minimal, No Persistence):**
        ```bash
        # Installs a basic 3-node cluster without persistent storage
        helm install opensearch opensearch/opensearch \
          --set clusterName="opensearch-cluster" \
          -n opensearch --create-namespace
        ```
        *Note: This default setup is **not recommended for production** as it lacks persistence.*

    *   **Installation with Custom Values (Recommended):**
        Create a `values-opensearch.yaml` file to configure persistence, resources, security, etc. See step 6 for an example.
        ```bash
        helm install opensearch opensearch/opensearch -f values-opensearch.yaml -n opensearch --create-namespace
        ```

3.  **Verify OpenSearch Installation**
    Check the status of the deployed OpenSearch pods in the `opensearch` namespace:
    ```bash
    kubectl get pods -n opensearch -l app=opensearch-cluster-master
    kubectl get pods -n opensearch -l app=opensearch-cluster-client
    kubectl get pods -n opensearch -l app=opensearch-cluster-data
    ```
    Wait until all relevant pods (master, data, client nodes) are in the `Running` state. Check cluster health:
    ```bash
    # Port-forward to access the cluster API
    kubectl port-forward svc/opensearch-cluster-master 9200:9200 -n opensearch &

    # Check health (default credentials: admin/admin)
    curl -k -u admin:admin https://localhost:9200/_cluster/health?pretty

    # Kill the port-forward process afterwards
    kill %1
    ```

4.  **Install OpenSearch Dashboards (Optional)**
    Deploy OpenSearch Dashboards to visualize and interact with your OpenSearch cluster.

    *   **Default Installation:**
        ```bash
        # Assumes OpenSearch cluster service is named 'opensearch-cluster-master'
        helm install opensearch-dashboards opensearch/opensearch-dashboards \
          --set opensearchHosts="https://opensearch-cluster-master.opensearch.svc.cluster.local:9200" \
          -n opensearch # Install in the same namespace
        ```

    *   **Installation with Custom Values:**
        Create a `values-dashboards.yaml` file for custom settings. See step 6 for an example.
        ```bash
        helm install opensearch-dashboards opensearch/opensearch-dashboards -f values-dashboards.yaml -n opensearch
        ```

5.  **Verify Dashboards Installation**
    Check the status of the OpenSearch Dashboards pods:
    ```bash
    kubectl get pods -n opensearch -l app=opensearch-dashboards
    ```
    Wait until the pod is `Running`.

6.  **Access OpenSearch Dashboards**
    Use port-forwarding for quick access to the Dashboards UI (default port 5601):
    ```bash
    kubectl port-forward svc/opensearch-dashboards 5601:5601 -n opensearch
    ```
    Open your browser and navigate to `https://localhost:5601`. You might need to accept a self-signed certificate warning. Log in using the default OpenSearch credentials (`admin`/`admin` unless changed).

7.  **Custom Configuration (Example)**
    Create `values-opensearch.yaml` and `values-dashboards.yaml` for a more robust setup.

    **Example `values-opensearch.yaml`:**
    ```yaml
    # filepath: values-opensearch.yaml
    clusterName: "opensearch-prod"
    nodeGroup: "master" # Example: Configuring master nodes specifically

    master:
      replicas: 3
      persistence:
        enable: true
        size: "10Gi"
        # storageClass: "your-storage-class" # Optional: Specify if needed

    data:
      replicas: 3
      persistence:
        enable: true
        size: "50Gi"
        # storageClass: "your-storage-class"

    client:
      replicas: 2

    # Enable security plugin by default in recent charts
    # security:
    #   enable: true

    # Adjust resources as needed
    # masterResources:
    #   requests:
    #     memory: "1Gi"
    #     cpu: "500m"
    #   limits:
    #     memory: "2Gi"
    #     cpu: "1"
    # dataResources: { ... }
    # clientResources: { ... }

    # Refer to the chart's default values.yaml for all options:
    # https://github.com/opensearch-project/helm-charts/blob/main/charts/opensearch/values.yaml
    ```

    **Example `values-dashboards.yaml`:**
    ```yaml
    # filepath: values-dashboards.yaml
    # Point to the correct OpenSearch service endpoint
    opensearchHosts: "https://opensearch-prod-master.opensearch.svc.cluster.local:9200" # Match clusterName from opensearch values

    replicas: 1

    # Enable persistence for dashboards plugins/configs if needed
    # persistence:
    #   enabled: true
    #   size: 1Gi

    # resources:
    #   requests:
    #     memory: "512Mi"
    #     cpu: "200m"
    #   limits:
    #     memory: "1Gi"
    #     cpu: "500m"

    # Refer to the chart's default values.yaml for all options:
    # https://github.com/opensearch-project/helm-charts/blob/main/charts/opensearch-dashboards/values.yaml
    ```
    Install or upgrade using these files:
    ```bash
    # Install
    helm install opensearch opensearch/opensearch -f values-opensearch.yaml -n opensearch --create-namespace
    helm install opensearch-dashboards opensearch/opensearch-dashboards -f values-dashboards.yaml -n opensearch

    # Upgrade an existing release
    helm upgrade opensearch opensearch/opensearch -f values-opensearch.yaml -n opensearch
    helm upgrade opensearch-dashboards opensearch/opensearch-dashboards -f values-dashboards.yaml -n opensearch
    ```
    **Security Note:** The default `admin`/`admin` credentials should be changed immediately in a production environment. Refer to the OpenSearch security plugin documentation.

### References
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [OpenSearch Helm Charts Repository](https://github.com/opensearch-project/helm-charts)
- [OpenSearch Chart `values.yaml`](https://github.com/opensearch-project/helm-charts/blob/main/charts/opensearch/values.yaml)
- [OpenSearch Dashboards Chart `values.yaml`](https://github.com/opensearch-project/helm-charts/blob/main/charts/opensearch-dashboards/values.yaml)