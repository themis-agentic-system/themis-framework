## Description
<!-- Provide a brief description of the changes in this PR -->



## Type of Change
<!-- Check all that apply -->
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Security fix
- [ ] Performance improvement
- [ ] Refactoring (no functional changes)
- [ ] Dependency update
- [ ] CI/CD or infrastructure change

## Related Issues
<!-- Link to related issues/discussions -->
Fixes #
Relates to #

## Changes Made
<!-- List the specific changes made in this PR -->
-
-
-

## Security Checklist
<!-- IMPORTANT: Review all items before submitting -->
- [ ] No secrets, API keys, or credentials committed
- [ ] No hardcoded passwords or sensitive data
- [ ] Input validation added for user-provided data
- [ ] Error messages don't leak sensitive information (stack traces, paths, credentials)
- [ ] Dependencies scanned for vulnerabilities (`pip-audit` or Dependabot)
- [ ] Authentication/authorization properly implemented (if applicable)
- [ ] SQL injection prevention verified (if database changes)
- [ ] XSS/injection prevention verified (if user input handling)
- [ ] Proper access controls for new endpoints (if API changes)
- [ ] Rate limiting configured (if new API endpoints)
- [ ] Logging doesn't expose sensitive data
- [ ] Docker image security reviewed (if Dockerfile changes)
- [ ] GitHub Actions security reviewed (if workflow changes)

## Testing Checklist
<!-- Verify all items before requesting review -->
- [ ] Tests added or updated for new/changed functionality
- [ ] All tests pass locally (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] QA checks pass (`make qa`)
- [ ] Manual testing performed (describe below)
- [ ] Edge cases considered and tested
- [ ] Error handling tested
- [ ] Tested with stub mode (if agent changes)
- [ ] Integration tests updated (if applicable)

### Manual Testing Performed
<!-- Describe your manual testing process -->



## Code Quality Checklist
- [ ] Code follows project style guidelines
- [ ] Type hints added for new functions
- [ ] Docstrings added/updated for public functions and classes
- [ ] Comments added for complex logic
- [ ] No commented-out code or debug prints
- [ ] Error handling is comprehensive
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Performance impact considered

## Documentation Checklist
- [ ] README updated (if user-facing changes)
- [ ] API documentation updated (if API changes)
- [ ] CHANGELOG.md updated (if versioned release)
- [ ] Inline code documentation added/updated
- [ ] Configuration documentation updated (if config changes)
- [ ] Migration guide provided (if breaking changes)

## Practice Pack Changes (if applicable)
- [ ] Practice pack schema validated
- [ ] Fixture files updated/added
- [ ] Document generators tested
- [ ] Output artifacts verified
- [ ] Jurisdiction-specific rules reviewed

## Breaking Changes
<!-- If this PR introduces breaking changes, describe them and the migration path -->
- [ ] No breaking changes
- [ ] Breaking changes documented below

### Breaking Changes Details
<!-- List all breaking changes and how users should migrate -->



## Performance Impact
<!-- Describe any performance implications -->
- [ ] No significant performance impact
- [ ] Performance improved (describe how)
- [ ] Performance may be affected (describe and justify)

## Deployment Notes
<!-- Special considerations for deployment -->
- [ ] No special deployment steps required
- [ ] Requires environment variable changes (document below)
- [ ] Requires database migration (document below)
- [ ] Requires infrastructure changes (document below)

### Deployment Steps
<!-- If special steps needed, document here -->



## Screenshots/Logs (if applicable)
<!-- Add screenshots or log outputs demonstrating the changes -->



## Reviewer Notes
<!-- Anything specific you want reviewers to focus on? -->



## Checklist Before Merge
<!-- Final checks before merging -->
- [ ] All CI/CD checks pass
- [ ] At least one approval from CODEOWNERS
- [ ] All review comments addressed
- [ ] Conflicts resolved
- [ ] Branch is up to date with base branch
- [ ] Commit messages are clear and descriptive

---

## For Reviewers

### Review Focus Areas
- [ ] Security considerations addressed
- [ ] Test coverage is adequate
- [ ] Code quality meets standards
- [ ] Documentation is complete
- [ ] No sensitive data exposed
- [ ] Performance impact acceptable
- [ ] Breaking changes properly documented

### Reviewer Checklist
- [ ] Code reviewed for security vulnerabilities
- [ ] Tests reviewed and verified
- [ ] Documentation reviewed
- [ ] Deployment impact assessed
- [ ] Breaking changes understood

---

**Note:** This PR template helps ensure code quality and security. Please fill out all relevant sections before requesting review. If a section doesn't apply, mark it as N/A or check the box.
