# Security Guide for EC2 Deployment Automation Platform

## Overview

This document outlines security best practices and configurations for running a secure EC2 deployment automation platform for web applications, with controlled access for family members without requiring fixed IP addresses.

## Authentication & Access Control

### For Family Members (Web Platform Management)

#### Option 1: SSH Bastion Host (Most Secure)
```bash
# Family members SSH to bastion host first
ssh -i cloud_gaming.pem ec2-user@bastion-host-ip
# Then SSH to target web servers
ssh ec2-user@private-server-ip
```

**Pros:** Most secure, controlled access, audit logging
**Cons:** Two-step SSH process

#### Option 2: AWS Systems Manager Session Manager (Easiest)
```bash
# Family members use AWS CLI/Console
aws ssm start-session --target i-1234567890abcdef0
# Browser-based access through AWS Console
```

**Pros:** No SSH keys needed, browser-based access
**Cons:** Requires AWS CLI setup or console access

#### Option 3: VPN Access (Most Flexible)
```bash
# Install AWS Client VPN or third-party VPN solution
# Direct access to private subnets after VPN connection
```

**Pros:** Transparent access, works with all tools
**Cons:** VPN client setup required

### Current Security Issues Fixed

1. **SSH Access Controls:** Implemented bastion host patterns and SSM access
2. **Password Authentication:** Disabled in favor of key-based authentication
3. **Container Security:** Using AWS Lambda base images, vulnerability scanning
4. **Network Segmentation:** Proper security group controls between tiers

## Infrastructure Security

### Network Architecture
```
Internet Gateway
    ↓
Application Load Balancer (Public Subnet)
    ↓
Web Servers (Public/Private Subnets with EIPs)
    ↓
Database (Private Subnet - when implemented)
```

### Required AWS Resources

#### Security Groups (Compute Workspace)
```hcl
# ALB Security Group - Internet facing
resource "aws_security_group" "alb_sg" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Web Server Security Group - ALB only
resource "aws_security_group" "web_sg" {
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }
  
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }
}

# Bastion Host Security Group - Family IPs only
resource "aws_security_group" "bastion_sg" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [
      "YOUR_HOME_IP/32",
      "BROTHER_1_IP/32",
      "BROTHER_2_IP/32"
    ]
  }
}
```

#### IAM Roles for Enhanced Security
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

## Web Application Security

### HTTPS Implementation
```hcl
# Certificate Manager certificate
resource "aws_acm_certificate" "web_cert" {
  domain_name       = "yourdomain.com"
  validation_method = "DNS"
  
  subject_alternative_names = [
    "*.yourdomain.com"
  ]
  
  lifecycle {
    create_before_destroy = true
  }
}

# ALB HTTPS listener
resource "aws_alb_listener" "https" {
  load_balancer_arn = aws_alb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.web_cert.arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.web.arn
  }
}

# HTTP to HTTPS redirect
resource "aws_alb_listener" "http_redirect" {
  load_balancer_arn = aws_alb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

### Web Server Hardening
```bash
# Update compute/user_data/userdata.ssh with security hardening
#!/bin/bash
sudo su
yum update -y
yum install httpd -y

# Apache security configuration
echo "ServerTokens Prod" >> /etc/httpd/conf/httpd.conf
echo "ServerSignature Off" >> /etc/httpd/conf/httpd.conf
echo "Header always set X-Frame-Options DENY" >> /etc/httpd/conf/httpd.conf
echo "Header always set X-Content-Type-Options nosniff" >> /etc/httpd/conf/httpd.conf

# SSH hardening
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
echo "AllowUsers ec2-user" >> /etc/ssh/sshd_config
echo "MaxAuthTries 3" >> /etc/ssh/sshd_config
echo "ClientAliveInterval 300" >> /etc/ssh/sshd_config
echo "ClientAliveCountMax 2" >> /etc/ssh/sshd_config

systemctl restart sshd
systemctl start httpd
systemctl enable httpd

# Create web content
EC2_AVAIL_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
echo "<h1>Web Server $(hostname -f) in AZ $EC2_AVAIL_ZONE</h1>" > /var/www/html/index.html
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
# Store sensitive values in AWS Secrets Manager
DB_CONNECTION_STRING            # If database is added
API_KEYS                        # For external integrations
ALLOWED_USERS                   # Family member user IDs
```

## Cost & Monitoring Security

### Cost Controls
```python
# Implement in Lambda
def check_resource_costs():
    # Monitor ALB, EC2, and Lambda costs
    # Alert when exceeding $100/month
    # Auto-terminate unused resources
```

### CloudWatch Monitoring
```bash
# Set up alarms for:
# - Failed SSH attempts
# - High CPU usage on web servers
# - ALB 4xx/5xx error rates
# - Lambda function errors
# - Unusual API call patterns
```

## Family Access Model

### Role-Based Access
1. **Platform Admin (You):** Full AWS access, Terraform deployment
2. **Family Developers:** SSH access to web servers, limited AWS API access
3. **Web Users:** HTTP/HTTPS access to deployed applications only

### Access Patterns
```bash
# Family members can:
# 1. Access web applications via ALB DNS
# 2. SSH to servers via bastion host or SSM
# 3. Deploy new applications via EC2-Deployer API
# 4. View logs and metrics (read-only AWS console access)
```

## Emergency Procedures

### Server Compromise
1. Terminate affected EC2 instance via AWS Console
2. Check CloudTrail logs for unauthorized actions
3. Rotate SSH keys and API credentials
4. Review security group rules

### Cost Overrun
1. Set up billing alerts at $25, $50, $100
2. Implement automatic resource shutdown
3. Use AWS Budgets for cost tracking
4. Monitor reserved instance utilization

## Security Checklist

### Infrastructure Security
- [ ] Enable AWS CloudTrail in all regions
- [ ] Set up AWS Config for compliance monitoring
- [ ] Enable VPC Flow Logs
- [ ] Configure AWS GuardDuty for threat detection
- [ ] Set up AWS Security Hub for centralized findings
- [ ] Enable AWS WAF on ALB
- [ ] Configure AWS Shield for DDoS protection

### Web Application Security
- [ ] Implement HTTPS with valid certificates
- [ ] Configure security headers (X-Frame-Options, etc.)
- [ ] Set up log aggregation and monitoring
- [ ] Implement backup and recovery procedures
- [ ] Test disaster recovery scenarios
- [ ] Regular security updates for EC2 instances

### Access Control
- [ ] Implement bastion host or SSM access
- [ ] Disable password authentication
- [ ] Use IAM roles instead of access keys
- [ ] Enable MFA for AWS console access
- [ ] Regular access review (quarterly)
- [ ] Audit SSH key usage

### Monitoring & Alerting
- [ ] CloudWatch alarms for system health
- [ ] Cost monitoring and alerts
- [ ] Security event notifications
- [ ] Performance monitoring dashboards
- [ ] Log retention policies
- [ ] Incident response procedures

## Contact & Incident Response

### Family Access Issues
- Platform admin contact for SSH key distribution
- Documentation for common troubleshooting steps
- Escalation procedures for emergencies

### Security Incidents
- Immediate isolation procedures
- Evidence preservation steps
- Communication protocols
- Recovery and lessons learned process

**Important:** This is a web application hosting platform, not a gaming platform. Security measures are focused on protecting web servers, databases, and API endpoints rather than gaming instances.