# EC2 Deployment Automation Platform

## Overview

This repository contains a **basic Lambda function** that is part of a larger **EC2 deployment automation platform** built on AWS. The platform enables automated provisioning and management of web application infrastructure through multiple Terraform workspaces and Lambda APIs.

**CORRECTION:** After reviewing all related repositories, this is **NOT a gaming platform** as initially analyzed. It's a web application deployment automation system.

## Multi-Workspace Architecture

This platform consists of several interconnected Terraform workspaces and Lambda functions:

### Workspace Dependencies & Deployment Order

1. **VPC Workspace** (`bravocharlie007/vpc`)
   - Creates VPC (15.0.0.0/16), public/private subnets
   - Configures Internet Gateway and route tables
   - Provides network foundation for all other components
   - **Outputs**: vpc_id, subnet_id_list, igw_id, root_deployment_id

2. **Compute Workspace** (`bravocharlie007/compute`) 
   - Creates Application Load Balancer in public subnets
   - Provisions EC2 instances (t3.micro) running Apache web servers
   - Configures security groups for web traffic
   - Attaches Elastic IPs to instances
   - **Purpose**: Web application hosting infrastructure

3. **EC2-Deployer API Lambda** (`bravocharlie007/ec2-deployer-api-lambda`)
   - Advanced Lambda API for automated EC2 provisioning
   - Uses AWS Lambda Powertools for enterprise features
   - Supports instance "pave" requests (automated deployment)
   - **Purpose**: Production API for EC2 automation

4. **This Repository** (`bravocharlie007/ecr_lambda_project`)
   - Basic "Hello World" Lambda function
   - Learning/prototype implementation
   - CI/CD pipeline for containerized Lambda deployment
   - **Purpose**: Development/learning environment

5. **Zone Infrastructure** (`bravocharlie007/zone-infrastructure`)
   - Route 53 hosted zone management
   - DNS configuration for the platform
   - **Purpose**: DNS and domain management

### Deployment Sequence
```bash
1. Deploy VPC workspace first (network foundation)
2. Deploy Zone Infrastructure (DNS setup)
3. Deploy Compute workspace (ALB + web servers)
4. Deploy EC2-Deployer API Lambda (production API)
5. Deploy this Lambda workspace (development/testing)
```

## Actual Architecture (Web Application Platform)

### Core Components

1. **Application Load Balancer**
   - Internet-facing ALB distributing traffic to web servers
   - HTTP/HTTPS listeners (HTTPS redirect ready)
   - Target groups with health checks

2. **EC2 Web Servers**
   - t3.micro instances running Apache HTTP server
   - Displays hostname and availability zone information
   - Distributed across multiple AZs for high availability
   - Elastic IPs for consistent addressing

3. **EC2 Deployment API**
   - Professional Lambda API using AWS Powertools
   - Automated instance provisioning ("pave" requests)
   - Request validation and quota management
   - Comprehensive error handling

4. **This Basic Lambda**
   - Simple "Hello World" implementation
   - Docker containerization via ECR
   - GitHub Actions CI/CD pipeline
   - Learning/development purposes

### Network Security Architecture

**Current Security Groups (from Compute workspace):**
- **ALB Security Group**: Allows HTTP/HTTPS from internet (0.0.0.0/0)
- **EC2 Security Group**: Allows HTTP/HTTPS from ALB only
- **SSH Security Group**: Allows SSH from anywhere (0.0.0.0/0) ⚠️ **SECURITY CONCERN**
- **Package Security Group**: Allows HTTPS to AWS package repositories

## Security Analysis & Recommendations

### 🚨 Current Security Issues

1. **SSH Access Wide Open**
   ```hcl
   # In compute/main.tf - SECURITY RISK
   ingress {
     from_port = 22
     to_port = 22
     protocol = "tcp"
     cidr_blocks = ["0.0.0.0/0"]  # ← ALLOWS SSH FROM ANYWHERE
   }
   ```

2. **Password Authentication Enabled**
   ```bash
   # In compute/user_data/userdata.ssh
   sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
   ```

3. **No VPN or Bastion Host**
   - Web servers have direct internet SSH access
   - No controlled access mechanism for your brothers

### 🔒 Family Access Solutions (For Web Platform Management)

Since this is a web application platform, your brothers would need:

