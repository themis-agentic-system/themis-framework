Security Policy
===============

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| 0.x.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

We take security seriously and appreciate your efforts to responsibly disclose your findings.

### How to Report

Please report security vulnerabilities using one of the following methods:

1. **GitHub Security Advisories (Preferred)**
   - Go to https://github.com/themis-agentic-system/themis-framework/security/advisories/new
   - Click "Report a vulnerability"
   - Provide detailed information about the vulnerability

2. **Email** (if Security Advisories not available)
   - Contact the maintainers directly via GitHub Discussions
   - Mark the discussion as private if possible
   - Include "SECURITY" in the subject line

### What to Include

When reporting a vulnerability, please include:

- **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
- **Affected component** (e.g., API endpoint, agent, orchestrator)
- **Steps to reproduce** (detailed, step-by-step)
- **Proof of concept** (code, screenshots, or curl commands)
- **Impact assessment** (what can an attacker do?)
- **Suggested fix** (if you have one)
- **Your contact information** (for follow-up)

### What to Expect

- **Acknowledgment:** We'll confirm receipt within 48 hours
- **Assessment:** We'll investigate and assess severity within 1 week
- **Updates:** We'll keep you informed of our progress
- **Fix:** We'll work on a patch and coordinate disclosure timing with you
- **Credit:** We'll acknowledge your contribution (if you wish) in the security advisory

### Disclosure Policy

- **Coordinated Disclosure:** Please give us reasonable time to fix the issue before public disclosure
- **Typical Timeline:**
  - Simple fixes: 1-2 weeks
  - Complex fixes: 2-4 weeks
  - Critical vulnerabilities: Expedited as quickly as possible
- **Public Disclosure:** We'll publish a security advisory when a fix is released

## Security Best Practices for Users

If you're using Themis Framework, please follow these security guidelines:

### API Keys & Secrets

- **Never commit** `.env` files or API keys to version control
- **Use environment variables** for all sensitive configuration
- **Rotate API keys** regularly (at least every 90 days)
- **Use separate keys** for development, staging, and production
- **Enable key rotation** in production deployments

### API Security

- **Set `THEMIS_API_KEY`** in production (don't run without authentication)
- **Use HTTPS** in production (never HTTP for sensitive data)
- **Enable rate limiting** to prevent abuse
- **Restrict network access** (firewall, VPC, security groups)
- **Monitor API logs** for suspicious activity

### Data Protection

- **Sanitize user inputs** before processing with agents
- **Validate matter payloads** before execution
- **Don't store sensitive client data** in logs or artifacts
- **Use encryption** for data at rest and in transit
- **Implement access controls** for multi-tenant deployments

### Dependencies

- **Keep dependencies updated** (use Dependabot)
- **Review dependency updates** before merging
- **Scan for vulnerabilities** regularly with `pip-audit`
- **Pin dependency versions** in production

### Docker Security

- **Don't use `latest` tags** in production
- **Run containers as non-root** user (default in Themis)
- **Scan images** for vulnerabilities before deployment
- **Bind to localhost** (127.0.0.1) unless public access needed
- **Use Docker secrets** instead of environment variables for sensitive data

### Monitoring

- **Enable structured logging** for security events
- **Monitor Prometheus metrics** for anomalies
- **Set up alerts** for failed authentication attempts
- **Review audit logs** regularly
- **Track API usage** to detect abuse

## Known Security Considerations

### LLM Integration

Themis Framework integrates with Anthropic's Claude API. Be aware:

- **Prompt injection:** User-provided matter data could influence agent behavior
- **Data privacy:** Matter content is sent to Anthropic's API (review their privacy policy)
- **Cost abuse:** Malicious actors could generate expensive API calls (use rate limiting)
- **Output validation:** Always review agent outputs before using in production

**Mitigations:**
- Input sanitization is implemented for matter payloads
- Rate limiting is enforced on API endpoints
- Stub mode available for testing without API calls
- Human review is the final step before any client communication

### API Vulnerabilities

The Themis API currently includes:

- **Authentication:** API key-based (optional in development mode)
- **Rate limiting:** Configurable per endpoint
- **Input validation:** Pydantic models with size limits
- **Logging:** Request tracking and audit trails

**Recommendations:**
- Always enable authentication in production (`THEMIS_API_KEY`)
- Use HTTPS/TLS in production deployments
- Review and adjust rate limits based on your use case
- Monitor logs for failed authentication attempts

### Data Storage

Themis stores execution plans and artifacts in:

- **SQLite database:** `orchestrator_state.db` (local filesystem)
- **In-memory cache:** TTL-based caching (60 seconds default)

**Security notes:**
- Database is not encrypted at rest (add encryption if storing sensitive data)
- Cache is cleared on service restart
- Artifacts may contain client-confidential information (secure the database file)

## Vulnerability Disclosure History

We will maintain a public record of security vulnerabilities and fixes:

| CVE | Severity | Component | Fixed In | Reported By |
| --- | -------- | --------- | -------- | ----------- |
| TBD | N/A      | N/A       | N/A      | N/A         |

*No vulnerabilities have been reported yet.*

## Security Updates

We publish security updates through:

- **GitHub Security Advisories:** https://github.com/themis-agentic-system/themis-framework/security/advisories
- **GitHub Releases:** Tagged releases with security notes
- **CHANGELOG.md:** Detailed change logs with security fixes highlighted

Subscribe to repository notifications to receive security alerts.

## Security Tooling

We use the following automated security tools:

- **GitHub Secret Scanning:** Detects accidentally committed secrets
- **GitHub Push Protection:** Prevents commits containing secrets
- **Dependabot:** Automated dependency vulnerability scanning and updates
- **CodeQL:** Static code analysis for security vulnerabilities (planned)
- **CI/CD Security Checks:** Automated linting, testing, and validation

## Compliance

Themis Framework is designed for legal professional use. If you have specific compliance requirements:

- **GDPR/Privacy:** Review data handling practices with your legal team
- **SOC 2:** Consider additional controls for production deployments
- **HIPAA:** Not recommended for PHI without additional safeguards
- **Attorney-Client Privilege:** Ensure proper data handling procedures

We recommend conducting your own security assessment before production use.

## Bug Bounty Program

We currently **do not** have a formal bug bounty program, but we deeply appreciate security researchers who:

- Responsibly disclose vulnerabilities
- Follow coordinated disclosure practices
- Help us improve security for all users

We will publicly acknowledge contributors (with permission) in security advisories.

## Contact

For security questions or concerns:

- **Private Vulnerabilities:** Use GitHub Security Advisories (preferred)
- **General Security Questions:** GitHub Discussions
- **Non-Sensitive Improvements:** GitHub Issues with `security` label

## Additional Resources

- [Security Guide](docs/SECURITY_GUIDE.md) - Comprehensive repository security best practices
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production security configuration
- [API Reference](docs/API_REFERENCE.md) - API authentication and security details

Thank you for helping keep Themis Framework and our users safe!
