GitHub Repository Security Guide
================================

This guide outlines security best practices and recommendations for protecting the Themis Framework repository from malicious activity.

Current Security Status
-----------------------

### ✅ Implemented
- `.gitignore` properly configured to exclude secrets (.env files, API keys)
- CI/CD pipeline with automated testing and linting
- Template files (.env.example) used instead of actual secrets
- QA checks run on all pull requests

### 🚧 Recommended Improvements
See sections below for detailed implementation steps.

Critical Security Recommendations
----------------------------------

## 1. Branch Protection Rules

**Protect your main branch** to prevent unauthorized or untested code from being merged.

### Recommended Settings for Main Branch:

**To configure (GitHub Settings → Branches → Add rule):**

1. **Branch name pattern:** `main` (or `master`)

2. **Require pull request reviews before merging:**
   - ✅ Required approvals: 1+ reviewers
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (if CODEOWNERS file exists)
   - ✅ Require approval of the most recent reviewable push

3. **Require status checks to pass:**
   - ✅ Require branches to be up to date before merging
   - ✅ Status checks that must pass:
     - `Build and Validate / build` (CI workflow)
     - `Lint`
     - `Test`
     - `QA checks`

4. **Require conversation resolution before merging:**
   - ✅ All PR comments must be resolved

5. **Require signed commits:**
   - ⚠️ Optional but recommended for high-security environments
   - Prevents commit impersonation

6. **Require linear history:**
   - ✅ Prevent merge commits, enforce rebase or squash
   - Keeps commit history clean and auditable

7. **Include administrators:**
   - ✅ Apply rules to repository administrators too
   - No one bypasses security checks

8. **Restrict who can push:**
   - ✅ Limit to specific teams or users
   - Prevents accidental force pushes

9. **Allow force pushes:**
   - ❌ Disabled (never allow force pushes to main)

10. **Allow deletions:**
    - ❌ Disabled (prevent accidental branch deletion)

### Example GitHub Settings:
```yaml
# .github/settings.yml (if using probot/settings app)
branches:
  - name: main
    protection:
      required_pull_request_reviews:
        required_approving_review_count: 1
        dismiss_stale_reviews: true
        require_code_owner_reviews: true
      required_status_checks:
        strict: true
        contexts:
          - "Build and Validate"
      enforce_admins: true
      required_linear_history: true
      restrictions: null
```

## 2. Access Control & Permissions

**Principle of Least Privilege:** Grant minimum necessary permissions.

### Repository Roles:

| Role | Permissions | Use Case |
|------|------------|----------|
| **Admin** | Full access, settings, secrets | Repository owners only (1-2 people) |
| **Maintain** | Manage repo without destructive actions | Core maintainers (2-5 people) |
| **Write** | Push to non-protected branches, create PRs | Regular contributors |
| **Triage** | Manage issues and PRs | Community moderators |
| **Read** | View and clone repo | Everyone else (public repos) |

### Team Structure (if organization):
```
themis-core-team (Admin)
  └── Repository owners

themis-maintainers (Maintain)
  └── Trusted maintainers who review PRs

themis-contributors (Write)
  └── Regular contributors with write access

themis-community (Triage)
  └── Community moderators for issues/discussions
```

### Action: Review Current Collaborators
```bash
# Audit who has access
gh api repos/themis-agentic-system/themis-framework/collaborators --paginate
```

## 3. Secret Management

**Never commit secrets to the repository.**

### GitHub Secrets (for CI/CD):
- Go to Settings → Secrets and variables → Actions
- Add secrets needed for CI/CD (e.g., `ANTHROPIC_API_KEY_TEST`)
- Use `${{ secrets.SECRET_NAME }}` in workflows

### Environment-Specific Secrets:
```bash
# Development (local)
.env                    # ✅ Gitignored, never commit

# Production
.env.production         # ✅ Gitignored, deploy via secure channels

# Templates
.env.example            # ✅ Safe to commit, no real values
.env.docker             # ✅ Safe to commit, uses placeholders
```

### Secret Scanning:
GitHub automatically scans for known secret patterns. Enable:
- Settings → Code security and analysis
- ✅ Secret scanning (detect committed secrets)
- ✅ Push protection (prevent commits with secrets)

### Action Items:
1. ✅ Verify `.gitignore` excludes all secret files
2. ✅ Add `ANTHROPIC_API_KEY` to GitHub Secrets for CI (if needed for tests)
3. ✅ Enable secret scanning and push protection
4. ✅ Rotate any keys that may have been exposed

## 4. Dependency Security

**Keep dependencies updated and scan for vulnerabilities.**

### Dependabot Configuration:
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "github-actions"
```

### Dependency Review:
Enable in Settings → Code security and analysis:
- ✅ Dependency graph
- ✅ Dependabot alerts (get notified of vulnerabilities)
- ✅ Dependabot security updates (auto-create PRs for fixes)

### Manual Audits:
```bash
# Check for known vulnerabilities
pip install pip-audit
pip-audit

