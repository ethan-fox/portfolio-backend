# Deployment Guide

This page covers deploying the backend to GCP Cloud Run using CI with Github Actions.

## Deployment Workflow

### How It Works

Deployments are triggered **only when you push a git tag** matching [semantic versioning](https://semver.org/) (e.g., `1.0.0`).

Regular commits to any branch will **NOT** trigger deployments, including `master`.

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

### Deployment Steps (Automated)

When you push a tag, GitHub Actions will:

1. Checkout your code
2. Extract version from tag
3. Authenticate to Google Cloud
4. Build Docker image
5. Tag image with version (e.g., `portfolio-api:1.0.0`)
6. Push to Artifact Registry
7. Deploy to Cloud Run
8. Display deployment URL

## Rollback

If you need to quickly roll back:

### Rollback from Command Line 

```bash
# Option 1: Re-push an existing tag
git push origin 1.0.0 --force

# Option 2: Create new tag from old commit
git checkout <old-commit-sha>
git tag 1.0.2
git push origin 1.0.2
```

### Rollback via Cloud Console

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on `portfolio-api` service
3. Go to **Revisions** tab
4. Find the previous working revision
5. Click **⋮** → **Manage traffic**
6. Set 100% traffic to the previous revision
7. Click **Save**

## Post-Deployment

### Verify

```bash
# Check health endpoint
curl https://portfolio-api-3rri4wydga-uc.a.run.app/health

# Should return:
# {"status":"healthy"}
```

### View Live Service

The API is live at:
```
https://portfolio-api-3rri4wydga-uc.a.run.app
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
