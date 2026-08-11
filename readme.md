# DevSecOps & Site Reliability Engineering (SRE) Assessment

## Overview

You have been assigned to deploy and manage a new microservice for our infrastructure. The application is a lightweight Python service that is known to have a memory leak, it starts at around 100MB and slowly increases its memory footprint to 1GB over the course of 5 minutes. It also generates standard application logs. 

Your mission is to build a secure delivery pipeline, implement a GitOps deployment strategy, and set up robust observability and alerting to catch the application when it inevitably crashes.

**Rules:**
- Everything should be done using free/open-source tools running locally (e.g., Minikube, Kind, K3d). No cloud accounts are required.
- Security controls are currently enforced **only** in the CI/CD pipeline. 
- Provide clear documentation on your setup, architecture, and instructions to reproduce your environment.

---

## Task 1: Dockerization & Secure CI/CD Pipeline

The application code is provided in the repository. Your first task is to containerize it and build a secure delivery pipeline.

1. **Dockerize the Application:**
   - Create an **optimal** `Dockerfile` for the provided Python application.
   - Keep the image size as small as possible while ensuring the application runs correctly.
   - Follow container security best practices (e.g., use a minimal base image, run as a non-root user).
2. **Secure CI/CD Pipeline (GitHub Actions or similar):**
   - Create a pipeline that builds the Docker image.
   - Design the pipeline so that it concurrently builds and tests the image against multiple different versions of the base runtime environment dynamically, without manually duplicating the pipeline jobs.
   - Integrate security scanning tools into the pipeline:
     - **Secret Scanning** (e.g., Gitleaks) *(Optional)*
     - **SAST** (Static Application Security Testing)
     - **Container Image Vulnerability Scanning** (e.g., Trivy or Grype)
   - If the image passes all security checks, push it to a container registry (e.g., Docker Hub, GHCR).

---

## Task 2: GitOps Deployment with ArgoCD

We use GitOps to manage our Kubernetes clusters. You need to automate the deployment of the image you just pushed.

1. **ArgoCD Setup:**
   - Install and configure ArgoCD on your local Kubernetes cluster.
2. **Kubernetes Manifests:**
   - Create the necessary Kubernetes manifests (Deployment, Service) for the application.
   - **Crucial:** Since the application has a known memory leak (designed to reach 500MB over 2 minutes), you must configure **Resource Requests and Limits** for the Pod. Set the memory limit explicitly to `400Mi` so that the Kubernetes scheduler terminates the pod (`OOMKilled`) well before it consumes node resources.
3. **Automated Deployment & Image Updates:**
   - Configure ArgoCD to track your repository and automatically deploy/sync the application.
   - **Important:** Do NOT configure your CI/CD pipeline to commit and push image tag updates back to your configuration repository. Instead, implement a dedicated tool or controller that automatically monitors the container registry for new image tags and updates the deployment automatically.
   
   > [!NOTE]
   > **ArgoCD Image Updater**
   > 
   > **Why we use it:** Updating image tags in Git via a CI pipeline requires giving your CI runner write access to your Git repository, which can be a security risk and clutters your git history with automated commits.
   > 
   > **How it works:** ArgoCD Image Updater polls your container registry for new tags. When it detects a new tag that matches your criteria (e.g., a specific semantic version range or regex), it signals ArgoCD to update the application.
   > 
   > **Ways of using it:** 
   > 1. **Imperative (Direct) Update:** The updater directly modifies the ArgoCD Application resource in the cluster's memory/etcd (fast, but causes drift from Git).
   > 2. **Declarative (Git Write-back):** The updater commits the new tag back to Git (maintains GitOps purity). For this assessment, you may use either method as long as the CI pipeline isn't doing the git commit!

---

## Task 3: Observability, Logging, & Alerting

Visibility into the cluster and the application's behavior is critical.

1. **Metrics & Dashboards:**
   - Install **Prometheus** and **Grafana** in your cluster(via Helm).
   - Build a comprehensive Grafana Dashboard that displays(You Can also import them):
     - **Node Metrics:** CPU, Memory, and Disk usage.
     - **Pod & Cluster Metrics:** CPU and Memory usage per pod.
2. **Alerting:**
   - Configure Prometheus/Alertmanager rules to trigger alerts for the following scenarios:
     - **Application Health Check Failures** (Pod goes down or becomes unready).
     - **OOMKilled Events** (Triggered when the application hits its memory limit).
   - *Bonus:* Route these alerts to a Slack webhook or an email address.

---

## Evaluation Criteria

- **Security Posture:** Quality of the Dockerfile and thoroughness of the CI/CD security gates.
- **GitOps Implementation:** A working ArgoCD setup that successfully detects and deploys changes.
- **Kubernetes Expertise:** Correct implementation of resource limits ensuring the `OOMKilled` behavior occurs as intended.
- **Observability:** A functional, well-designed Grafana dashboard.
- **Reliability Engineering:** Accurate and functional alerting rules for health checks and OOM limits.
