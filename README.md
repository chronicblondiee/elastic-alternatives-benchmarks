# Elasticsearch Alternatives Benchmarks

This repository provides installation guides and benchmarking resources for various Elasticsearch alternatives, focusing on deployment within a Kubernetes environment, specifically on ARM architecture.

## Goals & Requirements

The primary goal is to evaluate Elasticsearch alternatives based on the following criteria:

-   **Kubernetes Deployment:** Each alternative must be deployable on a standard Kubernetes cluster. Installation guides using Helm or Operators are preferred.
-   **ARM Compatibility:** The alternative must have official or community support for running on ARM64 architecture.
-   **Core Search Capabilities:** The alternative should offer core functionalities similar to Elasticsearch, such as full-text search, indexing, and querying capabilities.

## Included Alternatives

This repository currently includes guides and resources for the following Elasticsearch alternatives:

-   [ECK (Elastic Stack)](./eck/README.md)
-   [Grafana Loki](./grafana-loki/README.md)
-   [ManticoreSearch](./manticoresearch/README.md)
-   [Meilisearch](./meilisearch/README.md)
-   [OpenObserve](./openobserve/README.md)
-   [OpenSearch](./opensearch/README.md)
-   [Quickwit](./quickwit/README.md)
-   [Solr](./solr/README.md)
-   [Sonic](./sonic/README.md)
-   [Typesense](./typesense/README.md)
-   [ZincSearch](./zincsearch/README.md)

## Repository Structure

Each Elasticsearch alternative has its own dedicated directory within this repository. Inside each directory, you will find:

-   `README.md`: A detailed step-by-step guide for installing the alternative on Kubernetes.
-   `values.yaml` (or similar): Example configuration files for Helm charts or Kubernetes manifests.
-   *(Potentially)* Benchmarking scripts or configurations specific to that alternative.

## How to Use

1.  Navigate to the directory of the Elasticsearch alternative you are interested in (e.g., `cd manticoresearch`).
2.  Follow the instructions in the `README.md` file within that directory to install the alternative on your Kubernetes cluster.
3.  (Optional) Use any provided benchmarking tools or scripts to evaluate performance.

## Contributing

Contributions are welcome! If you want to add another Elasticsearch alternative, improve an existing guide, or add benchmarking tools, please feel free to open an issue or submit a pull request. Ensure any additions meet the core requirements (Kubernetes deployable, ARM compatible).
