# Security Guide for Family Gaming Cloud Platform

## Overview

This document outlines security best practices and configurations for running a secure family gaming cloud platform without requiring fixed IP addresses.

## Authentication & Access Control

### For Family Members (Recommended Solutions)

#### Option 1: AWS Client VPN (Most Secure)
```bash
# Family members install AWS VPN client
# Connect to VPN before accessing gaming instances
# Gaming instances remain in private subnets
```

**Pros:** Most secure, no IP restrictions needed
**Cons:** Requires VPN client installation

#### Option 2: Tailscale Mesh VPN (Easiest)
```bash
# Install Tailscale on gaming instances and family devices
# Creates secure mesh network
# No port forwarding or public IPs needed
```

**Pros:** Zero-config, works across NATs
**Cons:** Third-party dependency

#### Option 3: Dynamic DNS + OAuth (Flexible)
```bash
# Use AWS Cognito or Auth0 for user authentication
# Combined with AWS ALB authentication
# Session-based access tokens
```

**Pros:** Web-based, no client software
**Cons:** Still requires some public exposure

### Current Security Issues Fixed

1. **AWS Credentials:** Switched from long-lived access keys to OIDC roles
2. **SQL Injection:** Implemented parameterized queries
3. **Container Security:** Using AWS Lambda base images, non-root user
4. **Input Validation:** Added request validation and sanitization

## Infrastructure Security

### Network Architecture
```
Internet Gateway
    ↓
Application Load Balancer (Public Subnet)
    ↓
Lambda Functions (Private Subnet)
    ↓
Gaming EC2 Instances (Private Subnet)
    ↓
Database (Private Subnet)
```

### Required AWS Resources

#### IAM Roles
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:bravocharlie007/ecr_lambda_project:ref:refs/heads/master"
        }
      }
    }
  ]
}
```

#### Security Groups
```bash
# Gaming instances (private subnet)
- Inbound: VPN subnet only (10.0.0.0/8)
- Outbound: Internet for game downloads

# ALB (public subnet)  
- Inbound: HTTPS (443) from anywhere
- Outbound: Lambda subnets only

# Lambda functions
- Inbound: ALB security group only
- Outbound: Gaming instances, RDS, internet
```

## Secrets Management

### GitHub Secrets Required
```bash
AWS_ROLE_ARN                    # OIDC role for deployment
AWS_REGION                      # us-east-1, us-west-2, etc.
ECR_REPOSITORY                  # ECR repo name
S3_BUCKET                       # Deployment bucket
LAMBDA_EXECUTION_ROLE_ARN       # Lambda execution role
```

### Environment Variables (Lambda)
```bash
DB_HOST                         # RDS endpoint
DB_NAME                         # Database name
DB_USER                         # Database user
DB_PASS                         # Store in AWS Secrets Manager
ALLOWED_USERS                   # Comma-separated user IDs
SESSION_TIMEOUT                 # Default: 3600
```

## Cost & Monitoring Security

### Auto-Shutdown Policy
```python
# Implement in Lambda
def check_inactive_instances():
    # Shut down instances idle > 30 minutes
    # Send notifications before shutdown
    # Backup save games to S3
```

### CloudWatch Alarms
```bash
# Set up billing alerts
# Monitor unusual instance launches
# Track failed authentication attempts
# Alert on high data transfer
```

## Family-Friendly Security Model

### User Management
1. **Family Admin (You):** Full control, billing access
2. **Family Members:** Instance management only for their instances
3. **Guest Users:** Read-only access, no instance creation

### Session Management
```python
# Implement session timeouts
# Force re-authentication after inactivity
# Log all instance actions for auditing
```

### Save Game Protection
```bash
# Automatic S3 backup every hour
# Versioned backups (keep last 10)
# Cross-region replication for disaster recovery
```

## Emergency Procedures

### Instance Compromise
1. Terminate instance immediately via Lambda API
2. Check CloudTrail logs for unauthorized actions
3. Rotate all access credentials
4. Review security group rules

### Cost Overrun
1. Set up billing alerts ($50, $100, $200)
2. Implement emergency shutdown Lambda
3. Monitor Spot instance pricing
4. Use reserved instances for base capacity

## Security Checklist

- [ ] Enable AWS CloudTrail in all regions
- [ ] Set up AWS Config for compliance monitoring
- [ ] Enable VPC Flow Logs
- [ ] Configure AWS GuardDuty for threat detection
- [ ] Set up AWS Security Hub for centralized security findings
- [ ] Enable AWS WAF on ALB
- [ ] Configure AWS Shield for DDoS protection
- [ ] Set up AWS Inspector for vulnerability assessments
- [ ] Enable EBS encryption by default
- [ ] Configure S3 bucket encryption and versioning
- [ ] Set up cross-region backups
- [ ] Test disaster recovery procedures

## Contact & Incident Response

For security incidents or questions, contact the platform administrator immediately.

**Important:** Never share AWS credentials, API keys, or RDP passwords through insecure channels.