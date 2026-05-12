import os
import requests
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

base = "http://localhost:8000/api"

# 1. Register demo user
print("Creating demo user...")
r = requests.post(f"{base}/auth/register", json={
    "email": "demo@pricetracker.dev",
    "username": "demo",
    "password": "demopass123"
})
print(f"  Register: {r.status_code}")

# 2. Login via API to get token
print("Logging in via API...")
r = requests.post(f"{base}/auth/login", data={
    "username": "demo",
    "password": "demopass123"
})
r.raise_for_status()
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("  Logged in, token acquired")

# 3. Create products
print("Creating demo products...")
products = [
    {"nombre": "Sony WH-1000XM5 Auriculares", "url": "https://www.amazon.com/dp/B09XS7JWHH", "precio_objetivo": 280.0, "tienda": "Amazon"},
    {"nombre": "MacBook Air M2 13", "url": "https://www.amazon.com/dp/B0B3C2R8MP", "precio_objetivo": 999.0, "tienda": "Amazon"},
    {"nombre": "Nintendo Switch OLED", "url": "https://www.amazon.com/dp/B098RKWHHZ", "precio_objetivo": 280.0, "tienda": "Amazon"},
]
for p in products:
    r = requests.post(f"{base}/productos/", headers=headers, json=p)
    print(f"  Product {p['nombre'][:20]}: {r.status_code}")

# 4. Take screenshots
print("\nTaking screenshots with Playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()

    def wait_for_auth_and_content():
        """Wait for auth spinner to appear then disappear, then content to load."""
        # Wait for spinner to appear (React mounts and AuthContext starts checkAuth)
        try:
            page.wait_for_selector('text=Cargando...', state='visible', timeout=10000)
        except Exception:
            pass
        # Wait for spinner to disappear (auth check complete)
        try:
            page.wait_for_selector('text=Cargando...', state='hidden', timeout=15000)
        except Exception:
            pass
        # Wait for dashboard data fetch to complete
        try:
            page.wait_for_selector('.animate-spin', state='hidden', timeout=15000)
        except Exception:
            pass
        # Wait for actual dashboard content
        try:
            page.wait_for_selector('h1:has-text("Dashboard")', timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(800)

    # Screenshot 1: Login page
    print("  1/4: login.png")
    page.goto("http://localhost:5173/login")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "login.png"))

    # Inject token and navigate to dashboard
    print("  Injecting auth token and navigating to dashboard...")
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.goto("http://localhost:5173/dashboard")
    page.wait_for_load_state("domcontentloaded")
    wait_for_auth_and_content()

    # Screenshot 2: Dashboard light
    print("  2/4: dashboard-light.png")
    page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "dashboard-light.png"))

    # Toggle dark mode
    print("  Toggling dark mode...")
    page.evaluate("""() => {
        localStorage.setItem('theme', 'dark');
        document.documentElement.classList.add('dark');
    }""")
    page.wait_for_timeout(500)

    # Screenshot 3: Dashboard dark
    print("  3/4: dashboard-dark.png")
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    wait_for_auth_and_content()
    page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "dashboard-dark.png"))

    # Screenshot 4: Product detail
    print("  4/4: product-detail.png")
    page.goto("http://localhost:5173/productos")
    page.wait_for_load_state("domcontentloaded")
    wait_for_auth_and_content()
    page.wait_for_timeout(500)
    try:
        page.locator('a[href^="/productos/"]').first.click(timeout=3000)
        page.wait_for_load_state("domcontentloaded")
        # Wait for product detail to load
        page.wait_for_timeout(1500)
        try:
            page.wait_for_selector('text=Cargando...', state='visible', timeout=5000)
        except Exception:
            pass
        try:
            page.wait_for_selector('text=Cargando...', state='hidden', timeout=10000)
        except Exception:
            pass
        try:
            page.wait_for_selector('h1:has-text("$")', timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(1000)
    except Exception:
        page.goto("http://localhost:5173/productos/1")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)
        try:
            page.wait_for_selector('text=Cargando...', state='visible', timeout=5000)
        except Exception:
            pass
        try:
            page.wait_for_selector('text=Cargando...', state='hidden', timeout=10000)
        except Exception:
            pass
        try:
            page.wait_for_selector('h1:has-text("$")', timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "product-detail.png"))

    browser.close()

print("\nAll screenshots saved to docs/screenshots/")
