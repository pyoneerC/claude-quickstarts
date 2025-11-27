# Deployment Guide

This guide covers deploying the Computer Use Demo backend to various cloud platforms.

## Prerequisites

- Docker installed
- Cloud provider account (AWS, GCP, or Azure)
- Domain name (optional, for production)
- SSL certificate (for HTTPS)

## General Preparation

### 1. Environment Variables

Create a production `.env` file:

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# CORS (comma-separated origins)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# VNC Configuration
VNC_HOST=0.0.0.0
VNC_PORT=5900
NOVNC_PORT=6080
```

### 2. Build Docker Image

```bash
docker build -f Dockerfile.backend -t computer-use-demo:latest .
```

## AWS Deployment

### Option 1: AWS ECS with Fargate

#### 1. Create ECR Repository

```bash
aws ecr create-repository --repository-name computer-use-demo
```

#### 2. Push Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag computer-use-demo:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/computer-use-demo:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/computer-use-demo:latest
```

#### 3. Create RDS PostgreSQL Database

```bash
aws rds create-db-instance \
    --db-instance-identifier computer-use-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password <password> \
    --allocated-storage 20
```

#### 4. Create ECS Task Definition

Create `task-definition.json`:

```json
{
  "family": "computer-use-demo",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "computer-use-demo",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/computer-use-demo:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        },
        {
          "containerPort": 6080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://user:pass@rds-endpoint:5432/dbname"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:anthropic-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/computer-use-demo",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 5. Create ECS Service

```bash
aws ecs create-service \
    --cluster default \
    --service-name computer-use-demo \
    --task-definition computer-use-demo \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### 6. Set Up Application Load Balancer

Create ALB and configure target groups for ports 8000 and 6080.

### Option 2: AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance

# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# Clone repository
git clone <your-repo>
cd computer-use-demo

# Create .env file
nano .env

# Start with Docker Compose
docker-compose up -d
```

## Google Cloud Platform Deployment

### Option 1: Cloud Run

#### 1. Enable APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

#### 2. Build and Push Image

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/computer-use-demo

# Or use Docker
docker tag computer-use-demo:latest gcr.io/PROJECT_ID/computer-use-demo
docker push gcr.io/PROJECT_ID/computer-use-demo
```

#### 3. Create Cloud SQL PostgreSQL Instance

```bash
gcloud sql instances create computer-use-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1
```

#### 4. Deploy to Cloud Run

```bash
gcloud run deploy computer-use-demo \
    --image gcr.io/PROJECT_ID/computer-use-demo \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=postgresql+asyncpg://... \
    --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest \
    --port 8000 \
    --memory 2Gi \
    --timeout 3600
```

**Note:** Cloud Run has limitations for VNC access. Consider using GCE for full functionality.

### Option 2: Google Compute Engine

```bash
# Create VM
gcloud compute instances create computer-use-demo \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --boot-disk-size=30GB

# SSH and setup (similar to AWS EC2)
```

## Azure Deployment

### Option 1: Azure Container Instances

#### 1. Create Resource Group

```bash
az group create --name computer-use-rg --location eastus
```

#### 2. Create Azure Database for PostgreSQL

```bash
az postgres server create \
    --resource-group computer-use-rg \
    --name computer-use-db \
    --location eastus \
    --admin-user postgres \
    --admin-password <password> \
    --sku-name B_Gen5_1
```

#### 3. Push Image to Azure Container Registry

```bash
# Create ACR
az acr create --resource-group computer-use-rg --name computerusedemo --sku Basic

# Login to ACR
az acr login --name computerusedemo

# Tag and push
docker tag computer-use-demo:latest computerusedemo.azurecr.io/computer-use-demo:latest
docker push computerusedemo.azurecr.io/computer-use-demo:latest
```

#### 4. Deploy Container

```bash
az container create \
    --resource-group computer-use-rg \
    --name computer-use-demo \
    --image computerusedemo.azurecr.io/computer-use-demo:latest \
    --cpu 1 \
    --memory 2 \
    --ports 8000 6080 \
    --environment-variables \
        DATABASE_URL=postgresql+asyncpg://... \
    --secure-environment-variables \
        ANTHROPIC_API_KEY=<your-key> \
    --dns-name-label computer-use-demo
```

### Option 2: Azure Virtual Machines

Similar to AWS EC2 deployment.

## Production Checklist

### Security

- [ ] Use HTTPS with valid SSL certificate
- [ ] Store API keys in secrets manager (not environment variables)
- [ ] Configure CORS to only allow trusted domains
- [ ] Set up VPN or IP whitelisting for VNC access
- [ ] Enable authentication for API endpoints
- [ ] Use security groups/firewall rules
- [ ] Regularly update dependencies

### Database

- [ ] Use managed database service (RDS, Cloud SQL, etc.)
- [ ] Enable automatic backups
- [ ] Set up read replicas for scaling
- [ ] Configure connection pooling
- [ ] Monitor database performance

### Monitoring

- [ ] Set up logging (CloudWatch, Stackdriver, Application Insights)
- [ ] Configure error tracking (Sentry, Rollbar)
- [ ] Set up uptime monitoring
- [ ] Create alerts for errors and high resource usage
- [ ] Monitor API response times

### Performance

- [ ] Use CDN for static files
- [ ] Configure caching where appropriate
- [ ] Optimize database queries
- [ ] Set up auto-scaling
- [ ] Load test the application

### Backup & Recovery

- [ ] Regular database backups
- [ ] Document recovery procedures
- [ ] Test backup restoration
- [ ] Version control for configurations

## Scaling Considerations

### Horizontal Scaling

To scale the application horizontally:

1. **Session Affinity**: Use sticky sessions or external session storage
2. **Database**: Use connection pooling and read replicas
3. **Load Balancing**: Configure ALB/GCLB to distribute traffic
4. **WebSocket**: Ensure load balancer supports WebSocket connections

### Vertical Scaling

Adjust container resources:
- CPU: 2-4 cores recommended
- Memory: 4-8GB recommended
- Storage: 20GB minimum

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs <container-id>

# Check environment variables
docker exec <container-id> env

# Access container shell
docker exec -it <container-id> bash
```

### Database connection issues

```bash
# Test connection
docker exec <container-id> python -c "import asyncio; from backend.database import init_db; asyncio.run(init_db())"
```

### VNC not accessible

- Check security groups allow ports 5900 and 6080
- Verify VNC_HOST is set to 0.0.0.0
- Check container logs for X server errors

## Cost Optimization

### AWS
- Use Fargate Spot for cost savings
- Use RDS reserved instances
- Set up auto-scaling to scale down during low usage

### GCP
- Use committed use discounts
- Use Cloud Run (pay per request)
- Set up auto-scaling

### Azure
- Use Azure Reserved VM Instances
- Use Azure Database for PostgreSQL reserved capacity
- Configure auto-shutdown for development instances

## Support

For issues:
1. Check application logs
2. Review security group/firewall rules
3. Verify environment variables
4. Check database connectivity
5. Review resource utilization

For additional help, open an issue on GitHub.
