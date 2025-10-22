# System Architecture

## High-Level Overview
[Diagram showing: User → ALB → EKS → Pods → Model]

## Components
- Frontend: HTML/JS
- Backend: Flask API
- Model: XGBoost (pickle)
- Infrastructure: AWS (VPC, RDS)
- Monitoring: Prometheus, Grafana