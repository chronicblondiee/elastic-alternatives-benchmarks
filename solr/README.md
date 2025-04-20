## Install Guide
- [Solr Operator Local Tutorial](https://apache.github.io/solr-operator/docs/local_tutorial)
- [Apache Solr Getting Started Guide](https://solr.apache.org/guide/solr/latest/getting-started/introduction.html)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later).
- The Solr Operator installed in your Kubernetes cluster.

### Steps to Install Apache Solr on Kubernetes

1.  **Install the Solr Operator**
    Deploy the Solr Operator to manage Solr clusters in Kubernetes:
    ```bash
    kubectl apply -f https://apache.github.io/solr-operator/docs/solr-operator.yaml
    ```

2.  **Create a SolrCloud Instance**
    Save the following configuration to a file named `solrcloud.yaml`:
    ```yaml
    apiVersion: solr.apache.org/v1beta1
    kind: SolrCloud
    metadata:
      name: example-solrcloud
    spec:
      replicas: 3
      solrImage:
        tag: "9.3.0"
    ```
    Apply the configuration:
    ```bash
    kubectl apply -f solrcloud.yaml
    ```

3.  **Verify the Installation**
    Check if the SolrCloud pods are running:
    ```bash
    kubectl get pods
    ```

4.  **Access Solr**
    Expose the Solr service using port-forwarding:
    ```bash
    kubectl port-forward svc/example-solrcloud-solr 8983:8983
    ```
    You can now access the Solr Admin UI at `http://localhost:8983`.

### References
- [Solr Operator Documentation](https://apache.github.io/solr-operator/docs/local_tutorial)
- [Apache Solr Getting Started Guide](https://solr.apache.org/guide/solr/latest/getting-started/introduction.html)
