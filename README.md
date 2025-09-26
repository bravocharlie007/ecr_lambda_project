# Family Gaming Cloud Platform

## Overview

This repository contains the **API and Lambda functions** for a family-friendly cloud gaming platform built on AWS. The project enables you and your family members to spin up on-demand Windows gaming instances with automated management, without requiring fixed IP addresses.

## Multi-Workspace Architecture

**Note:** This repository is part of a larger multi-workspace setup. The complete platform requires the following workspaces/repositories:

### Workspace Dependencies & Deployment Order

1. **VPC Workspace** (External - handles network foundation)
   - Creates VPC, subnets, internet gateway, NAT gateway
   - Configures route tables and network ACLs
   - Sets up VPN endpoints for secure family access

2. **Compute Workspace** (External - handles ALB/NLB and gaming instances)  
   - Creates Application Load Balancer in public subnets
   - Configures target groups for Lambda functions
   - Manages EC2 gaming instances in private subnets
   - Sets up Auto Scaling groups for cost optimization

3. **This Repository** (API Lambda functions)
   - Gaming instance management APIs
   - User authentication and authorization
   - Save game backup automation
   - Session management and monitoring

### Deployment Sequence
```bash
1. Deploy VPC workspace first (network foundation)
2. Deploy Compute workspace second (ALB + EC2 instances)  
3. Deploy this Lambda workspace third (API layer)
4. Configure DNS and certificates last
```

## Architecture for Family Gaming

### Core Components

1. **AWS Lambda Functions** (`github_lambda.py`)
   - RESTful APIs for gaming instance management
   - Secure user authentication (no IP restrictions needed)
   - Automated save game backups to S3
   - Session monitoring and cost controls

2. **Docker Container** (`build/Dockerfile`)
   - AWS Lambda Python runtime for security
   - Non-root user configuration
   - Vulnerability scanning in CI/CD

3. **Secure CI/CD Pipeline** (`.github/workflows/main.yml`)
   - OIDC authentication (no long-lived credentials)
   - Security scanning before deployment
   - Automated testing and validation
   - Multi-environment support

### Family-Friendly Security Model

**Problem Solved:** How to give family members secure access without knowing their IP addresses

**Solutions Implemented:**

#### Option 1: AWS Client VPN (Recommended)
- Family members install AWS VPN client
- Gaming instances stay in private subnets  
- No public IP exposure needed
- Most secure option

#### Option 2: Tailscale Mesh VPN (Easiest)
- Install Tailscale on gaming instances and family devices
- Creates secure mesh network automatically
- Works through any firewall/NAT
- Zero configuration required

#### Option 3: Web-based Authentication
- AWS Cognito for user management
- Session-based access tokens
- Multi-factor authentication support
- Web browser access (no client software)

### Gaming Infrastructure

Based on the documentation, the complete platform includes:

#### Gaming Instances (Managed by Compute Workspace)
- **EC2 Instances**: Windows-based gaming with:
  - GPU drivers (NVIDIA Gaming, AMD Windows drivers)
  - Steam and SteamCMD pre-installed
  - DirectX and gaming frameworks
  - Automated driver installation
  - User profile isolation (non-admin accounts for family)

#### Storage & Backup
- **S3 Buckets**: 
  - Driver storage and distribution
  - Automated save game backups
  - Cross-region replication for disaster recovery
- **EBS Volumes**: Instance storage with encryption
- **Automated Backup**: Save games copied every hour

#### Network Security (VPC Workspace)
- **Private Subnets**: Gaming instances not directly accessible
- **Security Groups**: Restrictive access rules
- **VPN Access**: Secure family member connections
- **Multi-AZ**: High availability across regions

## API Endpoints

### Gaming Instance Management
```bash
GET    /gaming/instances          # List user's instances
POST   /gaming/instances          # Create new instance  
PUT    /gaming/instances/{id}     # Start/stop/terminate instance
GET    /health                    # System health check
```

### Example Usage
```bash
# Create gaming instance
curl -X POST https://api.gaming.yourdomain.com/gaming/instances \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"instance_type": "g4dn.xlarge"}'

# Start instance
curl -X PUT https://api.gaming.yourdomain.com/gaming/instances/i-12345 \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"action": "start"}'
```

## Development Roadmap

