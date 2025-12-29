Below is a **clean, copy-paste ready README.md** you can put directly into your Git repo.
It is written for **Docker → GKE (Kubernetes on Google Cloud)** and avoids all the issues you just faced (auth plugin, image name, external IP, refused connection).

---

# Docker to Kubernetes Deployment on Google Cloud (GKE)

This guide explains how to **containerize an application using Docker** and **deploy it to Kubernetes (GKE)** on Google Cloud.

---

## Architecture Overview

![Image](https://miro.medium.com/v2/resize%3Afit%3A1400/1%2A49X3DOOECL0Ox5bj0QsfbQ.jpeg)

![Image](https://docs.cloud.google.com/static/kubernetes-engine/images/gke-architecture.svg)

![Image](https://www.densify.com/wp-content/uploads/article-k8s-capacity-kubernetes-service-overview.svg)

```
Git Repository
   ↓
Docker Image
   ↓
Artifact Registry (GCP)
   ↓
GKE Cluster
   ↓
Kubernetes Deployment + Service
   ↓
Public Load Balancer (External IP)
```

---

## Prerequisites

* Google Cloud account with billing enabled
* Google Cloud SDK installed
* Docker installed
* kubectl installed
* Git repository with application code
* Application must listen on `0.0.0.0`

---

## Authenticate & Configure Google Cloud

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud config set compute/region asia-south1
```

Enable required APIs:

```bash
gcloud services enable \
container.googleapis.com \
artifactregistry.googleapis.com
```

---

## Install GKE Authentication Plugin (IMPORTANT)

```bash
gcloud components install gke-gcloud-auth-plugin
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
```

Persist it:

```bash
echo 'export USE_GKE_GCLOUD_AUTH_PLUGIN=True' >> ~/.zshrc
source ~/.zshrc
```

---

## Create Artifact Registry (Docker Images)

```bash
gcloud artifacts repositories create my-repo \
  --repository-format=docker \
  --location=asia-south1
```

Authenticate Docker:

```bash
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

---

## Build & Push Docker Image

```bash
docker build -t asia-south1-docker.pkg.dev/<PROJECT_ID>/my-repo/my-app:1.0 .
docker push asia-south1-docker.pkg.dev/<PROJECT_ID>/my-repo/my-app:1.0
```

Verify image:

```bash
gcloud artifacts docker images list asia-south1-docker.pkg.dev/<PROJECT_ID>/my-repo
```

---

## Create GKE Cluster

```bash
gcloud container clusters create my-gke-cluster \
  --num-nodes=2 \
  --machine-type=e2-standard-4 \
  --region=asia-south1
```

Configure kubectl:

```bash
gcloud container clusters get-credentials my-gke-cluster \
  --region asia-south1
```

Verify:

```bash
kubectl get nodes
```

---

## Kubernetes Deployment

### `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: asia-south1-docker.pkg.dev/<PROJECT_ID>/my-repo/my-app:1.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
```

---

## Kubernetes Service (External IP)

### `service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

---

## Deploy to Kubernetes

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

Check pods:

```bash
kubectl get pods
```

Expected:

```
READY   STATUS
1/1     Running
```

---

## Get External IP

```bash
kubectl get svc my-app-service
```

Example:

```
EXTERNAL-IP: 34.xxx.xxx.xxx
```

Open in browser:

```
http://<EXTERNAL-IP>
```

---

## Troubleshooting

### Pod status: `InvalidImageName`

✔ Image name must include:

```
region-docker.pkg.dev/project-id/repository/image:tag
```

---

### External IP shows but site refuses connection

✔ App must listen on `0.0.0.0`

Examples:

* **Flask**

```python
app.run(host="0.0.0.0", port=8080)
```

* **FastAPI**

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

---

### External IP is `<pending>`

✔ Check GCP quota:

* Forwarding rules
* External IP addresses

---

## Production Recommendations

* Use **Ingress + HTTPS**
* Enable **Horizontal Pod Autoscaling**
* Store secrets in **Kubernetes Secrets**
* Use **CI/CD (GitHub Actions or Cloud Build)**

---

## Final Checklist

✔ Docker image pushed
✔ Pods running
✔ Service endpoints created
✔ External IP reachable

---

## Support

If deployment fails, check:

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl describe svc my-app-service
```

