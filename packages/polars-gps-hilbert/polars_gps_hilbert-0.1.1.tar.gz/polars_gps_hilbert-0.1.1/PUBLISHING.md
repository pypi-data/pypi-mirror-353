# Publishing to PyPI Guide

This guide walks you through publishing `polars-gps-hilbert` to PyPI using GitHub Actions.

## 🔑 Step 1: Get PyPI API Token

1. **Create PyPI Account**: Go to [pypi.org](https://pypi.org) and create an account
2. **Generate API Token**:
   - Go to [Account Settings](https://pypi.org/manage/account/)
   - Scroll to "API tokens" section
   - Click "Add API token"
   - Name: `polars-gps-hilbert-github-actions`
   - Scope: "Entire account" (or "Project" after first publish)
   - **Copy the token** (starts with `pypi-`)

## 🔒 Step 2: Add Token to GitHub Secrets

1. **Go to your GitHub repo**: https://github.com/nullbutt/polars-gps-hilbert
2. **Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**
4. **Name**: `PYPI_API_TOKEN`
5. **Value**: Paste your PyPI token (including `pypi-` prefix)
6. **Click "Add secret"**

## 🚀 Step 3: Publish via GitHub Release

### Option A: Create Release via GitHub UI
1. Go to your repo → **Releases** → **Create a new release**
2. **Tag version**: `v0.1.0` (must start with 'v')
3. **Release title**: `v0.1.0 - Initial Release`
4. **Description**:
   ```
   ## 🎉 Initial Release of polars-gps-hilbert
   
   High-performance Polars plugin for GPS trajectory indexing using 3D Hilbert curves.
   
   ### Features
   - 3D Hilbert curve indexing for lat/lon/timestamp
   - 20M+ points/second throughput
   - Lazy evaluation for out-of-core processing
   - Excellent spatial locality for GPS queries
   
   ### Installation
   ```bash
   pip install polars-gps-hilbert
   ```
   ```
5. **Click "Publish release"**

### Option B: Create Release via Command Line
```bash
# Install GitHub CLI if not already installed
# brew install gh (macOS) or visit: https://cli.github.com/

# Create and push tag
git tag v0.1.0
git push origin v0.1.0

# Create release
gh release create v0.1.0 --title "v0.1.0 - Initial Release" --notes "Initial release of polars-gps-hilbert plugin"
```

## 🤖 Step 4: Watch GitHub Actions

1. **Go to**: Repository → **Actions** tab
2. **Watch the "Release" workflow**:
   - ✅ Wheels built for Linux/Windows/macOS
   - ✅ Published to PyPI automatically
   - ✅ Takes ~5-10 minutes total

## ✅ Step 5: Verify Publication

After the workflow completes (~10-15 minutes):

1. **Check PyPI**: https://pypi.org/project/polars-gps-hilbert/
2. **Test installation**:
   ```bash
   pip install polars-gps-hilbert
   python -c "import polars_gps_hilbert; print('Success!')"
   ```

## 🔄 Future Updates

For future releases:
1. **Update version** in `Cargo.toml` and `pyproject.toml`
2. **Commit changes**: `git commit -am "Bump version to 0.2.0"`
3. **Create new release**: `v0.2.0`
4. **GitHub Actions handles the rest!**

## 📋 Troubleshooting

### Common Issues:
- **"Invalid token"**: Make sure PyPI token is correct and has proper scope
- **"Package already exists"**: Bump version number in `Cargo.toml`
- **Build failures**: Check GitHub Actions logs for specific errors

### Manual Publishing (Backup):
If GitHub Actions fails, you can publish manually:
```bash
# Install maturin
pip install maturin

# Build and publish
maturin publish --username __token__ --password YOUR_PYPI_TOKEN
```

## 🎯 Next Steps

Once published:
- ✅ Package will be available: `pip install polars-gps-hilbert`
- ✅ Works in Palantir Foundry and any Python environment
- ✅ Source code stays private in your GitHub repo
- ✅ Automatic updates via GitHub releases