# Update dependencies
pip list --outdated
```

## 5. Code Scanning (CodeQL)

**Automatically detect security vulnerabilities in code.**

### Add CodeQL Workflow:
Create `.github/workflows/codeql.yml`:
```yaml
name: "CodeQL"

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Mondays

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v3

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
```

### Benefits:
- Detects SQL injection, XSS, path traversal, etc.
- Runs on every PR and weekly
- Creates security alerts in GitHub Security tab

## 6. Code Review Requirements

**Every change must be reviewed by another person.**

### Create CODEOWNERS File:
Create `.github/CODEOWNERS`:
```
# Default owners for everything
* @your-github-username @maintainer-username

# Specific areas
/api/ @api-team-lead
/agents/ @agents-team-lead
/orchestrator/ @orchestrator-team-lead

# Security-critical files
.github/ @security-team
Dockerfile @devops-team
docker-compose.yml @devops-team
/api/security.py @security-team
/api/middleware.py @security-team
```

### Pull Request Template:
Create `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Security fix

## Security Checklist
- [ ] No secrets or API keys committed
- [ ] Input validation added for user-provided data
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies updated and scanned
- [ ] Authentication/authorization properly implemented
- [ ] SQL injection prevention (if applicable)
- [ ] XSS prevention (if applicable)

## Testing
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Linting passes
- [ ] QA checks pass

## Documentation
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Comments added for complex logic
```

## 7. Issue Templates

**Standardize security vulnerability reports.**

### Create Security Issue Template:
Create `.github/ISSUE_TEMPLATE/security_vulnerability.md`:
```markdown
---
name: Security Vulnerability
about: Report a security vulnerability (do NOT use for public disclosure)
title: '[SECURITY] '
labels: 'security'
assignees: ''
---

⚠️ **STOP! Do not report security vulnerabilities publicly here.**

Please report security vulnerabilities via:
- Email: security@themis-agentic-system.org (if configured)
- GitHub Security Advisories: https://github.com/themis-agentic-system/themis-framework/security/advisories/new

For non-sensitive security improvements, you may use this template.

## Description
Brief description of the security concern

## Affected Components
- [ ] API authentication
- [ ] Agent execution
- [ ] Data storage
- [ ] Dependencies
- [ ] Other: ___

## Impact
What could an attacker do with this vulnerability?

## Suggested Fix
How should this be addressed?
```

## 8. Security Policy (SECURITY.md)

**Tell users how to report vulnerabilities.**

Create `SECURITY.md` in repository root (see separate file).

## 9. CI/CD Security

**Secure your GitHub Actions workflows.**

### Best Practices:

1. **Pin action versions:**
   ```yaml
   # ❌ Bad (mutable)
   - uses: actions/checkout@v4

   # ✅ Good (immutable)
   - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
   ```

2. **Minimize permissions:**
   ```yaml
   permissions:
     contents: read
     pull-requests: write
   ```

3. **Use secrets, not hardcoded values:**
   ```yaml
   # ❌ Bad
   env:
     API_KEY: "sk-abc123"

   # ✅ Good
   env:
     API_KEY: ${{ secrets.API_KEY }}
   ```

4. **Limit workflow triggers:**
   ```yaml
   # Be cautious with pull_request_target (has write access to secrets)
   # Prefer pull_request for untrusted PRs
   on:
     pull_request:  # Safe, no secrets access
   ```

5. **Validate external inputs:**
   ```yaml
   # Never use untrusted input directly in run commands
   # ❌ Dangerous:
   - run: echo "${{ github.event.pull_request.title }}"

   # ✅ Safe:
   - run: echo "$PR_TITLE"
     env:
       PR_TITLE: ${{ github.event.pull_request.title }}
   ```

## 10. Monitoring & Auditing

**Track and review security events.**

### Enable Security Features:
Settings → Code security and analysis:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ Push protection
- ✅ Code scanning (CodeQL)

### Audit Log:
- Review regularly: Settings → Audit log
- Monitor for:
  - Permission changes
  - Secret access
  - Branch protection modifications
  - Collaborator additions/removals

### Set Up Notifications:
- Watch the repository (GitHub notifications)
- Configure email alerts for:
  - Security advisories
  - Dependabot alerts
  - Code scanning results

## 11. Signed Commits (Optional)

**Verify commit authenticity with GPG/SSH signatures.**

### Why:
- Prevents commit impersonation
- Proves commits came from legitimate contributors
- Required for high-security compliance

### How to Enable:
```bash
# Configure GPG signing
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_GPG_KEY_ID

