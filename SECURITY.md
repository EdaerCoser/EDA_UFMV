# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          | Security Updates |
|---------|--------------------|------------------|
| 0.3.x   | :white_check_mark: Yes              | Until v0.4.0 release  |
| 0.2.x   | :white_check_mark: Yes              | Until v0.4.0 release  |
| 0.1.x   | :x: No                | No longer supported   |
| < 0.1.0 | :x: No                | No longer supported   |

## Reporting a Vulnerability

If you discover a security vulnerability in EDA_UFMV, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please send an email to: **security@eda-ufmv.org**

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Suggested mitigation (if any)

### What to Expect

1. **Confirmation**: You will receive an acknowledgment of your report within 48 hours
2. **Assessment**: We will assess the vulnerability and determine its severity
3. **Resolution**: We will work on a fix and coordinate disclosure with you
4. **Disclosure**: We will announce the security fix and release a patched version

### Response Time

- **Critical** (CVSS 9.0-10.0): 48 hours
- **High** (CVSS 7.0-8.9): 1 week
- **Medium** (CVSS 4.0-6.9): 2 weeks
- **Low** (CVSS 0.1-3.9): 1 month

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest stable version
2. **Review Dependencies**: Regularly update dependencies
3. **Sandbox Testing**: Test in isolated environments before production use
4. **Code Review**: Review code before deploying to critical systems

### For Developers

1. **Input Validation**: Always validate user input
2. **Dependency Management**: Keep dependencies updated
3. **Code Review**: Have security-sensitive code reviewed
4. **Testing**: Include security tests in your test suite

## Security Features

EDA_UFMV includes several security-conscious design features:

### Randomization Security

- Seeded randomization for reproducible results
- Cryptographically strong random number generation (when using system RNG)
- No hidden state manipulation

### Register Model Security

- Access control enforcement (RW, RO, WO, etc.)
- Back-door access isolation
- Hardware abstraction layer

### Coverage Database

- File-based databases with integrity checks
- Isolated sampling environments
- No cross-contamination between test runs

## Dependency Security

We regularly audit and update our dependencies. Current dependencies:

### Core (No External Dependencies)
- Python standard library only

### Optional Dependencies
- **z3-solver**: SMT solver for constraint solving (licensed under MIT)
- **pytest**: Testing framework (MIT licensed)
- **paramiko**: SSH library for remote access (LGPL 2.1+)

For a complete list, see [setup.py](setup.py) or [pyproject.toml](pyproject.toml).

## Security Audits

| Date       | Version | Auditor         | Status |
|------------|---------|-----------------|--------|
| TBD        | 0.3.0   | Pending         | Open   |

## Contact

For general security questions:
- Email: security@eda-ufmv.org
- GitHub Security: https://github.com/EdaerCoser/EDA_UFMV/security

Thank you for helping keep EDA_UFMV safe!
