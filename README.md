# ECR Lambda Project

## Overview

This repository contains infrastructure and application code for a cloud-based gaming platform built on AWS. The project appears to be in early development stages, designed to provide on-demand gaming instances for users with automated management capabilities.

## Architecture

### Core Components

1. **AWS Lambda Function** (`github_lambda.py`)
   - Basic Lambda handler that returns a "Hello World" response
   - Contains commented-out code for PostgreSQL/TimescaleDB integration
   - Currently deployed via GitHub Actions

2. **Docker Container** (`build/Dockerfile`)
   - Python 3.9 based container
   - Configured for Lambda deployment via ECR (Elastic Container Registry)
   - Includes requirements.txt with requests library

3. **CI/CD Pipeline** (`.github/workflows/main.yml`)
   - Automated deployment to AWS Lambda on master branch pushes
   - Builds and pushes Docker images to Amazon ECR
   - Syncs build artifacts to S3 bucket
   - Deploys Lambda function from source code

### Planned Infrastructure (Based on Documentation)

The documentation reveals a comprehensive cloud gaming platform with the following planned components:

#### Gaming Infrastructure (`ec2_gaming.md`)
- **EC2 Instances**: Windows-based gaming instances with:
  - GPU drivers (NVIDIA Gaming, AMD Windows drivers)
  - Steam and SteamCMD installation
  - DirectX support
  - RDP/SSH access with security groups
  - User profile management (non-admin accounts)

- **Storage Solutions**:
  - S3 buckets for driver storage and game save files
  - EBS volumes for instance storage
  - Automated save game backup to S3

#### Network & Security (`alb-pipeline.md`)
- **Application Load Balancer (ALB)** in public subnets
- **Route 53 DNS** with failover configuration
- Multi-region setup (us-east-1 primary, eu-west-2 secondary)
- Security groups for controlled access

#### Access Management (`tfe-roles.md`)
- **Terraform Enterprise (TFE) roles**:
  - `tfe-module-pave` - SAML federated role
  - `tfe-module-pave-apply` - Limited read/write permissions
- **SSM Parameter Store** organization:
  - `/application/ec2deployer/resource/main/*` - AWS console resources
  - `/application/ec2deployer/resource/terraform/*` - Terraform resources
  - `/application/ec2deployer/user/*` - User-related configuration

## Roadmap

The project follows a phased development approach:

### Version 1
- Create APIs for instance management (launch, start, stop, terminate)
- Infrastructure: ALB + API Lambda

### Version 2  
- APIs for AMI creation, snapshot management, save game S3 sync
- Infrastructure: Database + API Lambda + Workflow Lambda + Step Functions
- EC2 templates with automated driver installation
- Multiple instance type support

### Version 3
- User onboarding/offboarding APIs
- Per-user EC2 instances
- Multi-tenant architecture

## Development Tools

The project uses the following development stack (per `TOOLS.md`):
- **Languages**: Python, Java, JavaScript, TypeScript
- **Build Tools**: Maven
- **Version Control**: Git with GitHub CLI
- **IDE**: IntelliJ with plugins (Material Theme, Python, HCL, GitToolBox)
- **Infrastructure**: Docker, AWS CLI
- **Monitoring**: VPC Flow Logs with custom format

## Current Status

⚠️ **Project appears to be in early development stage (over 2 years old)**

- Basic Lambda function is implemented but mostly placeholder code
- Docker containerization is set up
- CI/CD pipeline is configured
- Extensive planning documentation exists but implementation is minimal
- Database integration code is commented out

## Security Concerns & Recommendations

### 🚨 Critical Security Issues

1. **Exposed AWS Credentials in GitHub Actions**
   - AWS credentials are stored as GitHub secrets but used in environment variables
   - Consider using OIDC/assume role patterns instead of long-lived credentials

2. **SQL Injection Vulnerability**
   - The SQL query in the Lambda function has a syntax error but shows potential for SQL injection
   - Current query: `"SELECT * FROM hypertable WHERE time > WHERE time > NOW() - INTERVAL '2 weeks'"`
   - Recommendation: Use parameterized queries and proper ORM

3. **Docker Security**
   - Dockerfile runs as root user
   - No security scanning or vulnerability checks in CI/CD
   - Base image should be pinned to specific versions

4. **Network Security**
   - Gaming instances with RDP/SSH access need strict IP whitelisting
   - Consider VPN or bastion host architecture instead of direct internet access

### 🔒 Additional Security Recommendations

1. **Infrastructure as Code**
   - Convert documentation to actual Terraform modules
   - Implement proper state management and backend configuration
   - Add security scanning to Terraform code

2. **Access Control**
   - Implement proper IAM policies with least privilege principle
   - Use AWS Systems Manager Session Manager instead of SSH/RDP where possible
   - Enable AWS CloudTrail for audit logging

3. **Data Protection**
   - Encrypt S3 buckets for save game storage
   - Use AWS KMS for encryption key management
   - Implement backup and disaster recovery procedures

4. **Monitoring & Logging**
   - Add AWS X-Ray tracing to Lambda functions
   - Implement CloudWatch monitoring and alerting
   - Set up AWS Config for compliance monitoring

5. **Cost Management**
   - Implement auto-shutdown for inactive gaming instances
   - Use Spot instances where appropriate
   - Set up billing alerts and cost monitoring

## Getting Started

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker installed
- Python 3.9+

### Local Development
```bash
# Install dependencies
pip install -r build/requirements.txt

# Run Lambda function locally (requires additional setup for database)
python github_lambda.py
```

### Deployment
The project automatically deploys on pushes to the master branch via GitHub Actions.

## Future Considerations

1. **Database Selection**: The commented PostgreSQL code suggests TimescaleDB for time-series data
2. **Multi-tenancy**: Architecture needs to support multiple users safely
3. **Cost Optimization**: GPU instances are expensive - implement smart scheduling
4. **Regional Expansion**: Plan for multi-region deployment for global users
5. **Monitoring**: Implement comprehensive monitoring for gaming performance

## Contributing

This appears to be a personal/prototype project. Before contributing:
1. Review the security recommendations above
2. Implement proper testing infrastructure
3. Create development environment setup documentation
4. Establish code review processes

---

*Last Updated: September 2024*  
*Original Project: ~2022 (based on commit history)*