# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-05-12

### Added

#### AI-Powered Price Prediction
- New endpoint `/api/predict/{product_id}` using linear regression
- Frontend component with trend indicator and confidence score
- Predicts price direction and estimated dates to reach target price

#### MCP Server Integration
- Full Model Context Protocol server with 6 tools
- Claude Code can now query prices, add products, and check alerts directly
- Documentation: `docs/MCP_INTEGRATION.md`

#### Dark Mode
- System preference detection + manual toggle
- Full UI coverage with Tailwind dark variants
- Persistent theme preference per user

#### Production Deployment
- Dokploy-ready with multi-stage Docker builds
- PostgreSQL support with health checks
- Nginx SPA configuration with security headers
- Auto-deploy via GitHub Actions webhook

#### Quality
- 24+ backend tests passing (Python 3.8-3.11)
- CI/CD with GitHub Actions
- MIT License
- Full contribution infrastructure (CONTRIBUTING.md, CODE_OF_CONDUCT.md)

---

## [1.0.0] - 2025-01-12

### Added
- Initial open source release under MIT License
- Full-stack price tracking application with FastAPI backend and React frontend
- JWT-based authentication system with email verification
- Multi-strategy web scraping engine supporting Mercado Libre, Amazon, eBay, and generic sites
- Interactive price history charts with Recharts
- Real-time dashboard with product statistics and alerts
- Target price alerts with savings calculation
- Responsive UI optimized for mobile, tablet, and desktop
- Docker Compose setup for easy local deployment
- GitHub Actions CI pipeline for automated testing and builds
- Comprehensive test suite with pytest and mock data
- Community documentation: CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates
- Cross-platform Makefile for development workflow
- Complete API documentation with Swagger and ReDoc

### Features
- User registration and login with secure password hashing (bcrypt)
- Product CRUD operations with per-user data isolation
- Automatic and manual price updates for tracked products
- URL testing to verify scraper compatibility before adding products
- Price history tracking with min/max statistics
- Alert system when current price reaches target price
- Dark mode support
- Mobile-first responsive design with TailwindCSS

### Technical
- FastAPI 0.104+ with async/await support
- SQLAlchemy 2.0 ORM with SQLite and PostgreSQL support
- React 18 with Vite build tooling
- React Query for server state management
- TailwindCSS for utility-first styling
- Playwright fallback for JavaScript-heavy sites
- Pydantic data validation across all endpoints
