# Claude for Open Source - Application

## Narrative

I am the primary maintainer and architect of Pricy Price Tracker, an open-source intelligent monitoring platform. It serves as foundational infrastructure for developers building price tracking, alerting, and prediction systems.

The project is distinguished by its native Model Context Protocol (MCP) Server integration — allowing Claude Code and compatible AI tools to interact directly with the platform via structured tools for querying prices, managing products, checking alerts, and running predictions. This expands the MCP ecosystem into the monitoring and e-commerce space.

Key technical components:
- MCP Server with 6 exposed tools
- AI Price Prediction engine using linear regression with confidence scoring
- Full-stack architecture: FastAPI + React 18 + JWT auth + SQLAlchemy 2.0
- Production deployment: Multi-stage Docker builds, Dokploy orchestration, PostgreSQL
- Quality: 24+ automated tests, GitHub Actions CI/CD, MIT License
- Developer experience: Dark mode, PWA support, comprehensive documentation

I actively maintain the project with regular releases, review contributions within 24 hours, and continuously expand the platform.

Repository: https://github.com/LeonardoTemporal/price-tracker
