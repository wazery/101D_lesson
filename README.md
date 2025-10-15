# Flask S3 Gallery - Multi-Environment Deployment (101D)

This is a complete Flask S3 Gallery application with CI/CD deployment to multiple environments.

## What's Included

- **Flask S3 Gallery App** - Complete photo gallery with AWS S3 integration
- **Docker Configuration** - Dockerfile for containerization
- **GitHub Actions** - Automated deployment to staging and production
- **Environment Configuration** - Example environment variables

## Files

```
101D_source/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container configuration
├── .env.example           # Environment variables template
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   └── upload.html
├── .github/workflows/     # CI/CD automation
│   └── deploy.yml
├── DEPLOYMENT.md          # Deployment setup guide
└── README.md             # This file
```

## Quick Start

1. **Clone this directory** as your project repository
2. **Set up AWS S3** bucket and credentials
3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```
4. **Run locally**:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

## CI/CD Deployment

This repository includes automated deployment to staging and production servers:

- **Push to `staging` branch** → Deploys to staging server
- **Push to `main` branch** → Deploys to production server

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete setup instructions.

## Workshop Learning Objectives

This example demonstrates:

✅ **Multi-Environment Deployment** - Separate staging and production  
✅ **Docker Containerization** - Consistent deployment environments  
✅ **GitHub Actions CI/CD** - Automated build and deployment  
✅ **SSH-based Deployment** - Direct server deployment  
✅ **Environment Management** - Secure credential handling  
✅ **Health Checks** - Deployment verification  

Perfect for learning real-world CI/CD practices!