# Or use SSH signing (easier)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
```

### Enforce in Branch Protection:
- Settings → Branches → Branch protection rules
- ✅ Require signed commits

## 12. Container Security (Docker)

**Secure your Docker images.**

### Dockerfile Best Practices:
- ✅ Use official base images
- ✅ Pin specific versions (not `latest`)
- ✅ Run as non-root user
- ✅ Multi-stage builds to minimize attack surface
- ✅ Scan images for vulnerabilities

### Docker Compose Security:
```yaml
# Don't bind to 0.0.0.0 in production
ports:
  - "127.0.0.1:8000:8000"  # ✅ Localhost only

# Use secrets, not environment variables
secrets:
  api_key:
    file: ./secrets/api_key.txt
```

### Image Scanning:
```bash
# Scan with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image themis-framework:latest

# Scan with Snyk
snyk container test themis-framework:latest
```

Implementation Checklist
------------------------

### Immediate Actions (Do Now):
- [ ] Enable branch protection on `main` branch
- [ ] Enable secret scanning and push protection
- [ ] Create `SECURITY.md` policy file
- [ ] Add Dependabot configuration
- [ ] Create CODEOWNERS file
- [ ] Review and restrict collaborator access
- [ ] Audit current secrets/credentials

### Short-Term (This Week):
- [ ] Add CodeQL scanning workflow
- [ ] Create pull request template with security checklist
- [ ] Create security issue template
- [ ] Enable all GitHub security features
- [ ] Review audit logs
- [ ] Pin GitHub Actions versions
- [ ] Set up security notifications

### Medium-Term (This Month):
- [ ] Implement signed commit requirement
- [ ] Conduct dependency audit
- [ ] Review and update dependencies
- [ ] Add container scanning to CI/CD
- [ ] Document incident response plan
- [ ] Set up automated security scanning schedule

### Long-Term (Ongoing):
- [ ] Regular security audits (quarterly)
- [ ] Dependency updates (automated via Dependabot)
- [ ] Review access permissions (monthly)
- [ ] Security training for contributors
- [ ] Penetration testing (if handling sensitive data)
- [ ] Compliance reviews (if required)

Common Attack Vectors & Prevention
----------------------------------

### 1. Malicious Pull Requests
**Attack:** Contributor submits PR with backdoor code

**Prevention:**
- ✅ Require code review by trusted maintainer
- ✅ Run automated security scans
- ✅ Review all external contributions carefully
- ✅ Never merge PRs that modify security-critical files without thorough review

### 2. Dependency Vulnerabilities
**Attack:** Exploit known CVEs in dependencies

**Prevention:**
- ✅ Dependabot alerts and auto-updates
- ✅ Regular `pip-audit` scans
- ✅ Pin dependency versions
- ✅ Review dependency changes in PRs

### 3. Secret Leakage
**Attack:** API keys committed to repository

**Prevention:**
- ✅ Gitignore all secret files
- ✅ Secret scanning enabled
- ✅ Push protection blocks commits with secrets
- ✅ Regular audits of commit history

### 4. Supply Chain Attacks
**Attack:** Compromised GitHub Action or Docker base image

**Prevention:**
- ✅ Pin action versions to commit SHAs
- ✅ Use official Docker images
- ✅ Pin Docker image tags
- ✅ Scan containers for vulnerabilities

### 5. Unauthorized Access
**Attack:** Stolen credentials or compromised accounts

**Prevention:**
- ✅ Require 2FA for all contributors
- ✅ Use PATs (Personal Access Tokens) with minimal scopes
- ✅ Rotate secrets regularly
- ✅ Monitor audit logs for suspicious activity

### 6. Code Injection
**Attack:** SQL injection, XSS, command injection in application code

**Prevention:**
- ✅ CodeQL scanning detects common patterns
- ✅ Input validation and sanitization
- ✅ Parameterized queries (no string concatenation)
- ✅ Security-focused code reviews

Additional Resources
--------------------

### GitHub Documentation:
- [About securing your repository](https://docs.github.com/en/code-security/getting-started/securing-your-repository)
- [Configuring branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Managing security and analysis settings](https://docs.github.com/en/code-security/getting-started/securing-your-repository)
- [About secret scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)

### Security Tools:
- [pip-audit](https://github.com/pypa/pip-audit) - Scan Python dependencies for vulnerabilities
- [Trivy](https://github.com/aquasecurity/trivy) - Container and dependency scanner
- [Snyk](https://snyk.io/) - Security scanning for code and containers
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter

### Best Practices:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common web vulnerabilities
- [CWE Top 25](https://cwe.mitre.org/top25/) - Most dangerous software weaknesses
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/best-practices-for-securing-your-repository)

Contact
-------
For security concerns or questions:
- Review `SECURITY.md` for vulnerability reporting
- GitHub Discussions for general security questions
- GitHub Issues (public, non-sensitive security improvements)

Last Updated: 2025-10-26
