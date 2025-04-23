# Elasticsearch Alternatives Benchmarks

This repository provides installation guides and benchmarking resources for various Elasticsearch alternatives, focusing on deployment within a Kubernetes environment, specifically on ARM architecture.

## Goals & Requirements

The primary goal is to evaluate Elasticsearch alternatives based on the following criteria:

-   **Kubernetes Deployment:** Each alternative must be deployable on a standard Kubernetes cluster. Installation guides using Helm or Operators are preferred.
-   **ARM Compatibility:** The alternative must have official or community support for running on ARM64 architecture.
-   **Core Search Capabilities:** The alternative should offer core functionalities similar to Elasticsearch, such as full-text search, indexing, and querying capabilities.
-   **Benchmarking:** Provide tools and scripts to measure indexing and search performance.

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

-   **Root Directory:** Contains this main README file.
-   **Alternative Directories (e.g., `./opensearch/`, `./zincsearch/`):** Each directory dedicated to an Elasticsearch alternative typically includes:
    -   `README.md`: A detailed step-by-step guide for installing the alternative on Kubernetes.
    -   `values.yaml` (or similar): Example configuration files for Helm charts or Kubernetes manifests.
-   **`./benchmarks/`:** Contains tools and scripts for performance benchmarking.
    -   `elasticsearch-benchmark-tool/`: A specific tool for benchmarking Elasticsearch instances. Includes Python scripts for ingestion/search tests and a script to generate NDJSON test data. See [`./benchmarks/elasticsearch-benchmark-tool/README.md`](./benchmarks/elasticsearch-benchmark-tool/README.md) for details.
    -   `utils/`: May contain shared utilities or other benchmarking scripts (like the general `benchmark.py` for multiple database types).

## How to Use

1.  **Installation:**
    *   Navigate to the directory of the Elasticsearch alternative you are interested in (e.g., `cd opensearch`).
    *   Follow the instructions in the `README.md` file within that directory to install the alternative on your Kubernetes cluster.
2.  **Benchmarking:**
    *   Navigate to the relevant benchmark tool directory (e.g., `cd benchmarks/elasticsearch-benchmark-tool`).
    *   Follow the instructions in the `README.md` within that benchmark directory to set up and run the performance tests against your deployed instance.
    *   You may need to generate test data first using provided scripts (e.g., `scripts/generate_log_data.sh`).

## Contributing

Contributions are welcome! If you want to add another Elasticsearch alternative, improve an existing guide, enhance the benchmarking tools, or add results, please feel free to open an issue or submit a pull request. Ensure any additions meet the core requirements (Kubernetes deployable, ARM compatible).

## Note

I have not fully validated if all of the software listed work well on ARM I will update the repo with status as implemenation of each benchmark progresses.
