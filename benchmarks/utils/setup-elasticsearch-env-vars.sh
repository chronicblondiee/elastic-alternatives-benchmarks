#!/bin/bash

# --- Configuration ---
DEFAULT_CLUSTER_NAME="elasticsearch" # Default Elasticsearch cluster name used in manifests/es-kb.yml
DEFAULT_NAMESPACE="elastic"          # Default namespace where ECK resources are deployed
LOADBALANCER_TIMEOUT_SECONDS=180     # How long to wait for LoadBalancer IP

# --- Functions ---
usage() {
  echo "Usage: source $0 [-n <namespace>] [-c <cluster_name>] [-t <timeout>]"
  echo "  Extracts the 'elastic' user credentials, LoadBalancer IP, and HTTP port"
  echo "  from the ECK-generated resources and exports them as environment variables:"
  echo "    ELASTIC_USER, ELASTIC_PASSWORD, ES_HOST, ES_PORT"
  echo "  Must be sourced (e.g., 'source $0') to affect the current shell session."
  echo ""
  echo "  Options:"
  echo "    -n <namespace>:    Kubernetes namespace where the Elasticsearch cluster is deployed (default: $DEFAULT_NAMESPACE)"
  echo "    -c <cluster_name>: Name of the Elasticsearch cluster resource (default: $DEFAULT_CLUSTER_NAME)"
  echo "    -t <timeout>:      Timeout in seconds to wait for LoadBalancer IP (default: $LOADBALANCER_TIMEOUT_SECONDS)"
  echo "    -h:                Display this help message"
  # Use return instead of exit in case the script is sourced and -h is used
  return 1
}

# --- Argument Parsing ---
NAMESPACE="$DEFAULT_NAMESPACE"
CLUSTER_NAME="$DEFAULT_CLUSTER_NAME"
TIMEOUT="$LOADBALANCER_TIMEOUT_SECONDS"

# Use getopts for parsing arguments
# Note: getopts runs in the current shell when sourced, so OPTIND needs reset if run multiple times
OPTIND=1
while getopts "n:c:t:h" opt; do
  case $opt in
    n) NAMESPACE="$OPTARG" ;;
    c) CLUSTER_NAME="$OPTARG" ;;
    t) TIMEOUT="$OPTARG" ;;
    h) usage; return 0 ;; # Use return 0 for successful help display when sourced
    \?) echo "Invalid option: -$OPTARG" >&2; usage; return 1 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage; return 1 ;;
  esac
done
shift $((OPTIND-1))

# --- Validation ---
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl command not found. Please ensure kubectl is installed and in your PATH." >&2
    return 1
fi
if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
    echo "Error: Timeout value must be an integer." >&2
    usage
    return 1
fi


# --- Main Logic ---

# 1. Extract User Credentials
SECRET_NAME="${CLUSTER_NAME}-es-elastic-user"
echo "Attempting to extract credentials for user 'elastic' from secret '$SECRET_NAME' in namespace '$NAMESPACE'..." >&2

encoded_password=$(kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" -o jsonpath='{.data.elastic}' 2>/dev/null)

if [[ $? -ne 0 || -z "$encoded_password" ]]; then
  echo "Error: Failed to retrieve secret '$SECRET_NAME' in namespace '$NAMESPACE'." >&2
  echo "Please check if the cluster name and namespace are correct and the secret exists." >&2
  return 1
fi

decoded_password=$(echo "$encoded_password" | base64 --decode 2>/dev/null)

if [[ $? -ne 0 || -z "$decoded_password" ]]; then
    echo "Error: Failed to decode the password. The secret data might be corrupted." >&2
    return 1
fi

export ELASTIC_USER="elastic"
export ELASTIC_PASSWORD="$decoded_password"
echo "Successfully exported ELASTIC_USER and ELASTIC_PASSWORD." >&2


# 2. Extract LoadBalancer IP and Port
SERVICE_NAME="${CLUSTER_NAME}-es-http"
echo "Attempting to extract LoadBalancer IP and Port from service '$SERVICE_NAME' in namespace '$NAMESPACE'..." >&2

# Get Port first (usually available immediately)
service_port=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.ports[?(@.name=="https")].port}' 2>/dev/null)
echo "Service Port: $service_port" >&2
if [[ $? -ne 0 || -z "$service_port" ]]; then
    echo "Error: Failed to retrieve port 'http' from service '$SERVICE_NAME' in namespace '$NAMESPACE'." >&2
    echo "Please check if the service exists and is correctly configured." >&2
    return 1
fi

# Wait for LoadBalancer IP
echo "Waiting up to $TIMEOUT seconds for LoadBalancer IP..." >&2
lb_ip=""
start_time=$(date +%s)
while true; do
    # Try getting IP first, then hostname if IP is empty
    lb_ip=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [[ -z "$lb_ip" ]]; then
        lb_ip=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
    fi

    if [[ -n "$lb_ip" ]]; then
        echo "LoadBalancer IP/Hostname found: $lb_ip" >&2
        break
    fi

    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [[ $elapsed_time -ge $TIMEOUT ]]; then
        echo "Error: Timed out waiting for LoadBalancer IP/Hostname for service '$SERVICE_NAME' after $TIMEOUT seconds." >&2
        echo "Check the service status: kubectl get service $SERVICE_NAME -n $NAMESPACE -o wide" >&2
        return 1
    fi

    echo -n "." >&2 # Progress indicator
    sleep 5
done

export ES_HOST="$lb_ip"
export ES_PORT="$service_port"
echo "Successfully exported ES_HOST=$ES_HOST and ES_PORT=$ES_PORT." >&2
echo "You can now use these variables in this shell session." >&2

# Prevent the rest of the script from executing if sourced multiple times without resetting OPTIND properly outside
return 0