### Version 1 ✅ (Current)
- ✅ Secure API Lambda functions
- ✅ Basic instance management APIs
- ✅ Security improvements (OIDC, input validation)
- ✅ CI/CD with vulnerability scanning

### Version 2 (Planned)
- Database integration (PostgreSQL/TimescaleDB)
- Advanced features: AMI creation, snapshot management
- Step Functions for complex workflows
- Multiple instance type support with game-specific recommendations

### Version 3 (Future)
- Multi-tenant user onboarding/offboarding
- Per-user billing and usage tracking
- Advanced monitoring and analytics
- Integration with game libraries and mod support

## Security Improvements Made

### 🔒 Critical Issues Fixed

1. **AWS Credentials Security**
   - ❌ Before: Long-lived access keys in GitHub secrets
   - ✅ After: OIDC roles with temporary credentials
   - ✅ Added: Least-privilege IAM policies

2. **SQL Injection Prevention**
   - ❌ Before: Malformed SQL with potential injection
   - ✅ After: Parameterized queries with proper validation
   - ✅ Added: Input sanitization and validation

3. **Container Security**
   - ❌ Before: Generic Python image, root user
   - ✅ After: AWS Lambda base image, non-root user
   - ✅ Added: Vulnerability scanning in CI/CD

4. **Network Security**
   - ❌ Before: Direct RDP/SSH exposure planned
   - ✅ After: VPN-based access, private subnets
   - ✅ Added: Security group restrictions

### 🛡️ Family-Specific Security Features

1. **User Authentication**
   - Session-based access tokens
   - Multi-factor authentication support
   - User activity logging and monitoring

2. **Cost Controls**
   - Automatic instance shutdown after 30 minutes idle
   - Billing alerts at $50, $100, $200
   - Usage tracking per family member

3. **Data Protection**
   - Encrypted S3 buckets for save games
   - Automated backups with versioning
   - Cross-region disaster recovery

## Getting Started

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker installed for local testing
- Python 3.9+ for development

### Family Member Setup
1. **Option 1 - VPN:** Install AWS Client VPN profile
2. **Option 2 - Tailscale:** Install Tailscale client
3. **Option 3 - Web:** Access through web portal

### Local Development
```bash
# Install dependencies
pip install -r build/requirements.txt

# Test Lambda function locally
python -c "
import github_lambda
result = github_lambda.lambda_handler({'path': '/health', 'httpMethod': 'GET'}, {})
print(result)
"
```

### Deployment
The project automatically deploys on pushes to master branch:
1. Security scanning runs first
2. Code is deployed to Lambda
3. Docker image is built and pushed to ECR
4. S3 artifacts are updated with encryption

## Cost Estimation

### Monthly Costs (Family of 4)
- **Lambda API calls:** ~$5-10/month
- **Gaming instances (g4dn.xlarge):** $0.526/hour
  - 20 hours/week usage: ~$42/month per active user
- **Storage (S3 + EBS):** ~$10-20/month
- **VPN (if using AWS Client VPN):** ~$22/month
- **Data transfer:** ~$5-15/month

**Total estimated:** $80-120/month for active family gaming

### Cost Optimization Tips
- Use Spot instances for 60-70% savings
- Automatic shutdown after 30 minutes idle
- Reserved instances for predictable usage
- Cross-region replication only for critical data

## Monitoring & Maintenance

### CloudWatch Dashboards
- Instance usage and costs
- Family member activity
- Save game backup status
- Security events and alerts

### Regular Maintenance
- Monthly cost review
- Security patch updates
- Save game cleanup (keep last 30 days)
- Performance optimization

## Support & Troubleshooting

### Common Issues
1. **Can't connect to gaming instance**
   - Check VPN connection status
   - Verify security group rules
   - Confirm instance is running

2. **High costs**
   - Review auto-shutdown settings
   - Check for zombie instances
   - Consider Spot instances

3. **Save game not backed up**
   - Check S3 bucket permissions
   - Verify Lambda execution logs
   - Test backup Lambda manually

### Emergency Contacts
- Platform Admin: (Your contact info)
- AWS Support: Enterprise support recommended
- Security Issues: See SECURITY.md

---

*Last Updated: September 2024*  
*Original Project: ~2022*  
*Security Hardened: September 2024*