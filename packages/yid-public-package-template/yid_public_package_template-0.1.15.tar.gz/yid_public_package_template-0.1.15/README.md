# Public Python Package Template

## Using This Template for Your Own Package (e.g., "my_package")

To adapt this template for your new package (let's call it "my_package"):

1.  **Copy or Template the Repository:**
    *   Click the "Use this template" button on GitHub to create a new repository from this template.

2.  **Rename the Package Directory:**
    *   Rename the main package directory in src dir

3.  **Update `pyproject.toml`:**
    *   **`[project].name`**: Change from `"public_package_template"` to `"my_package"`.
    *   **`[project].urls`**: Update `Homepage` and `Repository` URLs to point to your new repository.

4.  **Set up bump version:**
    1.  Install and authenticate GitHub CLI:
        ```bash
        # Install GitHub CLI (if not already installed)
        # macOS: brew install gh
        # Linux: See https://cli.github.com/
        
        # Authenticate
        gh auth login
        ```
    2.  Create a Personal Access Token:
        *   Go to: https://github.com/settings/personal-access-tokens/new?type=beta
        *   Set permission "Contents" to Read & Write
        *   Copy the generated token
    3.  Add the token to repository secrets:
        ```bash
        gh secret set BUMPVERSION_TOKEN --body "your_generated_token_here"
        ```
    4.  It is recommended to make the main branch protected as every push/merge/commit to it will trigger a bump version.

5.  **Set up PyPI**
    1.  Create PyPI API token:
        *   Go to: https://pypi.org/manage/account/token/
        *   Click "Add API token", set the scope for your package
        *   Copy the generated token (starts with `pypi-`)
    2.  Add the token to repository secrets:
        ```bash
        gh secret set PYPI_PUBLISH_TOKEN --body "pypi-your_token_here"
        ```

6.  **Verify secrets setup:**
    ```bash
    # List all repository secrets
    gh secret list
    
    # Check authentication status
    gh auth status
    ```

7.  **Once you push anything to main, a new tag will be created, built, and published to PyPI**

## Managing Repository Secrets via CLI

### Additional useful commands:
```bash
# Set multiple secrets from .env file
gh secret set -f .env

# Delete a secret
gh secret delete SECRET_NAME

# Set organization-level secret
gh secret set SECRET_NAME --org your-org

# Open repository settings in browser
gh browse --settings
```

## Installing Your Published Public Package

Then you can just pip install your package.
