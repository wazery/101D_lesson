# Docker Permission Issues - Quick Fix

## Problem: Permission Denied Errors

If you see these errors:
```
mkdir: cannot create directory '/opt/flask-app': Permission denied
permission denied while trying to connect to the Docker daemon socket
```

## ✅ Quick Fix for EC2

Run these commands on your EC2 instance:

```bash
# Fix Docker permissions (no sudo needed for docker commands)
sudo usermod -aG docker $USER

# Logout and login again, OR run:
newgrp docker

# Test Docker without sudo
docker ps

# The app will now be deployed to ~/flask-app (user home directory)
```

## ✅ Verification

After setup, verify everything works:

```bash
# Check Docker works without sudo
docker --version
docker ps

# Check the app directory exists
ls -la ~/flask-app

# Check if app is running (after deployment)
docker ps
curl http://localhost:8080/health
```

## ⚠️ If Still Having Issues

1. **Reboot the EC2 instance** (this often fixes group membership issues)
2. **Use a different user** - try `ec2-user` instead of `ubuntu` in your GitHub secrets
3. **Check AMI type** - Make sure you're using Ubuntu or Amazon Linux 2

## 📝 Updated Deployment Paths

The workflow now uses:
- **App directory**: `~/flask-app` (user home, not `/opt/`)
- **No sudo required** for any commands
- **User-owned directories** - no permission issues

This is actually **better practice** for workshop environments!