## Install Guide for Elastic Stack on Kubernetes using ECK (Elastic Cloud on Kubernetes)

- [ECK Quickstart Guide](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-quickstart.html)
- [ECK Documentation](https://www.elastic.co/guide/en/cloud-on-k8s/current/index.html)

### Prerequisites
- A Kubernetes cluster (v1.20 or later recommended).
- `kubectl` installed and configured to interact with your cluster.
- Helm installed (v3 or later) - Optional, but used in this guide for the operator installation.

### Steps to Install Elastic Stack (Elasticsearch, Kibana, Beats, Logstash) using ECK

1.  **Install the ECK Operator**
    You can install the operator using `kubectl apply` or Helm. Helm is often simpler for managing versions.

    *   **Using Helm:**
        ```bash
        # Add the Elastic Helm repository
        helm repo add elastic https://helm.elastic.co
        helm repo update

        # Install the ECK operator CRDs and the operator itself
        helm install elastic-operator elastic/eck-operator -n elastic-system --create-namespace
        ```

    *   **Using kubectl:**
        ```bash
        # Install the CRDs
        kubectl create -f https://download.elastic.co/downloads/eck/2.13.0/crds.yaml

        # Install the operator
        kubectl apply -f https://download.elastic.co/downloads/eck/2.13.0/operator.yaml
        ```
        *(Replace `2.13.0` with the desired ECK version if needed)*

2.  **Verify Operator Installation**
    Check if the ECK operator pod is running in the `elastic-system` namespace:
    ```bash
    kubectl get pods -n elastic-system
    ```
    Wait until the pod shows `Running` status.

3.  **Deploy an Elasticsearch Cluster**
    Create a file named `elasticsearch.yaml` with the following content:
    ```yaml
    # filepath: elasticsearch.yaml
    apiVersion: elasticsearch.k8s.elastic.co/v1
    kind: Elasticsearch
    metadata:
      name: quickstart # Name of your Elasticsearch cluster
    spec:
      version: 8.13.2 # Specify the desired Elasticsearch version
      nodeSets:
      - name: default
        count: 1 # Start with a single node for simplicity
        config:
          node.store.allow_mmap: false # Recommended setting for some environments
        # Add volumeClaimTemplates for persistent storage in production
        # volumeClaimTemplates:
        # - metadata:
        #     name: elasticsearch-data
        #   spec:
        #     accessModes:
        #     - ReadWriteOnce
        #     resources:
        #       requests:
        #         storage: 10Gi
        #     storageClassName: standard # Adjust storage class if needed
    ```
    Apply the configuration:
    ```bash
    kubectl apply -f elasticsearch.yaml -n default # Deploy in the 'default' namespace or choose another
    ```

4.  **Deploy a Kibana Instance**
    Create a file named `kibana.yaml` linking to the Elasticsearch cluster:
    ```yaml
    # filepath: kibana.yaml
    apiVersion: kibana.k8s.elastic.co/v1
    kind: Kibana
    metadata:
      name: quickstart # Name of your Kibana instance
    spec:
      version: 8.13.2 # Match the Elasticsearch version
      count: 1
      elasticsearchRef:
        name: quickstart # Must match the name of your Elasticsearch cluster
    ```
    Apply the configuration:
    ```bash
    kubectl apply -f kibana.yaml -n default # Deploy in the same namespace as Elasticsearch
    ```

5.  **Deploy Filebeat (Optional)**
    Filebeat is used to ship logs. Create `filebeat.yaml`:
    ```yaml
    # filepath: filebeat.yaml
    apiVersion: beat.k8s.elastic.co/v1beta1
    kind: Beat
    metadata:
      name: quickstart-filebeat
    spec:
      type: filebeat
      version: 8.13.2 # Match the stack version
      elasticsearchRef:
        name: quickstart # Points to your Elasticsearch cluster
      kibanaRef:
        name: quickstart # Points to your Kibana instance (for dashboards)
      config:
        filebeat.inputs:
        - type: container
          paths:
            - /var/log/containers/*.log
        processors:
        - add_kubernetes_metadata: ~
      # Deploy as a DaemonSet to run on all eligible nodes
      daemonSet:
        podTemplate:
          spec:
            serviceAccountName: quickstart-filebeat # Needs RBAC, see below
            automountServiceAccountToken: true
            terminationGracePeriodSeconds: 30
            dnsPolicy: ClusterFirstWithHostNet
            hostNetwork: true # Allows access to node logs
            securityContext:
              runAsUser: 0
            containers:
            - name: filebeat
              volumeMounts:
              - name: varlogcontainers
                mountPath: /var/log/containers
              - name: varlogpods
                mountPath: /var/log/pods
              - name: varlibdockercontainers
                mountPath: /var/lib/docker/containers
            volumes:
            - name: varlogcontainers
              hostPath:
                path: /var/log/containers
            - name: varlogpods
              hostPath:
                path: /var/log/pods
            - name: varlibdockercontainers
              hostPath:
                path: /var/lib/docker/containers
    ---
    # RBAC permissions needed for Filebeat DaemonSet
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: quickstart-filebeat
      namespace: default # Same namespace as Filebeat
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: quickstart-filebeat
    rules:
    - apiGroups: [""] # "" indicates the core API group
      resources:
      - namespaces
      - pods
      - nodes
      verbs:
      - get
      - watch
      - list
    - apiGroups: ["apps"]
      resources:
      - replicasets
      verbs: ["get", "list", "watch"]
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: quickstart-filebeat
    subjects:
    - kind: ServiceAccount
      name: quickstart-filebeat
      namespace: default # Same namespace as Filebeat
    roleRef:
      kind: ClusterRole
      name: quickstart-filebeat
      apiGroup: rbac.authorization.k8s.io
    ```
    Apply the configuration:
    ```bash
    kubectl apply -f filebeat.yaml -n default
    ```

6.  **Deploy Logstash (Optional)**
    Logstash is used for data processing pipelines. Create `logstash.yaml`:
    ```yaml
    # filepath: logstash.yaml
    apiVersion: logstash.k8s.elastic.co/v1alpha1
    kind: Logstash
    metadata:
      name: quickstart-logstash
    spec:
      version: 8.13.2 # Match the stack version
      count: 1 # Number of Logstash instances
      elasticsearchRefs: # Note: plural 'Refs'
      - name: quickstart # Points to your Elasticsearch cluster
        clusterName: quickstart # Optional: Specify cluster name if needed
      # Define Logstash pipelines here
      pipelines:
      - pipeline.id: main
        config.string: |
          input {
            beats {
              port => 5044
            }
          }
          # Add filters here if needed
          # filter {
          #   grok { ... }
          # }
          output {
            elasticsearch {
              hosts => ["https://quickstart-es-http.default.svc:9200"] # Internal ES service
              # Manage credentials securely, e.g., via secrets
              # user => elastic
              # password => "${ELASTIC_PASSWORD}" # Example using env var secret
              ssl_verification_mode => "none" # Use 'full' or 'certificate' in production with proper certs
              index => "logstash-%{+YYYY.MM.dd}"
            }
          }
      # Expose the Beats input port
      services:
       - name: beats
         service:
           spec:
             type: ClusterIP
             ports:
             - port: 5044
               name: "beats-port"
               protocol: TCP
               targetPort: 5044
      # Add volumeClaimTemplates for persistent queue if needed
      # volumeClaimTemplates:
      # - metadata:
      #     name: logstash-data
      #   spec:
      #     accessModes:
      #     - ReadWriteOnce
      #     resources:
      #       requests:
      #         storage: 5Gi
      #     storageClassName: standard
    ```
    Apply the configuration:
    ```bash
    kubectl apply -f logstash.yaml -n default
    ```
    *Note: You would typically configure Filebeat to output to this Logstash instance (`quickstart-logstash-beats.default.svc:5044`) instead of directly to Elasticsearch.*

7.  **Verify Stack Deployment**
    Check the status of all deployed components:
    ```bash
    kubectl get pods -n default
    kubectl get elasticsearch -n default
    kubectl get kibana -n default
    kubectl get beat -n default # If Filebeat deployed
    kubectl get logstash -n default # If Logstash deployed
    ```
    Wait until the pods are `Running` and the cluster health is `green` or `yellow`. This might take a few minutes.

8.  **Access Kibana**
    The ECK operator creates services for Elasticsearch and Kibana. Use port-forwarding for quick access:
    ```bash
    kubectl port-forward service/quickstart-kb-http 5601 -n default
    ```
    Open your browser and navigate to `https://localhost:5601`. You might need to accept a self-signed certificate warning.

9.  **Retrieve Credentials**
    The default `elastic` user password is stored in a Kubernetes secret. Retrieve it using:
    ```bash
    kubectl get secret quickstart-es-elastic-user -n default -o=jsonpath='{.data.elastic}' | base64 --decode; echo
    ```
    Use `elastic` as the username and the retrieved password to log in to Kibana.

10. **Custom Configuration (Optional)**
    Modify the `.yaml` files to customize resources, enable persistence, configure security settings, add more nodes, define complex pipelines, etc. Refer to the official ECK documentation for all available options. Apply changes using `kubectl apply -f <filename>.yaml`.

### References
- [ECK Quickstart Guide](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-quickstart.html)
- [ECK Elasticsearch CRD Reference](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-elasticsearch-specification.html)
- [ECK Kibana CRD Reference](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-kibana-specification.html)
- [ECK Beat CRD Reference](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-beat-specification.html)
- [ECK Logstash CRD Reference](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-logstash-specification.html)
- [Elastic Helm Charts Repository](https://github.com/elastic/helm-charts)