#### Option 1: SSH Bastion Host (Recommended)
```hcl
# Add to compute workspace
resource "aws_instance" "bastion" {
  ami           = "ami-005f9685cb30f234b"
  instance_type = "t3.micro"
  subnet_id     = data.terraform_remote_state.vpc.outputs.subnet_id_list[0]
  
  security_groups = [aws_security_group.bastion_sg.id]
  key_name        = "cloud_gaming"
  
  tags = {
    Name = "Bastion-Host"
  }
}

resource "aws_security_group" "bastion_sg" {
  name_prefix = "bastion-"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  
  # Allow SSH from specific IP ranges (your family)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [
      "YOUR_HOME_IP/32",      # Your IP
      "BROTHER_1_IP/32",      # Brother 1's IP
      "BROTHER_2_IP/32"       # Brother 2's IP
    ]
  }
  
  # Allow outbound SSH to private instances
  egress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.my_tf_ec2_sg.id]
  }
}
```

#### Option 2: AWS Systems Manager Session Manager
```hcl
# Add IAM role to EC2 instances for SSM
resource "aws_iam_role" "ec2_ssm_role" {
  name = "ec2-ssm-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_managed_instance_core" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-ssm-profile"
  role = aws_iam_role.ec2_ssm_role.name
}

# Update EC2 instances to use SSM
resource "aws_instance" "my_tf_ec2" {
  # ... existing configuration ...
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
}
```

#### Option 3: VPN Access
```hcl
# Add Client VPN endpoint to VPC workspace
resource "aws_ec2_client_vpn_endpoint" "family_vpn" {
  description            = "Family VPN for server access"
  server_certificate_arn = aws_acm_certificate.vpn_server.arn
  client_cidr_block      = "172.16.0.0/16"
  
  authentication_options {
    type                       = "certificate-authentication"
    root_certificate_chain_arn = aws_acm_certificate.vpn_client.arn
  }
  
  connection_log_options {
    enabled = false
  }
}
```

### Web Application Access

Your brothers can access the deployed web applications via:
- **ALB DNS Name**: `http://[alb-dns-name]` (from compute workspace output)
- **Direct Instance Access**: Via Elastic IPs (after secure SSH setup)
- **API Access**: To provision new instances via the EC2-Deployer API

## Security Improvements to Implement

### 1. Update Compute Workspace Security Groups

```hcl
# Remove this dangerous rule from compute/main.tf
# ingress {
#   description = "Allow SSH into instance"
#   from_port = 22
#   to_port = 22
#   protocol = "tcp"
#   cidr_blocks = ["0.0.0.0/0"]  # ← REMOVE THIS
# }

# Replace with bastion host access or specific IPs
ingress {
  description     = "Allow SSH from bastion"
  from_port       = 22
  to_port         = 22
  protocol        = "tcp"
  security_groups = [aws_security_group.bastion_sg.id]
}
```

### 2. Disable Password Authentication

```bash
# Update compute/user_data/userdata.ssh
# Remove this line:
# sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Add proper SSH hardening:
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
echo "AllowUsers ec2-user" >> /etc/ssh/sshd_config
```

### 3. Enable HTTPS with Certificate Manager

```hcl
# Add to compute workspace
resource "aws_acm_certificate" "web_cert" {
  domain_name       = "yourdomain.com"
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
}

# Update ALB listener to use HTTPS
resource "aws_alb_listener" "https_listener" {
  load_balancer_arn = aws_alb.ec2_deployer_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.web_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.ec2_target_group.arn
  }
}
```

## Cost Estimates

### Monthly Costs (Web Platform)
- **ALB**: ~$16/month
- **EC2 instances (2x t3.micro)**: ~$15/month  
- **Elastic IPs (2)**: ~$7/month
- **Lambda API calls**: ~$1-5/month
- **Route 53 hosted zone**: ~$0.50/month
- **Data transfer**: ~$5-15/month

**Total estimated**: $45-60/month for the web application platform

## Getting Started

### Prerequisites
- AWS CLI configured
- Terraform installed
- SSH key pair "cloud_gaming" created in AWS

### Deployment Order
1. **Deploy VPC**: Creates network foundation
2. **Deploy Zone Infrastructure**: Sets up DNS
3. **Deploy Compute**: Creates web servers and ALB
4. **Deploy APIs**: Both basic (this repo) and advanced APIs

### Accessing Web Applications
- Navigate to ALB DNS name for web applications
- Use secure SSH access (after implementing security fixes)
- Use EC2 Deployer API for automated provisioning

## Current Status

- **VPC & Compute**: Production-ready infrastructure ✅
- **EC2-Deployer API**: Advanced automation capabilities ✅
- **This Lambda**: Basic development/learning implementation ✅
- **Security**: Needs hardening (SSH access controls) ⚠️
- **HTTPS**: Ready to implement with ACM certificates ⚠️

---

*Last Updated: September 2024*  
*Corrected Architecture Understanding: September 2024*