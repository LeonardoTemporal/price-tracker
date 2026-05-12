# Pricy Price Tracker

> **Open-source price tracking system with multi-user authentication, responsive design, and intelligent alerts.**
> Perfect as a **starter kit** for building monitoring systems, learning modern full-stack architecture, or deploying your own price tracking service.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

A professional, full-stack price tracking application built with **FastAPI** and **React**. Track product prices across multiple e-commerce sites, visualize price history with interactive charts, and receive alerts when products hit your target price.

Perfect as a **starter kit** for building monitoring systems, learning modern full-stack architecture, or deploying your own price tracking service.

---

## Features

### Authentication & Security
- Multi-user registration and login with JWT tokens
- Secure password hashing with bcrypt
- Persistent sessions with localStorage tokens
- Route-level authentication middleware
- Data isolation: each user only sees their own products

### Interactive Dashboard
- Real-time price evolution charts with Recharts
- Summary cards: total products, active alerts, potential savings
- Recent products with quick access
- Mobile-optimized responsive layout

### Smart Price Tracking
- Multi-site scraping (Mercado Libre, Amazon, eBay + generic fallback)
- URL testing before adding products
- Automatic price updates with one click
- Complete price history table
- Target price alerts

### Modern UI/UX
- TailwindCSS utility-first responsive design
- Mobile hamburger navigation
- Touch-optimized buttons (44px minimum)
- Clean, modern interface

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/LeonardoTemporal/price-tracker.git
cd price-tracker

# Run the setup script (Windows)
start-all.bat

# Or manual steps:
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
playwright install chromium
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal:
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---

## Architecture

```
price-tracker/
├── backend/              # FastAPI REST API
│   ├── app/
│   │   ├── main.py       # FastAPI app with CORS
│   │   ├── database.py   # SQLAlchemy models
│   │   ├── security.py   # JWT & bcrypt auth
│   │   └── routers/      # REST endpoints
│   │       ├── auth.py
│   │       └── productos.py
│   └── tests/            # Automated tests
├── frontend/             # React SPA
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── contexts/     # AuthContext
│   │   ├── services/     # Axios API client
│   │   └── App.jsx
│   └── tests/
├── src/                  # Shared scraping logic
│   ├── scraper.py        # Multi-strategy web scraper
│   ├── tracker.py        # Tracking orchestrator
│   └── database.py
└── README.md
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI 0.104, Python 3.8+, SQLAlchemy 2.0, JWT, bcrypt |
| **Frontend** | React 18, Vite 5, TailwindCSS 3, React Query, Recharts |
| **Scraping** | BeautifulSoup4, Playwright, requests |
| **Database** | SQLite (dev) / PostgreSQL (production-ready) |
| **Testing** | pytest |

---

## Supported Sites

| Site | Status | Method |
|------|--------|--------|
| **Mercado Libre** | Fully supported | API + Playwright fallback |
| **Amazon** | Supported | Multi-selector extraction |
| **eBay** | Supported | Domain-specific config |
| **Generic sites** | Most sites work | Pattern-based fallback |

---

## Contributing

We welcome contributions of all kinds. Whether it is a bug fix, new feature, or documentation improvement, your help is appreciated.

Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request.

### Quick Contributing Steps
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

---

## Acknowledgments

- Built with passion for modern web development and automation
- Inspired by the need for transparent price monitoring tools
- Thanks to all contributors and the open source community

---

## Contact

- **Author**: Leonardo Temporal
- **Email**: pricy.pricetracker@gmail.com
- **GitHub**: [@LeonardoTemporal](https://github.com/LeonardoTemporal)

---

## Star History

If you find this project useful, please consider giving it a star. It helps others discover the project and motivates continued development.

[![Star History Chart](https://api.star-history.com/svg?repos=LeonardoTemporal/price-tracker&type=Date)](https://star-history.com/#LeonardoTemporal/price-tracker&Date)
