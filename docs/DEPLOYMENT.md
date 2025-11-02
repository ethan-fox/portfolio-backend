# Deployment Guide

This guide covers deploying your FastAPI backend to Google Cloud Run using GitHub Actions.

## Prerequisites

Before deploying, ensure you have:
- ✅ Completed infrastructure setup with OpenTofu
- ✅ Service account JSON key downloaded
- ✅ GitHub repository created

## Setup GitHub Secrets

You need to add two secrets to your GitHub repository:

### 1. Navigate to GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### 2. Add Required Secrets

#### Secret 1: `GCP_SA_KEY`
- **Name**: `GCP_SA_KEY`
- **Value**: Paste the **entire contents** of your service account JSON key file
  - This is the file you downloaded from GCP Console
  - Should start with `{` and end with `}`
  - Include everything, don't modify it

#### Secret 2: `GCP_PROJECT_ID`
- **Name**: `GCP_PROJECT_ID`
- **Value**: `portfolio-477017`

## Deployment Workflow

### How It Works

Deployments are triggered **only when you push a git tag** matching semantic versioning (e.g., `1.0.0`).

Regular commits to any branch will **NOT** trigger deployments.

### Deploy a New Version

```bash
# 1. Ensure all changes are committed and pushed
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Create a version tag (without 'v' prefix)
git tag 1.0.0

# 3. Push the tag to trigger deployment
git push origin 1.0.0
```

### Semantic Versioning Guide

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR** (`2.0.0`): Breaking changes
- **MINOR** (`1.1.0`): New features, backward compatible
- **PATCH** (`1.0.1`): Bug fixes, backward compatible

Examples:
```bash
git tag 1.0.0    # Initial release
git tag 1.0.1    # Bug fix
git tag 1.1.0    # New feature
git tag 2.0.0    # Breaking change
```

### View Deployment Status

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You'll see the "Deploy to Cloud Run" workflow running
4. Click on the workflow run to see detailed logs
5. Each step shows its progress and any errors

### Deployment Steps (Automated)

When you push a tag, GitHub Actions will:

1. ✅ Checkout your code
2. ✅ Extract version from tag
3. ✅ Authenticate to Google Cloud
4. ✅ Build Docker image
5. ✅ Tag image with version (e.g., `portfolio-api:1.0.0`)
6. ✅ Push to Artifact Registry
7. ✅ Deploy to Cloud Run
8. ✅ Display deployment URL

## Post-Deployment

### Verify Deployment

```bash
# Check health endpoint
curl https://portfolio-api-3rri4wydga-uc.a.run.app/health

# Should return:
# {"status":"healthy"}
```

### View Live Service

Your API is live at:
```
https://portfolio-api-3rri4wydga-uc.a.run.app
```

### View Logs

```bash
# View recent logs
gcloud run services logs read portfolio-api --limit=50 --region=us-central1

# Stream live logs
gcloud run services logs tail portfolio-api --region=us-central1
```

## Managing Tags

### List All Tags

```bash
git tag -l
```

### Delete a Tag (Locally and Remote)

```bash
# Delete locally
git tag -d 1.0.0

# Delete from GitHub
git push origin :refs/tags/1.0.0
```

### Deploy Previous Version (Rollback)

```bash
# Option 1: Re-push an existing tag
git push origin 1.0.0 --force

# Option 2: Create new tag from old commit
git checkout <old-commit-sha>
git tag 1.0.2
git push origin 1.0.2
```

## Rollback via Cloud Run Console

If you need to quickly roll back without redeploying:

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on `portfolio-api` service
3. Go to **Revisions** tab
4. Find the previous working revision
5. Click **⋮** → **Manage traffic**
6. Set 100% traffic to the previous revision
7. Click **Save**

Or via CLI:
```bash
# List revisions
gcloud run revisions list --service=portfolio-api --region=us-central1

# Route 100% traffic to a specific revision
gcloud run services update-traffic portfolio-api \
  --to-revisions=portfolio-api-00001-abc=100 \
  --region=us-central1
```

## Troubleshooting

### Deployment Fails at Authentication

**Error**: `Authentication failed` or `Invalid credentials`

**Solution**:
- Verify `GCP_SA_KEY` secret contains the full JSON (including `{}`)
- Ensure service account key hasn't been deleted in GCP
- Check project ID matches in the JSON key

### Deployment Fails at Docker Push

**Error**: `denied: Permission denied` or `repository does not exist`

**Solution**:
- Verify Artifact Registry repository exists: `gcloud artifacts repositories list`
- Ensure service account has `roles/artifactregistry.writer`
- Check registry path is correct: `us-central1-docker.pkg.dev/portfolio-477017/portfolio-images`

### Deployment Succeeds but Service Returns 500

**Check Cloud Run logs**:
```bash
gcloud run services logs read portfolio-api --limit=50 --region=us-central1
```

**Common issues**:
- Database connection failed (check `DATABASE_URL` secret in Secret Manager)
- App not listening on port 7050
- Missing environment variables
- Python dependencies not installed

### Health Check Fails

**Error**: `Service not ready` or `Health check failed`

**Solution**:
- Verify `/health` endpoint is accessible locally
- Check app is binding to `0.0.0.0` not `localhost`
- Ensure port 7050 is correct in Dockerfile and workflow

## Test Deployment Checklist

After your first deployment:

- [ ] GitHub Actions workflow completed successfully
- [ ] Cloud Run service shows "healthy" status
- [ ] Health endpoint responds: `curl https://portfolio-api-3rri4wydga-uc.a.run.app/health`
- [ ] API endpoints are accessible
- [ ] Database connection works (test subscriber creation)
- [ ] Logs show no errors: `gcloud run services logs read portfolio-api`
- [ ] Service scales to zero when idle (check after 15 minutes)

## Deployment Best Practices

1. **Test locally first**: Always test your Docker build locally before pushing a tag
2. **Use semantic versioning**: Follow MAJOR.MINOR.PATCH convention
3. **Tag stable commits**: Only tag commits that have been tested
4. **Monitor deployments**: Watch the GitHub Actions workflow complete
5. **Keep tags immutable**: Don't reuse version numbers
6. **Document releases**: Use GitHub Releases to document changes per version

## Cost Management

Cloud Run pricing (for hobby projects):
- **Free tier**: 2 million requests/month
- **Idle cost**: $0 (scales to zero)
- **Per request**: ~$0.0000004 per request after free tier
- **Memory**: Minimal cost for FastAPI

**Tips to minimize costs**:
- Service scales to zero when idle (free)
- Use minimum instance count of 0
- Delete old container images periodically
- Monitor usage in GCP Console

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Semantic Versioning](https://semver.org/)
