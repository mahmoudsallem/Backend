# Backend

<p align="left"><img src="static/ci_icon.svg" alt="CI/CD" width="48" height="48" /></p>

Short: CI/CD pipeline for building, testing, scanning, signing, and reporting the backend.

## Table of contents

- [Overview](#overview)
- [Stages & Jobs](#stages--jobs)
- [Reports & Artifacts](#reports--artifacts)
- [Required Secrets & Permissions](#required-secrets--permissions)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Overview

- **Workflow name:** CI/CD Pipeline
- **Trigger:** push to `dev`, pull requests to `dev` (validation)
- **High-level flow:** Secret Scanning → Build & Security Analysis → Parallel Test & Security Jobs → Image Signing (Cosign) → Final Summary

## Stages & Jobs

### Stage 1 — Secret Scanning
- **Job:** `gitleaks`
- **Purpose:** Detect leaked credentials in the repo and history.
- **Runner:** `ubuntu-latest`
- **Key steps:** checkout full history (`fetch-depth: 0`), run `gitleaks/gitleaks-action@v2`

### Stage 2 — Build & Security Analysis
- **Job:** `build-and-secure`
- **Purpose:** Validate `Dockerfile`, build the image, compute digest.
- **Depends on:** `gitleaks`
- **Outputs:** `image_digest` (for signing/reporting)

### Stage 3 — Parallel Test & Security Jobs (depend on `build-and-secure`)
- **`njsscan`** — JS static analysis. Outputs: `njsscan-results.json`, `njsscan-results.sarif`, `njsscan-report.html`.
- **`code-quality`** — Python linting (`flake8`).
- **`semgrep`** — SAST container. Outputs: `semgrep-results.json`, `semgrep-results.sarif`, `semgrep-report.html`.
- **`snyk`** — Dependency + SAST + container scanning. Outputs: per-scan JSON and `snyk-combined-report.html`.
- **`security-scan`** (Trivy) — Image vulnerability scan. Outputs: `trivy-results.json`, `trivy-report.html`.
- **`zap`** — DAST using OWASP ZAP against the locally launched app (`http://127.0.0.1:5000`). If ZAP auto-creates issues, job needs `issues: write`.

### Stage 4 — Image Signing
- **Job:** `cosign-sign`
- **Purpose:** Keyless attestation for the built Docker image.
- **Permissions:** `id-token: write`, `contents: read` (for OIDC)
- **Note:** For registry transparency logs, push the image to a registry first.

### Stage 5 — Summary
- **Job:** `summary` — Aggregate job statuses and link artifacts/SARIF uploads in the run summary.

## Reports & Artifacts

**HTML reports (artifacts):**
- `njsscan-report.html`
- `semgrep-report.html`
- `snyk-combined-report.html`
- `trivy-report.html`
- ZAP output (format depends on action configuration)

**JSON outputs:**
- `njsscan-results.json`
- `semgrep-results.json`
- `snyk-opensource-results.json`
- `snyk-code-results.json`
- `snyk-container-results.json`
- `trivy-results.json`

**SARIF uploads (GitHub Security tab):**
- `njsscan-results.sarif`
- `semgrep-results.sarif`
- `snyk-*.sarif` (if enabled)

## Required Secrets & Permissions

**Required secret:**
- `SNYK_TOKEN` — for Snyk scans

**Optional / conditional:**
- `ZAP_TARGET` — for external target scanning (not used when launching app in CI)

**Workflow permissions to consider:**
- `issues: write` — if ZAP creates GitHub issues
- `id-token: write` — for Cosign keyless signing
- `contents: read` — for jobs that read repo contents

## Troubleshooting

- ZAP: "Resource not accessible by integration" → grant `issues: write` if the job needs to create issues.
- ZAP 404s → ZAP crawls common endpoints; either add routes or ignore expected 404s.
- Snyk fragmentation → rely on `snyk-combined-report.html` as the single source of truth.

## Files & locations

- Workflow: [.github/workflows/CICD.yaml](.github/workflows/CICD.yaml)
- Report generator: [.github/scripts/generate-report.py](.github/scripts/generate-report.py)
- Templates: [.github/templates/](.github/templates/)

## Maintenance

- Keep Actions and scanning tools up-to-date.
- Review fail thresholds periodically.
- Consider gating heavy scans to `main`/`dev` or disabling them on short-lived branches.


# Test CI

