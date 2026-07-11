# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Boilerworks, please report it responsibly.

**Do not open a public issue.**

Instead, email **security@weareconflict.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and aim to release a fix within 7 days for critical issues.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| latest  | Yes       |

## Security Best Practices

When deploying Boilerworks:

- Change all default credentials (database, MinIO)
- Set `DJANGO_SECRET_KEY` to a unique, unpredictable value (required when `DJANGO_DEBUG` is false)
- Set `DJANGO_DEBUG=false`
- Set `DJANGO_ALLOWED_HOSTS` to your domain(s) only
- Configure `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to your domain only
- Use HTTPS in production
