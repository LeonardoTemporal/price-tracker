# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-12

### Added
- MCP Server with 6 tools for external AI tool integration
- AI Price Prediction endpoint using linear regression with confidence scoring
- Dark mode with system preference detection and manual toggle
- Dokploy deployment configuration (dokploy-compose.yml, Dockerfiles, nginx)
- Multi-stage Docker builds for production backend and frontend
- Auto-deploy via GitHub Actions webhook to Dokploy

### Changed
- Downgraded TailwindCSS v4 to v3.4 for PostCSS compatibility
- CI/CD frontend build now passes without continue-on-error

## [1.0.0] - 2026-05-10

### Added
- Initial open source release under MIT License
- Full-stack price tracking with FastAPI + React
- JWT authentication with email verification
- Multi-strategy web scraping (Mercado Libre, Amazon, eBay, generic)
- Interactive price history charts with Recharts
- Real-time dashboard with alerts and statistics
- Docker Compose setup for local development
- GitHub Actions CI with pytest across Python 3.8-3.11
- Comprehensive community docs: CONTRIBUTING.md, CODE_OF_CONDUCT.md
- Cross-platform Makefile
- Swagger and ReDoc API documentation
