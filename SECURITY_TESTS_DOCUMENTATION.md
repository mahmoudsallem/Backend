# CI/CD Security Tests Documentation

## Table of Contents
1. [Overview](#overview)
2. [Pipeline Stages](#pipeline-stages)
3. [Security Tools & Tests](#security-tools--tests)
4. [Test Results Interpretation](#test-results-interpretation)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This CI/CD pipeline implements **5 security testing layers** to protect the application across the entire software development lifecycle:

<<<<<<< HEAD
| Stage | Purpose | Type |
|-------|---------|------|
| **Stage 1: Secret Scanning** | Detect accidentally committed credentials | SAST |
| **Stage 2: Build** | Build Docker image and cache for testing | N/A |
| **Stage 3: Test** | Run 7 parallel security & quality tests | Mixed |
| **Stage 4: Sign** | Sign Docker image for provenance | Signing |
| **Stage 5: Summary** | Aggregate and report all results | Reporting |
=======
| Stage | Purpose | Type | Speed |
|-------|---------|------|-------|
| **Stage 1: Secret Scanning** | Detect accidentally committed credentials | SAST | ~2 min |
| **Stage 2: Build** | Build Docker image and cache for testing | N/A | ~5-10 min |
| **Stage 3: Test** | Run 7 parallel security & quality tests | Mixed | ~10-20 min |
| **Stage 4: Sign** | Sign Docker image for provenance | Signing | ~2 min |
| **Stage 5: Summary** | Aggregate and report all results | Reporting | ~1 min |

**Total Pipeline Time:** ~20-40 minutes
>>>>>>> 67b1ad328d3237163d3470596736e589ccab4ef7

---

## Pipeline Stages

### Stage 1: Secret Scanning

**Job:** `gitleaks`

**Purpose:** Scan the entire git history for accidentally committed secrets before any other testing.

**When it runs:** First, no dependencies

**Output:** SARIF format (GitHub Code Scanning integration)

---

### Stage 2: Build

**Job:** `build`

**Purpose:** 
- Build a single Docker image once
- Cache and share it across all test jobs (efficiency)

**Key features:**
- Runs after Gitleaks passes
- Exports `image_digest` for downstream jobs
- Saves image as artifact for 1 day retention

---

### Stage 3: Test (7 Parallel Jobs)

<<<<<<< HEAD
All 7 security/quality jobs run **simultaneously** after the build completes. Each job produces machine-readable reports (JSON/SARIF/JUnit) under `reports/` and exits with a non-zero status on failure according to pipeline policy.

#### 3a. Application Tests (pytest)

- **Purpose:** Run unit, integration, and API contract tests to validate functionality before security checks.
- **Command:** `pytest -q --maxfail=1 --junitxml=reports/pytest-results.xml`
- **Inputs:** source code, test suite, test DB fixtures or test config.
- **Outputs:** JUnit XML, console logs, optional coverage report (`coverage.xml`).
- **Fail criteria:** any test failure (non-zero exit).
- **Remediation:** fix failing tests; add regression tests for uncovered cases.

#### 3b. Bandit (Python Security)

- **Purpose:** Static scan for Python-specific security anti-patterns (injection, insecure crypto, unsafe deserialization).
- **Command:** `bandit -r . -f json -o reports/bandit.json`
- **Inputs:** Python source files (exclude virtualenvs, test artifacts).
- **Outputs:** JSON report with findings, severities, and file locations.
- **Fail criteria:** policy-driven threshold (e.g., any HIGH findings block merge).
- **Remediation:** apply secure coding fixes (use parameterized queries, safer libraries), then re-run tests.

#### 3c. Code Quality (flake8)

- **Purpose:** Enforce style, detect syntax errors and maintainability issues.
- **Command:** `flake8 . --output-file=reports/flake8.txt --max-line-length=127`
- **Inputs:** source files.
- **Outputs:** lint report; optionally converted to machine-readable format for dashboards.
- **Fail criteria:** lint errors (configurable; teams often treat errors as blocking and warnings as advisory).
- **Remediation:** run autoformatters (`black`, `isort`) and fix remaining issues.

#### 3d. Semgrep (SAST)

- **Purpose:** Semantic static analysis for complex, context-aware patterns (injection, auth bypasses, insecure crypto).
- **Command:** `semgrep --config auto --json --output=reports/semgrep.json`
- **Inputs:** source code and optional custom rule packs.
- **Outputs:** JSON/SARIF with rule IDs, severity, and code spans.
- **Fail criteria:** policy-defined (block on CRITICAL/HIGH); lower severities can be reported for triage.
- **Remediation:** implement secure fixes, add test coverage, or add documented suppressions for false positives.

#### 3e. Snyk (Dependencies/Code/Container)

- **Purpose:** Detect vulnerable dependencies and source-code issues across OSS and container layers.
- **Commands:**
  - `snyk test --json > reports/snyk-deps.json`
  - `snyk code test --json > reports/snyk-code.json`
- **Inputs:** `requirements.txt`, lock files, and the built Docker image.
- **Outputs:** JSON with CVEs, remediation guidance, and suggested upgrades/patches.
- **Fail criteria:** HIGH/CRITICAL vulnerabilities per policy.
- **Remediation:** upgrade or pin dependencies; update base image and rebuild.

#### 3f. Trivy (Docker Image Scanning)

- **Purpose:** Scan the built Docker image for OS and package vulnerabilities and misconfigurations.
- **Command:** `trivy image --format json -o reports/trivy.json $IMAGE`
- **Inputs:** Docker image artifact generated in the Build stage.
- **Outputs:** JSON with CVEs, severities, and fix suggestions.
- **Fail criteria:** CRITICAL/HIGH vulnerabilities (configurable).
- **Remediation:** use minimal/base-updated images, update packages, and rebuild.

#### 3g. OWASP ZAP (DAST)

- **Purpose:** Runtime scanning of the live application to find runtime issues (XSS, CSRF, auth problems).
- **Preconditions:** application started from the image and reachable (e.g., `http://127.0.0.1:5000`), test DB or stubbed services available.
- **Command (example):** `zap-baseline.py -t http://127.0.0.1:5000 -r reports/zap.html`
- **Inputs:** running app endpoints, optional authentication credentials for authenticated scans.
- **Outputs:** HTML/JSON/SARIF report with attack traces and affected endpoints.
- **Fail criteria:** policy on HIGH/CRITICAL findings.
- **Remediation:** fix runtime bugs, add input validation, harden headers and auth flows.

---

=======
All 7 security/quality jobs run **simultaneously** after the build completes:

#### 3a. Application Tests (pytest)
#### 3b. Bandit (Python Security)
#### 3c. Code Quality (flake8)
#### 3d. Semgrep (SAST)
#### 3e. Snyk (Dependencies/Code/Container)
#### 3f. Trivy (Docker Image Scanning)
#### 3g. OWASP ZAP (DAST)

>>>>>>> 67b1ad328d3237163d3470596736e589ccab4ef7
---

### Stage 4: Sign

**Job:** `cosign-sign`

**Purpose:** Sign the Docker image for provenance and authenticity verification.

**Runs after:** All 7 test jobs pass

---

### Stage 5: Summary

**Job:** `summary`

**Purpose:** Generate final pipeline report with all job statuses.

**Runs after:** Everything completes (even if some jobs fail)

---

## Security Tools & Tests

### 1. **Gitleaks** — Secret Scanning

**Type:** SAST (Static)  
**Focus:** Credentials & API keys  

#### What it does:
- Scans entire git history (all commits, branches, tags)
- Detects 100+ types of secrets: AWS keys, GitHub tokens, API keys, private keys, etc.
- Runs before any code analysis (fails fast on exposed secrets)

#### What to look for in output:

```
✅ PASS: "results": []
- Zero secrets found — your repository is clean
- This is the ideal state

❌ FAIL: "results": [{...findings...}]
- Secret pattern detected in git history
- Action: Rotate the credential immediately, remove it from history
```

#### Sample secrets detected:
- AWS Access Keys: `AKIA...`
- GitHub Tokens: `ghp_...`, `gho_...`
- Private SSH Keys: `-----BEGIN PRIVATE KEY-----`
- API Keys: Stripe, Twilio, SendGrid, etc.
- Database credentials: `postgresql://user:pass@host`

#### Run locally:
```bash
pip install gitleaks
gitleaks detect --source . --verbose
```

---

### 2. **Bandit** — Python Security Scanner

**Type:** SAST (Static)  
**Focus:** Python code security issues  

#### What it does:
- Scans Python code for security anti-patterns
- Identifies: SQL injection, insecure cryptography, hardcoded passwords, etc.
- Runs fast (source code only)

#### Severity Levels:
- **HIGH** — Critical security issues, must fix
- **MEDIUM** — Important but may have workarounds
- **LOW** — Best practices, low immediate risk

#### What to look for in output:

```
✅ PASS: Few or zero HIGH findings
- Expected for clean code

⚠️  WARNING: MEDIUM or LOW findings
- Review and fix if practical

❌ FAIL: HIGH findings
- Immediately investigate and fix before merging
```

#### Example findings:
- Hardcoded SQL: `query = "SELECT * FROM users WHERE id=" + user_input`
- Weak crypto: `hashlib.md5()` instead of `sha256`
- Pickle deserialize: `pickle.loads(untrusted_data)`
- Tempfile: `tempfile.mktemp()` (predictable names)

#### Run locally:
```bash
pip install bandit
bandit -r . --exclude ./venv,./tests -f json -o bandit-results.json
```

---

### 3. **Code Quality (flake8)** — Linting & Style

**Type:** Quality Gate  
**Focus:** Code style, syntax, complexity  

#### What it does:
- Enforces PEP 8 style guide
- Checks for undefined variables, unused imports
- Limits complexity (max 10)
- Limits line length (max 127 chars)

#### What to look for in output:

```
✅ PASS: No errors or warnings
- Code meets style standards

⚠️  WARNING: Warnings only
- Usually OK to ignore or fix as technical debt

❌ FAIL: Errors (E9, F63, F7, F82)
- Must fix before merging
```

#### Example errors:
- `E9`: Syntax errors
- `F63`: Future feature errors
- `F7`: Type comment issues
- `F82`: Undefined names

#### Run locally:
```bash
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

---

### 4. **Semgrep** — SAST (Static Application Security Testing)

**Type:** SAST (Static)  
**Focus:** Complex code vulnerabilities  

#### What it does:
- Runs **1000+ security rules** on source code
- Detects: injection flaws, XSS, authentication bypasses, weak crypto, etc.
- Uses semantic analysis (understands code structure, not just patterns)
- Auto-configured with `--config auto` (Semgrep Registry)

#### Severity Levels:
- **CRITICAL** — Immediate exploit risk
- **HIGH** — Serious vulnerability
- **MEDIUM** — Moderate risk
- **LOW** — Best practices

#### What to look for in output:

```json
"results": [
  {
    "rule_id": "python.lang.best-practice.use-of-assert",
    "severity": "MEDIUM",
    "message": "...",
    "location": {"path": "app.py", "start_line": 42}
  }
]
```

#### Example findings:
- SQL injection: String concatenation in queries
- Command injection: `os.system(user_input)`
- Weak randomness: `random.choice()` for crypto
- Hardcoded secrets: API keys in code

#### Run locally:
```bash
docker run --rm -v /path/to/repo:/src semgrep/semgrep semgrep scan --config auto /src
```

---

### 5. **Snyk** — Dependency & Code Vulnerability Scanner

**Type:** Hybrid SAST + Dependency Scanning  
**Focus:** Dependencies, OS packages, code vulnerabilities  

#### What it does:
Runs **3 sub-scans**:

##### 5a. Snyk Open Source (Dependencies)
- Scans `requirements.txt`, `package-lock.json`, etc.
- Identifies known CVEs in libraries
- Checks for outdated versions
- Risk: Supply chain attacks, inherited vulnerabilities

##### 5b. Snyk Code (Source Code SAST)
- Analyzes Python/JS/Java source for custom code flaws
- Similar to Semgrep but different rule set
- Complements Semgrep for coverage

##### 5c. Snyk Container (Docker Image)
- Scans Docker layers for OS-level vulnerabilities
- Checks base image, system packages, Python packages
- Identifies unpatched OS libraries

#### Output Format:

```json
{
  "uniqueCount": 5,
  "vulnerabilities": [
    {
      "id": "SNYK-PYTHON-FLASK-1234567",
      "title": "Flask Security Issue",
      "severity": "high",
      "from": ["flask@2.0.1"],
      "remediation": "Upgrade to flask@2.0.2"
    }
  ]
}
```

#### Severity Mapping:
- **CRITICAL** — Exploit in the wild
- **HIGH** — Likely exploitable
- **MEDIUM** — Possible exploitation
- **LOW** — Difficult to exploit

#### What to look for:

```
✅ PASS: N/A or 0 vulnerabilities
- Dependencies are secure and up-to-date

⚠️  WARNING: LOW/MEDIUM vulnerabilities
- Review and patch in next release

❌ FAIL: HIGH/CRITICAL vulnerabilities
- Fix immediately before deployment
```

#### Run locally:
```bash
npm install -g snyk
snyk auth  # Authenticate with token
snyk test  # Check dependencies
snyk code test  # Check source code
```

---

### 6. **Trivy** — Docker Image Vulnerability Scanner

**Type:** Container Image Scanning  
**Focus:** OS and library vulnerabilities in Docker image  

#### What it does:
- Scans Docker image filesystem
- Detects vulnerabilities in base image (OS packages)
- Checks application dependencies (Python packages, etc.)
- Generates comprehensive reports

#### Output Categories:
- **OS Packages** (from base image, e.g., `ubuntu:20.04`)
- **Application Libraries** (Python, Node.js, Java, etc.)
- **Unfixed vulnerabilities** (known but no patch available)

#### Example output:
```
┌────────────────────────────────────────────────────────────────┐
│                           Vulnerabilities                       │
├─────────────────┬──────────────────┬─────────┬─────────┬────────┤
│ Library         │ Vulnerability ID │ Severity│ Status  │ Fixed  │
├─────────────────┼──────────────────┼─────────┼─────────┼────────┤
│ openssl         │ CVE-2021-12345   │ CRITICAL│ unfixed │ -      │
│ curl            │ CVE-2022-67890   │ HIGH    │ fixed   │ 7.86.0 │
└─────────────────┴──────────────────┴─────────┴─────────┴────────┘
```

#### What to look for:

```
✅ PASS: Only LOW/unfixed vulnerabilities
- Safe to deploy; unfixed issues monitored

⚠️  WARNING: MEDIUM vulnerabilities
- Consider upgrading base image or libraries

❌ FAIL: CRITICAL/HIGH fixable vulnerabilities
- Upgrade immediately; blocking deployment
```

#### Best practices:
- Use minimal base images: `python:3.12-slim` instead of `python:3.12`
- Keep base image updated regularly
- Pin dependency versions in `requirements.txt`
- Scan regularly, not just at build time

#### Run locally:
```bash
trivy image backend-app:latest
trivy image --severity CRITICAL,HIGH backend-app:latest
```

---

### 7. **OWASP ZAP** — Dynamic Application Security Testing (DAST)

**Type:** DAST (Dynamic)  
**Focus:** Runtime vulnerabilities (requires running app)  

#### What it does:
- Starts the **live Flask application**
- Sends HTTP requests to test endpoints
- Detects runtime vulnerabilities: injection, XSS, CSRF, etc.
- Requires app to be running and responsive

#### Pre-scan requirements:
1. **App startup** — Waits up to 30 seconds for `/health` endpoint
2. **Database** — Uses SQLite in-memory or temp file
3. **Network** — Tests `http://127.0.0.1:5000`

#### Test categories:
- **SQL Injection** — Testing params with malicious SQL
- **Cross-Site Scripting (XSS)** — Script injection attempts
- **CSRF** — Cross-Site Request Forgery
- **Authentication bypass** — Testing login mechanisms
- **Information disclosure** — Checking for sensitive data leaks
- **Path traversal** — Directory/file access attempts
- **Security misconfiguration** — Headers, SSL, etc.

#### Output format:
```xml
<site name="http://127.0.0.1:5000">
  <alerts>
    <alertitem>
      <pluginid>10000</pluginid>
      <name>SQL Injection</name>
      <riskcode>3</riskcode>  <!-- 3=HIGH, 2=MEDIUM, 1=LOW -->
      <confidence>2</confidence>
      <url>http://127.0.0.1:5000/api/tasks</url>
      <evidence>Payload: 1' OR '1'='1</evidence>
    </alertitem>
  </alerts>
</site>
```

#### What to look for:

```
✅ PASS: No HIGH/CRITICAL findings
- Application is secure at runtime

⚠️  WARNING: LOW/MEDIUM findings
- Review; some may be false positives
- Disable false positive rules in `.zap/rules.tsv`

❌ FAIL: HIGH/CRITICAL findings
- Immediate fix required; likely real vulnerability
```

#### Common false positives:
- Informational messages tagged as vulnerabilities
- Test endpoints not in production code
- Expected error messages flagged as information disclosure

#### Disable false positives:
Create `.zap/rules.tsv`:
```
10043	IGNORE	X-Frame-Options Header Missing
10016	IGNORE	Web Browser XSS Protection Not Enabled
10010	IGNORE	Cookie Without HttpOnly Flag
```

#### Run locally:
```bash
# Start Flask app
python app.py

# In another terminal, run ZAP
docker run --rm -t \
  -v $(pwd):/zap/wrk:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://127.0.0.1:5000 -r report.html
```

---

## Test Results Interpretation

### How to read the Summary

The CI/CD summary shows all stages and jobs:

```
### CI/CD Pipeline Summary

#### Stage 1: Secret Scanning
| Job | Status |
|-----|--------|
| Gitleaks | `success` |

#### Stage 2: Build
| Job | Status |
| Build Docker Image | `success` |

#### Stage 3: Test
| Job | Status |
| Application Tests (pytest) | `success` |
| Bandit (Python Security) | `success` |
| Code Quality (flake8) | `success` |
| Semgrep (SAST) | `success` |
| Snyk (Dependencies/Code/Container) | `success` |
| Trivy Security Scan | `success` |
| OWASP ZAP (DAST) | `success` |

#### Stage 4: Sign
| Job | Status |
| Cosign Image Signing | `success` |
```

### Status Values:
- **`success`** — Job completed, no critical issues
- **`failure`** — Job failed; check logs and fix
- **`skipped`** — Job was skipped (conditional logic)
- **`cancelled`** — User cancelled the pipeline

---

## Best Practices

### 1. **Secrets Management**
- ✅ Use environment variables, never hardcode secrets
- ✅ Rotate exposed credentials immediately
- ✅ Use GitHub Secrets for CI/CD tokens
- ✅ Review git history periodically with Gitleaks

### 2. **Dependency Security**
- ✅ Keep `requirements.txt` pinned to minor versions: `flask==3.0.*`
- ✅ Use `pip audit` locally to check before committing
- ✅ Update dependencies regularly (weekly or monthly)
- ✅ Review CVE reports when updates available

### 3. **Code Security**
- ✅ Parameterize queries: `db.session.execute(query, {"id": user_id})`
- ✅ Use secure random: `secrets.token_urlsafe()` not `random.choice()`
- ✅ Validate all user input before use
- ✅ Use HTTPS only in production

### 4. **Docker Image Security**
- ✅ Use minimal base images (`python:3.12-slim`)
- ✅ Run as non-root user in Dockerfile
- ✅ Scan images regularly (CI/CD + locally)
- ✅ Keep base image updated (monthly patches)

### 5. **CI/CD Best Practices**
- ✅ Review all test reports in artifacts before merging
- ✅ Fail the build on HIGH/CRITICAL findings
- ✅ Triage and fix issues, don't suppress them
- ✅ Keep security tools up-to-date

---

## Troubleshooting

### Common Issues & Solutions

#### 1. Gitleaks finds old secret in history

**Problem:** Git shows an old credential that's been rotated.

**Solution:**
```bash
# Option 1: Remove from history (rebase/squash)
git rebase -i HEAD~20

# Option 2: Use git-filter-repo
pip install git-filter-repo
git filter-repo --invert-paths --path <file-with-secret>

# Option 3: Ignore in Gitleaks config (if false positive)
# .gitleaks.toml
[allowlist]
regexes = ["(old-test-key-pattern)"]
```

#### 2. Bandit/Semgrep reports false positive

**Problem:** Security tool flags code that's actually safe.

**Solution:**
```python
# Add ignore comment
import pickle
data = pickle.loads(untrusted_data)  # nosec (Bandit)
# or
data = pickle.loads(untrusted_data)  # semgrep: ignore=...
```

#### 3. ZAP DAST fails with "App did not become ready"

**Problem:** Flask app takes too long to start.

**Solution:**
```yaml
# In .github/workflows/CICD.yaml
- name: Wait for app to be ready
  run: |
    for i in {1..60}; do  # Increase from 30 to 60
      if curl -fsS http://127.0.0.1:5000/health >/dev/null; then
        echo "App is ready"
        exit 0
      fi
      sleep 2
    done
```

#### 4. Snyk shows "N/A vulnerabilities"

**Problem:** Snyk token missing or invalid.

**Solution:**
```bash
# Add token to GitHub Secrets
1. Go to Settings → Secrets and variables → Actions
2. Add SNYK_TOKEN from https://snyk.io/account/settings/api
3. Re-run pipeline
```

#### 5. Trivy image scan shows many unfixed vulnerabilities

**Problem:** Base image or dependencies have known CVEs.

**Solution:**
```dockerfile
# Use minimal, updated base image
FROM python:3.12-slim

# Or pin to specific patched version
FROM ubuntu:22.04  # Ubuntu 20.04 is EOL
```

#### 6. Build fails: "Dockerfile not found"

**Problem:** Pipeline can't find Dockerfile.

**Solution:**
```bash
# Ensure Dockerfile exists in repo root
ls -la Dockerfile

# Or create a minimal one
cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
EOF
```

---

## Artifact Reports

All jobs produce artifacts stored for 30 days:

| Job | Artifacts | Format |
|-----|-----------|--------|
| Gitleaks | SARIF | GitHub Code Scanning |
| Bandit | HTML, SARIF, JSON | Reports & Integration |
| Semgrep | HTML, SARIF, JSON | Reports & Integration |
| Snyk | HTML, SARIF, JSON | Reports & Integration |
| Trivy | HTML, JSON | Reports |
| ZAP | XML, HTML, JSON | Reports |
| App Tests | HTML, XML, coverage | Reports |

**Access artifacts:**
1. Go to GitHub Actions run
2. Scroll to "Artifacts" section
3. Download the report
4. Open HTML in browser

---

## Security Score Calculation

A simplified security score based on pipeline results:

```
Base: 100
- Per HIGH finding: -10
- Per CRITICAL finding: -20
- Per failed job: -5

Example:
100 - (2 HIGH × 10) - (1 CRITICAL × 20) = 60/100 (⚠️  Fair)
100 - (0 findings) = 100/100 (✅ Excellent)
```

---

## References

- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **Bandit:** https://bandit.readthedocs.io
- **Semgrep:** https://semgrep.dev
- **Snyk:** https://snyk.io
- **Trivy:** https://github.com/aquasecurity/trivy
- **OWASP ZAP:** https://www.zaproxy.org
- **OWASP Top 10:** https://owasp.org/www-project-top-ten

---

## Document Version

- **Created:** February 9, 2026
- **Version:** 1.0
- **Last Updated:** February 9, 2026
- **Maintainer:** Security Team
