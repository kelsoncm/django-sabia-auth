# Changelog

All notable changes to `django-sabia-auth` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-01

### Added

- Initial release
- `SabiaOAuth2Client` for OAuth2 authorization code flow
- `SabiaAPIClient` for user management API
- `SabiaAuthBackend` Django authentication backend
- `SabiaLoginView` and `SabiaCallbackView` class-based views
- Utility functions: `get_sabia_settings`, `get_oauth2_client`, `get_api_client`, `generate_state`
- Custom exceptions: `SabiaAuthError`, `SabiaTokenError`, `SabiaUserInfoError`, `SabiaAPIError`, `SabiaStateMismatchError`
- GitHub Actions CI workflow
- Pre-commit configuration
