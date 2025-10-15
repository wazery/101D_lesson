# Simple EC2 Deployment

This workflow deploys the Flask S3 Gallery app directly to EC2 servers using SSH.

## Required GitHub Secrets

**Infrastructure Secrets:**

### Staging Environment
- `STAGING_HOST` - Staging EC2 server IP address
- `STAGING_USER` - SSH username (usually `ubuntu` or `ec2-user`)
- `STAGING_SSH_KEY` - Private SSH key for staging server

### Production Environment
- `PRODUCTION_HOST` - Production EC2 server IP address  
- `PRODUCTION_USER` - SSH username (usually `ubuntu` or `ec2-user`)
- `PRODUCTION_SSH_KEY` - Private SSH key for production server

**Application Secrets:**
- `SECRET_KEY` - Flask secret key for sessions (generate a random string)
- `AWS_ACCESS_KEY_ID` - Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret access key
- `AWS_REGION` - AWS region (e.g., `us-east-1`, `eu-north-1`)
- `S3_BUCKET_NAME` - Your S3 bucket name

**Total: 11 secrets needed**

## How It Works

1. **Push to `staging` branch** → Deploys to staging server
2. **Push to `main` branch** → Deploys to production server
3. **Manual trigger** → Choose which environment to deploy

## Server Setup

Each EC2 server needs:

```bash
# Install Docker
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker

# IMPORTANT: Add user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker $USER

# Logout and login again, OR run:
newgrp docker

# Test Docker works without sudo
docker --version
docker ps
```

**The workflow creates `~/flask-app` directory and `.env` file automatically from GitHub secrets!**

⚠️ **Important**: Never commit `.env` files to git - they contain sensitive credentials!

## How to Set Up Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name listed above

### Generating SECRET_KEY

Generate a secure Flask secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Getting AWS Credentials

1. Go to AWS Console → IAM → Users
2. Create new user or use existing
3. Attach policy: `AmazonS3FullAccess`
4. Create Access Key → Application running outside AWS
5. Copy Access Key ID and Secret Access Key

### Security Best Practices

✅ **DO:**
- Use GitHub Secrets for all sensitive data
- Generate strong secret keys
- Use least-privilege AWS policies
- Rotate credentials regularly

❌ **DON'T:**
- Commit `.env` files to git
- Share AWS credentials in chat/email
- Use the same secret key for staging and production

## SSH Key Setup

1. Generate SSH key pair:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/deploy_key
   ```

2. Copy public key to server:
   ```bash
   ssh-copy-id -i ~/.ssh/deploy_key.pub user@server-ip
   ```

3. Add private key to GitHub secrets:
   ```bash
   cat ~/.ssh/deploy_key
   ```

## What the Workflow Does

1. ✅ Checks out code from GitHub
2. ✅ Connects to server via SSH  
3. ✅ Stops existing Docker container
4. ✅ **Copies files directly** from GitHub Actions to server
5. ✅ **Creates .env file** from GitHub secrets (secure!)
6. ✅ Builds new Docker image on server
7. ✅ Runs new container with environment variables
8. ✅ Performs health check

**Secure credential handling** - AWS keys never stored in code!