## Install Guide for OpenSearch on Kubernetes using the OpenSearch Kubernetes Operator

- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [OpenSearch Kubernetes Operator Documentation](https://opensearch.org/docs/latest/tools/k8s-operator/)
- [OpenSearch Operator GitHub Repository](https://github.com/opensearch-project/opensearch-k8s-operator)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later) for installing the operator.
- Persistent storage configured in your cluster (recommended for production deployments).

### Steps to Install OpenSearch and OpenSearch Dashboards on Kubernetes using the OpenSearch Operator

1.  **Add the OpenSearch Operator Helm Repository**
    Add the official OpenSearch Operator Helm chart repository:
    ```bash
    helm repo add opensearch-operator https://opensearch-project.github.io/opensearch-k8s-operator/
    helm repo update
    ```
    Verify the repository is added:
    ```bash
    helm repo list | grep opensearch-operator
    ```

2.  **Install the OpenSearch Operator**
    Deploy the OpenSearch Operator to your Kubernetes environment. It's recommended to install it into its own namespace (e.g., `opensearch-operator-system`).
    ```bash
    helm install opensearch-operator opensearch-operator/opensearch-operator --namespace opensearch-operator-system --create-namespace
    ```

3.  **Verify Operator Installation**
    Check the status of the deployed OpenSearch Operator pods:
    ```bash
    kubectl get pods -n opensearch-operator-system
    ```
    Wait until the operator pod (e.g., `opensearch-operator-controller-manager-...`) is in the `Running` state.

4.  **Define and Deploy an OpenSearch Cluster**
    Create a YAML manifest file (e.g., `opensearch-cluster.yaml`) to define your OpenSearch cluster. The operator will watch for this Custom Resource (CR) and provision the cluster.

    **Example `opensearch-cluster.yaml` (Basic):**
    ```yaml
    # filepath: opensearch-cluster.yaml
    apiVersion: opensearch.opster.io/v1
    kind: OpenSearchCluster
    metadata:
      name: my-opensearch-cluster # Name of your OpenSearch cluster
      namespace: opensearch # Namespace where the cluster will be deployed (create if it doesn't exist)
    spec:
      general:
        version: "2.x" # Specify your desired OpenSearch version
        serviceName: my-opensearch-cluster # Base name for services
      nodePools:
        - component: master
          replicas: 3
          diskSize: "10Gi"
          # resources:
          #   requests:
          #     memory: "1Gi"
          #     cpu: "500m"
          #   limits:
          #     memory: "2Gi"
          #     cpu: "1"
        - component: data
          replicas: 3
          diskSize: "20Gi"
          # resources: { ... }
        - component: client
          replicas: 2
          # resources: { ... }
      dashboards:
        enable: true
        replicas: 1
        # resources: { ... }
    ```
    *Create the namespace for the cluster if it doesn\'t exist:*
    ```bash
    kubectl create namespace opensearch # Or the namespace you specified in the CR
    ```
    *Apply the manifest to deploy the cluster:*
    ```bash
    kubectl apply -f opensearch-cluster.yaml -n opensearch # Use the namespace specified in your CR
    ```

5.  **Verify OpenSearch Cluster and Dashboards Installation**
    Check the status of the OpenSearch cluster pods and services created by the operator in the specified namespace:
    ```bash
    kubectl get pods -n opensearch -l opensearch.cluster.opster.io/cluster-name=my-opensearch-cluster
    kubectl get svc -n opensearch -l opensearch.cluster.opster.io/cluster-name=my-opensearch-cluster
    ```
    Wait until all relevant pods (master, data, client, dashboards) are in the `Running` state.
    The operator will also create services. Typically, a service for OpenSearch might be named `my-opensearch-cluster-client` or similar, and for Dashboards `my-opensearch-cluster-dashboards-svc`.

    Check cluster health (credentials might be stored in a secret created by the operator, often `my-opensearch-cluster-user-admin`):
    ```bash
    # Find the admin secret
    kubectl get secret -n opensearch my-opensearch-cluster-user-admin -o jsonpath='{.data.username}' | base64 -d; echo
    kubectl get secret -n opensearch my-opensearch-cluster-user-admin -o jsonpath='{.data.password}' | base64 -d; echo

    # Port-forward to access the cluster API (service name might vary)
    kubectl port-forward svc/my-opensearch-cluster-client 9200:9200 -n opensearch &

    # Check health (use retrieved credentials)
    # curl -k -u <admin-username>:<admin-password> https://localhost:9200/_cluster/health?pretty
    # Example with default if security is not yet fully configured or known:
    # curl -k https://localhost:9200/_cluster/health?pretty

    # Kill the port-forward process afterwards
    kill %1
    ```

6.  **Access OpenSearch Dashboards**
    Use port-forwarding for quick access to the Dashboards UI. The service name for Dashboards is typically derived from your cluster name (e.g., `my-opensearch-cluster-dashboards-svc`).
    ```bash
    kubectl port-forward svc/my-opensearch-cluster-dashboards-svc 5601:5601 -n opensearch
    ```
    Open your browser and navigate to `http://localhost:5601` (or `https://` if TLS is enabled by default by the operator). Log in using the credentials (often `admin`/`admin` by default, or retrieved from the secret as shown in step 5).

7.  **Custom Configuration**
    To customize your OpenSearch cluster (persistence, resources, security, plugins, etc.), modify the `opensearch-cluster.yaml` manifest file and re-apply it.
    Refer to the [OpenSearch Operator Configuration Documentation](https://opensearch.org/docs/latest/tools/k8s-operator/reference/) for all available options in the `OpenSearchCluster` Custom Resource Definition.

    **Example `opensearch-cluster.yaml` with more options:**
    ```yaml
    # filepath: opensearch-cluster.yaml
    apiVersion: opensearch.opster.io/v1
    kind: OpenSearchCluster
    metadata:
      name: opensearch-prod
      namespace: opensearch-prod-ns
    spec:
      general:
        version: "2.11.0" # Be specific with version
        serviceName: opensearch-prod
        # httpPort: 9200 # Default
        setVMMaxMapCount: true # Recommended for production
      security:
        enable: true # Enable security plugin
        # tls:
        #   transport:
        #     generate: true # Operator generates certs
        #   http:
        #     generate: true # Operator generates certs
      nodePools:
        - component: master
          replicas: 3
          diskSize: "30Gi"
          # storageClass: "your-ssd-storage-class" # Specify storage class
          resources:
            requests:
              memory: "4Gi"
              cpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2"
        - component: data
          replicas: 3
          diskSize: "100Gi"
          # storageClass: "your-ssd-storage-class"
          roles: # Explicitly define roles for data nodes
            - data
            - ingest
          resources:
            requests:
              memory: "8Gi"
              cpu: "2"
            limits:
              memory: "8Gi"
              cpu: "4"
        - component: client # Dedicated coordinating nodes
          replicas: 2
          diskSize: "5Gi" # Minimal storage for client nodes
          roles:
            - client # Only client role
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1"
      dashboards:
        enable: true
        replicas: 1
        # version: "2.11.0" # Match OpenSearch version
        # tls:
        #   enable: true # Enable TLS for Dashboards
        #   generate: true
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
    ```
    Apply changes:
    ```bash
    kubectl apply -f opensearch-cluster.yaml -n opensearch-prod-ns # Use the correct namespace
    ```
    **Security Note:** The operator typically creates default credentials. It is crucial to understand how the operator manages security, how to retrieve or set initial admin passwords, and how to configure identity providers or other security mechanisms as per the operator's documentation for production environments.

### Uninstalling

1.  **Delete the OpenSearch Cluster CR**
    ```bash
    kubectl delete -f opensearch-cluster.yaml -n opensearch # Or your cluster's namespace
    # Alternatively:
    # kubectl delete opensearchcluster my-opensearch-cluster -n opensearch
    ```
    The operator will de-provision all resources associated with the cluster (Pods, Services, PVCs if reclaim policy allows).

2.  **Uninstall the OpenSearch Operator**
    ```bash
    helm uninstall opensearch-operator -n opensearch-operator-system
    ```

3.  **Delete Namespaces (Optional)**
    ```bash
    kubectl delete namespace opensearch
    kubectl delete namespace opensearch-operator-system
    ```
    Ensure all persistent volume claims (PVCs) are also deleted if you don't need the data anymore.

### References
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [OpenSearch Kubernetes Operator Documentation](https://opensearch.org/docs/latest/tools/k8s-operator/)
- [OpenSearch Operator GitHub Repository](https://github.com/opensearch-project/opensearch-k8s-operator)
- [Operator Hub - OpenSearch Operator](https://operatorhub.io/operator/opensearch-operator)