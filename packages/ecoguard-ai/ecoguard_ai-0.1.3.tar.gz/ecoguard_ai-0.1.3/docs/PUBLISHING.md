# EcoGuard AI Publishing Guide

## Automated Publishing Setup

EcoGuard AI uses an automated CI/CD pipeline for publishing to PyPI with trusted publishing for enhanced security.

## Publishing Workflows

### 1. Automatic Publishing (Recommended)

**Test PyPI (Development):**
- Triggered on every push to `main` branch
- Publishes to Test PyPI automatically
- Uses trusted publishing (no API tokens needed)

**Production PyPI:**
- Triggered when version tags are pushed (e.g., `v0.1.4`)
- Publishes to production PyPI
- Uses trusted publishing

### 2. Manual Release Workflow

Use the manual release workflow for controlled releases:

```bash
# Go to GitHub Actions → Release workflow → Run workflow
# Enter version number (e.g., 0.1.4)
# Optionally mark as pre-release
```

This workflow will:
1. Update version in `pyproject.toml` and CLI
2. Run full test suite
3. Build and verify package
4. Create and push git tag
5. Create GitHub release with auto-generated notes
6. Publish to PyPI

## Setup Instructions

### 1. PyPI Trusted Publisher Configuration

**For Test PyPI:**
1. Go to https://test.pypi.org/manage/account/publishing/
2. Add a new trusted publisher with:
   - PyPI Project Name: `ecoguard-ai`
   - Owner: `your-github-username`
   - Repository: `ecoguard`
   - Workflow: `ci.yml`
   - Environment: `release`

**For Production PyPI:**
1. Go to https://pypi.org/manage/account/publishing/
2. Add a new trusted publisher with:
   - PyPI Project Name: `ecoguard-ai`
   - Owner: `your-github-username`
   - Repository: `ecoguard`
   - Workflow: `ci.yml`
   - Environment: `release`

### 2. GitHub Environment Setup

Create a GitHub environment named `release`:

1. Go to Repository Settings → Environments
2. Create new environment: `release`
3. Add protection rules:
   - Required reviewers (optional)
   - Restrict to specific branches: `main`
   - Wait timer: 0 minutes

### 3. Version Management

Current version: `0.1.3`

**Version Bump Process:**
1. Use the manual release workflow (recommended)
2. Or manually update version in:
   - `pyproject.toml`
   - `src/ecoguard_ai/cli/__init__.py`

## Testing the Pipeline

### Test PyPI Deployment
```bash
# Push to main branch to trigger Test PyPI deployment
git push origin main

# Check Test PyPI: https://test.pypi.org/project/ecoguard-ai/
```

### Production PyPI Deployment
```bash
# Create and push a version tag
git tag v0.1.4
git push origin v0.1.4

# Or use the manual release workflow (preferred)
```

### Testing Installation from Test PyPI
```bash
# Install from Test PyPI
pip install -i https://test.pypi.org/simple/ ecoguard-ai

# Test the installation
ecoguard --version
ecoguard --help
```

## Security Features

### Trusted Publishing Benefits
- No API tokens stored in GitHub
- Enhanced security through OIDC
- Automatic token generation per deployment

### Environment Protection
- `release` environment with protection rules
- Prevents unauthorized deployments
- Audit trail for all releases

## Monitoring and Troubleshooting

### Check Publishing Status
1. GitHub Actions → CI/CD Pipeline → Publish job
2. PyPI project page for upload confirmation
3. GitHub Releases for release notes

### Common Issues

**Publishing Fails:**
- Verify trusted publisher configuration
- Check environment permissions
- Ensure version number is incremented

**Version Conflicts:**
- Ensure version in `pyproject.toml` is updated
- Check for existing versions on PyPI
- Use `skip-existing: true` for safe retries

## Best Practices

1. **Always test on Test PyPI first**
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Create meaningful release notes**
4. **Test installation after publishing**
5. **Monitor security advisories**

## Next Steps

1. Configure PyPI trusted publishers (manual step required)
2. Create GitHub `release` environment
3. Test the publishing pipeline
4. Consider adding version management scripts
5. Set up automated security scanning

## Support

For issues with the publishing pipeline:
1. Check GitHub Actions logs
2. Verify PyPI trusted publisher configuration
3. Review environment settings
4. Contact the EcoGuard AI team
