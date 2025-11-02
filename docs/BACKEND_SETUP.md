# Backend Repository Setup - GitHub Actions CI/CD

This document contains everything you need to set up automated deployments for your FastAPI backend repository using GitHub Actions.

## Prerequisites

Before proceeding, ensure you have completed the infrastructure setup in this repository:

1. ✅ Ran `tofu apply` successfully
2. ✅ Populated secrets in Secret Manager (database-url, api-keys)
3. ✅ Created and downloaded service account JSON key
4. ✅ Have the OpenTofu outputs available (`tofu output`)

## Prompt for Claude (Backend Repo)

Copy the section below and paste it into Claude in your **backend repository**:

---

## 🤖 Setup GitHub Actions for Cloud Run Deployment

I need to set up GitHub Actions to automatically deploy my FastAPI backend to Google Cloud Run when I push a git tag.

### Context

**Infrastructure Details:**
- **GCP Project ID**: `[YOUR_PROJECT_ID]`
- **Region**: `us-central1`
- **Cloud Run Service**: `backend-api`
- **Artifact Registry**: `[YOUR_ARTIFACT_REGISTRY_LOCATION from tofu output]`
- **Service Account**: `[YOUR_GITHUB_ACTIONS_SA_EMAIL from tofu output]`

**Deployment Trigger:**
- Only deploy when I push a git tag (e.g., `v1.0.0`, `v1.0.1`)
- Regular commits to `main` should NOT trigger deployment

**My Backend:**
- FastAPI application with existing Dockerfile
- Dockerfile builds successfully
- App runs on port 8000
- Has `/health` endpoint for health checks

### Tasks

1. **Create `.github/workflows/deploy.yml`** with the following requirements:
   - Trigger only on git tags matching `v*.*.*` pattern
   - Build Docker image from my existing Dockerfile
   - Tag image with the git tag version
   - Authenticate to GCP using service account JSON (from GitHub secret)
   - Push image to Artifact Registry
   - Deploy to Cloud Run service
   - Use the service account for deployment

2. **Document GitHub Secrets** I need to add:
   - List each secret name
   - Explain what value goes in each
   - Explain how to add them to GitHub (Settings → Secrets)

3. **Provide instructions** for:
   - How to create and push a git tag for deployment
   - How to view deployment status in GitHub Actions
   - How to roll back to a previous version if needed

4. **Include a test deployment checklist** after setup

### Additional Requirements

- Use official Google GitHub Actions where possible
- Include error handling and clear job names
- Add comments explaining each major step
- Keep the workflow concise but production-ready

Please create the GitHub Actions workflow and all supporting documentation.

---

## After Running the Prompt

Claude will create:

1. **`.github/workflows/deploy.yml`** - Complete GitHub Actions workflow
2. **GitHub Secrets configuration** - Step-by-step instructions
3. **Git tag workflow** - How to deploy using tags
4. **Testing checklist** - Verify deployment works

## Information Claude Will Need

Have these values ready from your OpenTofu outputs:

```bash
# Run in this infrastructure repo
tofu output
```

You'll need:
- `artifact_registry_location` - Where to push Docker images
- `github_actions_service_account` - Service account email
- `cloud_run_url` - To test after deployment

## Service Account JSON Key

You should have already downloaded this from the Console. If not:

1. Go to [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Find `github-actions-deploy@...`
3. Actions → Manage Keys → Add Key → Create New Key (JSON)
4. Download and save securely

You'll add this entire JSON file contents as a GitHub Secret.

## Git Tags Quick Reference

After GitHub Actions is set up, deploy with:

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# View tags
git tag -l

# Delete a tag (if needed)
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

## Expected GitHub Actions Flow

```
1. Push git tag (v1.0.0)
   ↓
2. GitHub Actions triggers
   ↓
3. Checkout code
   ↓
4. Authenticate to GCP
   ↓
5. Build Docker image
   ↓
6. Push to Artifact Registry
   ↓
7. Deploy to Cloud Run
   ↓
8. Deployment complete! 🎉
```

## Troubleshooting

### Workflow Fails at Authentication

**Check**:
- GitHub Secret `GCP_SA_KEY` contains full JSON (including `{}`)
- Service account key is valid (not deleted)
- Project ID in secret matches your GCP project

### Workflow Fails at Docker Push

**Check**:
- Artifact Registry location is correct
- Service account has `roles/artifactregistry.writer`
- Repository exists: `gcloud artifacts repositories list`

### Workflow Fails at Deployment

**Check**:
- Service account has `roles/run.admin`
- Cloud Run service exists: `gcloud run services list`
- Image was pushed successfully (check previous step)

### Deployment Succeeds but Service Fails

**Check Cloud Run logs**:
```bash
gcloud run services logs read backend-api --limit=50
```

Common issues:
- Secrets not populated in Secret Manager
- FastAPI not listening on port 8000
- Health check endpoint `/health` not responding
- Missing environment variables

## Rolling Back a Deployment

If a deployment breaks production:

```bash
# List recent revisions
gcloud run revisions list --service=backend-api --region=us-central1

# Roll back to previous revision
gcloud run services update-traffic backend-api \
  --to-revisions=backend-api-previous-revision=100 \
  --region=us-central1
```

Or redeploy a previous tag:
```bash
# Find the tag you want to redeploy
git tag -l

# Re-push the tag (may need to delete first)
git push origin v1.0.0
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Auth GitHub Action](https://github.com/google-github-actions/auth)
- [Deploy Cloud Run GitHub Action](https://github.com/google-github-actions/deploy-cloudrun)
- [Cloud Run CI/CD Best Practices](https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build)
