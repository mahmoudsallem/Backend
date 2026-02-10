# CI/CD Pipeline Documentation

## Overview
This CI/CD pipeline automatically runs on every push and pull request to ensure code quality, security, and proper Docker configuration.

## Pipeline Jobs

### 1. 🔐 Gitleaks - Secret Scanning
- **Purpose**: Scans the repository for exposed secrets, API keys, passwords, and credentials
- **Tool**: [Gitleaks](https://github.com/gitleaks/gitleaks)
- **When it runs**: First job in the pipeline
- **What it checks**: Git history for leaked secrets

### 2. 🔍 njsscan - Python Code Security Scan
- **Purpose**: Scans JavaScript and Node.js code for security vulnerabilities
- **Tool**: [njsscan](https://github.com/ajinabraham/njsscan)
- **What it checks**:
  - Insecure code patterns
  - Hardcoded secrets in JS files
  - Missing security headers
  - Vulnerable dependencies
  - Common security misconfigurations
- **Outputs**:
  - Console output (displayed in workflow logs)
  - **HTML report** (downloadable artifact)
  - SARIF report (uploaded to GitHub Security tab)
- **Report retention**: 30 days
- **Runs in parallel**: With other security scans
- **Language support**: JavaScript, TypeScript, Node.js

#### Accessing the njsscan HTML Report
1. Go to the **Actions** tab in your GitHub repository
2. Click on the workflow run
3. Scroll down to the **Artifacts** section
4. Download **njsscan-security-report**
5. Extract and open `njsscan-report.html` in your browser


### 3. 🔍 Semgrep - Static Application Security Testing (SAST)
- **Purpose**: Advanced static analysis to find bugs, security vulnerabilities, and code quality issues
- **Tool**: [Semgrep](https://semgrep.dev/)
- **Rulesets used**:
  - `p/security-audit` - Security best practices
  - `p/secrets` - Hardcoded secrets detection
  - `p/owasp-top-ten` - OWASP Top 10 vulnerabilities
  - `p/python` - Python-specific security issues
- **What it checks**:
  - SQL injection vulnerabilities
  - XSS (Cross-Site Scripting)
  - Command injection
  - Path traversal
  - Insecure deserialization
  - Authentication/authorization issues
  - Cryptographic weaknesses
- **Outputs**:
  - Console output (displayed in workflow logs)
  - **HTML report** (downloadable artifact)
  - SARIF report (uploaded to GitHub Security tab)
- **Report retention**: 30 days
- **Runs in parallel**: With other security scans

#### Accessing the Semgrep HTML Report
1. Go to the **Actions** tab in your GitHub repository
2. Click on the workflow run
3. Scroll down to the **Artifacts** section
4. Download **semgrep-security-report**
5. Extract and open `semgrep-report.html` in your browser

### 4. 🐳 Dockerfile Validation and Build
- **Purpose**: Ensures Dockerfile exists and builds successfully
- **Steps**:
  - ✅ Checks if `Dockerfile` exists in the repository
  - ✅ Sets up Docker Buildx for advanced build features
  - ✅ Builds the Docker image
  - ✅ Tests the built image
- **Depends on**: Gitleaks job must pass

### 5. 🔏 Cosign Image Signing
- **Purpose**: Cryptographically sign Docker images for supply chain security
- **Tool**: [Cosign](https://github.com/sigstore/cosign) (Sigstore project)
- **Signing method**: Keyless signing using OIDC (OpenID Connect)
- **What it provides**:
  - Image authenticity verification
  - Integrity protection
  - Supply chain security (SLSA framework)
  - Signature attestation for local images
- **Depends on**: Dockerfile check must pass

### 6. 📝 Code Quality Check
- **Purpose**: Lints Python code for syntax errors and code quality
- **Tool**: flake8
- **What it checks**:
  - Python syntax errors
  - Undefined names
  - Code complexity
  - Line length (max 127 characters)
- **Depends on**: Dockerfile check must pass

### 7. 🛡️ Security Scan (Trivy)
- **Purpose**: Scans Docker image for vulnerabilities
- **Tool**: [Trivy](https://github.com/aquasecurity/trivy)
- **What it checks**: Known vulnerabilities in dependencies and base images
- **Severity levels**: CRITICAL and HIGH
- **Outputs**: 
  - Console table view (displayed in workflow logs)
  - **HTML report** (downloadable artifact)
- **Report retention**: 30 days
- **Depends on**: Dockerfile check must pass

#### Accessing the HTML Report
1. Go to the **Actions** tab in your GitHub repository
2. Click on the workflow run
3. Scroll down to the **Artifacts** section
4. Download **trivy-security-report**
5. Extract and open `trivy-report.html` in your browser

### 8. 📊 Pipeline Summary
- **Purpose**: Provides a summary of all pipeline jobs
- **When it runs**: Always runs at the end, regardless of job failures
- **What it shows**: Status of all completed jobs

## Triggering the Pipeline

The pipeline runs automatically on:
- Push to `main`, `master`, or `develop` branches
- Pull requests targeting `main`, `master`, or `develop` branches

## Viewing Pipeline Results

1. Go to your GitHub repository
2. Click on the **Actions** tab
3. Select the latest workflow run
4. View the status of each job

## Pipeline Flow

```
┌─────────────┐
│  Gitleaks   │ (Secret Scanning)
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Dockerfile Check    │ (Validation & Build)
└──────┬──────────────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Code Quality │ │Security Scan│ │   Summary   │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Customization

### Making Security Scan Fail on Vulnerabilities
Change `exit-code: '0'` to `exit-code: '1'` in the security-scan job:
```yaml
exit-code: '1'  # Fail the build on vulnerabilities
```

### Adjusting Branches
Modify the `on` section to change which branches trigger the pipeline:
```yaml
on:
  push:
    branches: [ your-branch-name ]
```

### Disabling Optional Jobs
Comment out or remove jobs you don't need:
- `code-quality` - Python linting
- `security-scan` - Vulnerability scanning
- `summary` - Pipeline summary

## Troubleshooting

### Gitleaks Fails
- Review the Gitleaks output for detected secrets
- Remove or encrypt any exposed credentials
- Use `.gitleaksignore` to ignore false positives

### Dockerfile Check Fails
- Ensure `Dockerfile` exists in the repository root
- Check Dockerfile syntax and build errors

### Docker Build Fails
- Review build logs for errors
- Test locally: `docker build -t test .`
- Check if all required files are present

### Code Quality Fails
- Fix Python syntax errors
- Run locally: `flake8 .`

## Local Testing

Test the pipeline components locally:

```bash
# 1. Test Gitleaks
docker run -v $(pwd):/path zricethezav/gitleaks:latest detect --source="/path" -v

# 2. Test Dockerfile
docker build -t backend-app:test .

# 3. Test Code Quality
pip install flake8
flake8 .

# 4. Test Security Scan
docker build -t backend-app:scan .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image backend-app:scan
```

## Next Steps

1. ✅ Push this workflow to your repository
2. ✅ Check the Actions tab for the first run
3. ✅ Fix any issues that arise
4. ✅ Consider adding deployment steps after all checks pass
