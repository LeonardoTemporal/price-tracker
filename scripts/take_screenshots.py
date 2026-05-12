#!/usr/bin/env python3
"""
Screenshot generator for README.md
Starts backend + frontend, creates demo data, takes screenshots via Playwright.
"""

import os
import subprocess
import sys
import time
import signal
import atexit

# Project root (parent of scripts/)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(ROOT, "frontend")
SCREENSHOTS_DIR = os.path.join(ROOT, "docs", "screenshots")

# Ensure screenshots directory exists
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

backend_proc = None
frontend_proc = None


def cleanup():
    """Terminate background processes on exit."""
    print("\nCleaning up background processes...")
    for proc, name in [(backend_proc, "backend"), (frontend_proc, "frontend")]:
        if proc and proc.poll() is None:
            print(f"  Terminating {name} (PID {proc.pid})...")
            if sys.platform == "win32":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


atexit.register(cleanup)


def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Poll URL until it responds or timeout."""
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def create_demo_data():
    """Register demo user and create sample products via API."""
    import requests

    base = "http://localhost:8000/api"

    # 1. Register demo user
    print("Creating demo user...")
    r = requests.post(f"{base}/auth/register", json={
        "email": "demo@pricetracker.dev",
        "username": "demo",
        "password": "demopass123"
    })
    if r.status_code not in (200, 201, 400):  # 400 = user already exists
        print(f"  Register warning: {r.status_code} {r.text}")

    # 2. Login
    print("Logging in...")
    r = requests.post(f"{base}/auth/login", data={
        "username": "demo",
        "password": "demopass123"
    })
    r.raise_for_status()
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create products
    print("Creating demo products...")
    products = [
        {
            "nombre": "Sony WH-1000XM5 Auriculares",
            "url": "https://www.amazon.com/dp/B09XS7JWHH",
            "precio_objetivo": 280.0,
            "tienda": "Amazon"
        },
        {
            "nombre": "MacBook Air M2 13",
            "url": "https://www.amazon.com/dp/B0B3C2R8MP",
            "precio_objetivo": 999.0,
            "tienda": "Amazon"
        },
        {
            "nombre": "Nintendo Switch OLED",
            "url": "https://www.amazon.com/dp/B098RKWHHZ",
            "precio_objetivo": 280.0,
            "tienda": "Amazon"
        }
    ]

    for p in products:
        r = requests.post(f"{base}/productos/", headers=headers, json=p)
        if r.status_code not in (200, 201):
            print(f"  Warning creating product: {r.status_code} {r.text}")

    # 4. Add price history to first product for AI prediction
    print("Adding price history for AI prediction demo...")
    r = requests.get(f"{base}/productos/", headers=headers)
    if r.status_code == 200:
        items = r.json()
        if items:
            product_id = items[0]["id"]
            # Simulate price history via direct DB or API if available
            # For now we rely on the product existing for the screenshot

    print("Demo data ready.")
    return token


def take_screenshots():
    """Use Playwright to capture UI screenshots."""
    from playwright.sync_api import sync_playwright

    print("\nTaking screenshots with Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=2
        )
        page = context.new_page()

        # --- 1. Login page ---
        print("  Screenshot 1/4: login.png")
        page.goto("http://localhost:5173/login")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "login.png"))

        # --- Login ---
        print("  Logging in via UI...")
        page.fill('input[name="username"], input[type="text"]', "demo")
        page.fill('input[name="password"], input[type="password"]', "demopass123")
        page.click('button[type="submit"]')
        page.wait_for_url("**/dashboard", wait_until="networkidle")
        page.wait_for_timeout(800)

        # --- 2. Dashboard (light) ---
        print("  Screenshot 2/4: dashboard-light.png")
        page.goto("http://localhost:5173/dashboard")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "dashboard-light.png"))

        # --- Toggle dark mode ---
        print("  Toggling dark mode...")
        # Try common selectors for theme toggle
        selectors = [
            'button[aria-label*="dark" i]',
            'button[aria-label*="theme" i]',
            'button[class*="theme" i]',
            '[data-testid="theme-toggle"]',
            'button svg[class*="moon" i]',
            'button svg[class*="sun" i]',
        ]
        for sel in selectors:
            try:
                page.click(sel, timeout=1000)
                print(f"    Dark mode toggled via: {sel}")
                break
            except Exception:
                continue
        else:
            # Fallback: try to use localStorage to set dark mode
            page.evaluate("""() => {
                localStorage.setItem('theme', 'dark');
                document.documentElement.classList.add('dark');
            }""")
            print("    Dark mode set via localStorage fallback")

        page.wait_for_timeout(800)

        # --- 3. Dashboard (dark) ---
        print("  Screenshot 3/4: dashboard-dark.png")
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "dashboard-dark.png"))

        # --- 4. Product detail ---
        print("  Screenshot 4/4: product-detail.png")
        # Navigate to first product
        page.goto("http://localhost:5173/productos")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Click first product row/link
        try:
            page.click('a[href^="/productos/"]', timeout=3000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1200)
        except Exception:
            # Direct navigation fallback
            page.goto("http://localhost:5173/productos/1")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1200)

        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "product-detail.png"))

        browser.close()

    print("All screenshots saved to docs/screenshots/")


def main():
    global backend_proc, frontend_proc

    print("=" * 50)
    print("Price Tracker Screenshot Generator")
    print("=" * 50)

    # --- Start backend ---
    print("\nStarting backend (uvicorn)...")
    backend_env = os.environ.copy()
    backend_env["DATABASE_URL"] = "sqlite:///./price_tracker_screenshots.db"
    backend_env["SECRET_KEY"] = "screenshot-demo-secret-key"
    backend_env["ALLOWED_ORIGINS"] = "http://localhost:5173"
    backend_env["PYTHONIOENCODING"] = "utf-8"

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
        env=backend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if not wait_for_service("http://127.0.0.1:8000/health", timeout=30):
        print("ERROR: Backend failed to start.")
        return 1
    print("  Backend ready at http://localhost:8000")

    # --- Start frontend ---
    print("\nStarting frontend (vite dev server)...")
    frontend_env = os.environ.copy()
    frontend_env["VITE_API_URL"] = "http://localhost:8000/api"

    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND,
        env=frontend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if not wait_for_service("http://127.0.0.1:5173", timeout=30):
        print("ERROR: Frontend failed to start.")
        return 1
    print("  Frontend ready at http://localhost:5173")

    # --- Create demo data ---
    print("\nSeeding demo data...")
    try:
        create_demo_data()
    except Exception as e:
        print(f"  Warning: demo data creation failed: {e}")

    # --- Take screenshots ---
    try:
        take_screenshots()
    except Exception as e:
        print(f"ERROR taking screenshots: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nDone! Screenshots saved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
