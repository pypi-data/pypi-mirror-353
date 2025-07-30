# PyPI Trusted Publisher Setup Guide

This guide will walk you through setting up trusted publishing for EcoGuard AI on both Test PyPI and production PyPI.

## Prerequisites

1. ✅ GitHub repository with CI/CD workflow configured
2. ✅ PyPI account (create at https://pypi.org/account/register/)
3. ✅ Test PyPI account (create at https://test.pypi.org/account/register/)

## Step 1: Create PyPI Project (First Time Only)

If this is your first time publishing, you'll need to create the project on PyPI first.

### Option A: Manual Upload (First Release)

1. Build the package locally:
   ```bash
   python -m build
   ```

2. Upload to Test PyPI first:
   ```bash
   pip install twine
   python -m twine upload --repository testpypi dist/*
   ```

3. Then upload to production PyPI:
   ```bash
   python -m twine upload dist/*
   ```

### Option B: Use GitHub Actions (Recommended)

1. Create an API token for the initial upload:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope for the entire account
   - Add it as a GitHub secret named `PYPI_API_TOKEN`

2. Temporarily modify the publish job in `.github/workflows/ci.yml` to use the token:
   ```yaml
   - name: Publish to PyPI (temporary)
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

3. Push to main or create a tag to trigger the upload

4. After successful upload, remove the API token method and continue with trusted publishing

## Step 2: Configure Trusted Publishing

### For Test PyPI

1. Go to https://test.pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name**: `ecoguard-ai`
   - **Owner**: `your-github-username` (replace with your actual GitHub username)
   - **Repository**: `ecoguard`
   - **Workflow**: `ci.yml`
   - **Environment**: `release`

### For Production PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the same details:
   - **PyPI Project Name**: `ecoguard-ai`
   - **Owner**: `your-github-username` (replace with your actual GitHub username)
   - **Repository**: `ecoguard`
   - **Workflow**: `ci.yml`
   - **Environment**: `release`

## Step 3: Create GitHub Environment

1. Go to your repository on GitHub
2. Click **Settings** → **Environments**
3. Click **New environment**
4. Name: `release`
5. Configure protection rules:
   - ✅ **Required reviewers**: (optional, add team members)
   - ✅ **Restrict to selected branches**: `main`
   - ⚠️ **Wait timer**: 0 minutes (or set a delay if you want)

## Step 4: Test the Setup

### Test PyPI Publishing

1. Make a small change and push to main:
   ```bash
   git add .
   git commit -m "test: trigger publishing workflow"
   git push origin main
   ```

2. Check GitHub Actions to see if the publish job runs
3. Verify the package appears on Test PyPI: https://test.pypi.org/project/ecoguard-ai/

### Production PyPI Publishing

1. Create and push a version tag:
   ```bash
   git tag v0.1.4
   git push origin v0.1.4
   ```

2. Check GitHub Actions for the publish job
3. Verify the package appears on PyPI: https://pypi.org/project/ecoguard-ai/

## Step 5: Verification

### Install from Test PyPI
```bash
pip install -i https://test.pypi.org/simple/ ecoguard-ai
ecoguard --version
```

### Install from Production PyPI
```bash
pip install ecoguard-ai
ecoguard --version
```

## Common Issues and Solutions

### Issue: "Project does not exist"
**Solution**: You need to create the project first with a manual upload (Step 1)

### Issue: "Invalid token" or "Authentication failed"
**Solution**:
- Ensure trusted publisher configuration is correct
- Verify the environment name matches exactly
- Check that the workflow name is correct (`ci.yml`)

### Issue: "Environment not found"
**Solution**: Create the `release` environment in GitHub repository settings

### Issue: "Permission denied"
**Solution**:
- Ensure the workflow has `id-token: write` permission
- Verify the environment is properly configured
- Check that the branch restrictions are correct

## Security Best Practices

1. **Never store API tokens in GitHub secrets** (after trusted publishing is set up)
2. **Use environment protection** to prevent unauthorized deployments
3. **Review all uploads** before they go to production
4. **Monitor PyPI project** for unexpected uploads
5. **Enable 2FA** on both GitHub and PyPI accounts

## Next Steps

After completing this setup:

1. ✅ Remove any temporary API tokens
2. ✅ Test both Test PyPI and production PyPI publishing
3. ✅ Update team members on the new publishing process
4. ✅ Document any project-specific publishing requirements
5. ✅ Set up monitoring/notifications for new releases

## Support

If you encounter issues:

1. Check the GitHub Actions logs for detailed error messages
2. Verify all configuration matches exactly
3. Test with a simple package first if needed
4. Consult the [PyPI Trusted Publishing documentation](https://docs.pypi.org/trusted-publishers/)
