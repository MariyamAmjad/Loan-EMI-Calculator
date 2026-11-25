# Loan EMI Calculator on Kubernetes (Minikube)

DS-584 Cloud Computing, Assignment 4.
A Loan EMI calculator (HTML, jQuery, Bootstrap, Node.js/Express) that stores every calculation in a 3-member MongoDB replica set. It is deployed on Minikube with NGINX Ingress, load balancing, self-healing and HPA autoscaling.

## Folder structure
- app/ : web application, Dockerfile, .dockerignore
- k8s/ : all Kubernetes manifests
- scripts/ : benchmark, profiling and graph scripts
- results/ : raw outputs (CSV, JSON, logs) and graphs

## Prerequisites
Minikube, kubectl, Docker, Python 3 (for the scripts).

## Bring up the whole system on a fresh Minikube cluster
1. Start Minikube and enable the addons:

        minikube start
        minikube addons enable ingress
        minikube addons enable metrics-server

2. Build the image and load it into Minikube:

        docker build -t emi-web:1.0 ./app
        minikube image load emi-web:1.0

3. Apply all manifests (namespace first, then everything else):

        kubectl apply -f k8s/00-namespace.yaml
        kubectl apply -f k8s/

   The web pods become Ready only after MongoDB is reachable. The mongo-init Job initiates the replica set rs0.

4. Check the cluster state:

        kubectl get all,pvc,configmap -n emi -o wide

5. Map emi.local to the cluster in /etc/hosts (use the output of minikube ip):

        echo "$(minikube ip) emi.local" | sudo tee -a /etc/hosts

6. Open http://emi.local

## Scripts (scripts/)
- run_benchmark.py : runs the load test at a given request rate
- collect_metrics.py : saves host CPU (every 1 s) and kubectl top pods (every 15 s) to CSV
- collect_hpa_metrics.py : records the HPA replica count every 15 s
- summarize_benchmarks.py : builds results/fixed_replica_summary.csv
- plot_graph1.py, plot_graph2.py, plot_graph3.py : generate Graphs 1 to 3

## Results (results/)
Raw outputs of the 15 fixed-replica runs, the autoscaling test, profiling CSV files, MongoDB replica set logs, the persistence test and the three graphs.
