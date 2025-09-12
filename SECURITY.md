# Security Policy

## Supported Versions
We aim to support the latest tagged release and the current `main` branch.

## Reporting a Vulnerability
Please email: security@example.org (replace with your address)
- Include steps to reproduce and potential impact
- Provide version/commit SHA and environment details
- We will acknowledge receipt within 72 hours and follow up with remediation steps

## Handling Secrets
- Use environment variables (`.env`) for local dev
- Never commit secrets; rotate immediately if leaked
