# Installing Ingress-NGINX

This document provides instructions on how to install the Ingress-NGINX controller on your Kubernetes cluster, particularly for bare-metal setups.

## Prerequisites

*   A running Kubernetes cluster (e.g., k3s, Kind, Minikube, or a cloud provider's K8s service).
*   `kubectl` configured to communicate with your cluster.
*   Helm package manager installed.

## Installation Steps

The following command will install Ingress-NGINX using Helm. It will create a dedicated namespace `ingress-nginx` for the controller.

<!-- filepath: /home/brown/elastic-alternatives-benchmarks/opensearch/ingress-nginx/README.md -->
### https://kubernetes.github.io/ingress-nginx/deploy/#bare-metal-clusters

```bash
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

## Verify Installation

After the Helm chart is installed, you can verify that the Ingress-NGINX controller pods are running:

```bash
kubectl get pods --namespace ingress-nginx
```

You should see pods in a `Running` state. It might take a few moments for all components to be ready.

You can also check the service created for the ingress controller:

```bash
kubectl get svc --namespace ingress-nginx
```
This will typically show a LoadBalancer service (if your environment supports it) or a NodePort service for bare-metal clusters.

## Notes for Bare-Metal Clusters

The command provided is suitable for bare-metal clusters as indicated by the original link. For cloud environments, there might be specific annotations or configurations needed for the LoadBalancer service to integrate correctly with the cloud provider's load balancing services. Always refer to the [official Ingress-NGINX deployment documentation](https://kubernetes.github.io/ingress-nginx/deploy/) for the most up-to-date and environment-specific instructions.