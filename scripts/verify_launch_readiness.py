"""
MarketLab AI — Automated Design Quality Enforcement & Launch Readiness Gate
Audits the repository against non-negotiable design rules, financial credibility standards,
and mandatory launch requirements.
"""

import os
import sys
import re
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"

class GateFailure(Exception):
    pass

def log_section(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def check_no_purple():
    print("[CHECK 1] Scanning frontend for prohibited purple tokens and gradients...")
    purple_regex = re.compile(r"(purple-|from-purple|to-purple|via-purple|#A855F7|#9333ea|#7e22ce|#c084fc)", re.IGNORECASE)
    violations = []

    for ext in ("*.tsx", "*.ts", "*.css", "*.html"):
        for path in FRONTEND_DIR.rglob(ext):
            if "node_modules" in path.parts or "dist" in path.parts:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(content.splitlines(), start=1):
                if purple_regex.search(line):
                    violations.append(f"{path.relative_to(ROOT_DIR)}:{line_no} -> {line.strip()}")

    if violations:
        for v in violations:
            print(f"  FAIL: {v}")
        raise GateFailure(f"Found {len(violations)} prohibited purple references in frontend source.")
    print("  PASS: Zero purple tokens or gradients detected.")

def check_no_em_dashes():
    print("[CHECK 2] Scanning website copy for prohibited em dashes (—)...")
    em_dash_char = "\u2014"
    violations = []

    for ext in ("*.tsx", "*.ts", "*.html"):
        for path in (FRONTEND_DIR / "src").rglob(ext):
            content = path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(content.splitlines(), start=1):
                if em_dash_char in line:
                    violations.append(f"{path.relative_to(ROOT_DIR)}:{line_no} -> {line.strip()}")

    index_html = FRONTEND_DIR / "index.html"
    if index_html.is_file():
        content = index_html.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(content.splitlines(), start=1):
            if em_dash_char in line:
                violations.append(f"{index_html.relative_to(ROOT_DIR)}:{line_no} -> {line.strip()}")

    if violations:
        for v in violations:
            print(f"  FAIL: {v}")
        raise GateFailure(f"Found {len(violations)} prohibited em dashes in website copy.")
    print("  PASS: Zero em dashes in website copy.")

def check_no_emojis_in_icons():
    print("[CHECK 3] Scanning components for emoji interface icons...")
    # Emojis in range U+1F300-1F9FF, U+2600-26FF, U+2700-27BF
    emoji_regex = re.compile(r"[\U0001F300-\U0001F9FF\U00002600-\U000026FF\U00002700-\U000027BF]")
    violations = []

    for path in (FRONTEND_DIR / "src").rglob("*.tsx"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(content.splitlines(), start=1):
            # Exclude code comments or standard ASCII
            if emoji_regex.search(line):
                violations.append(f"{path.relative_to(ROOT_DIR)}:{line_no} -> {line.strip()}")

    if violations:
        for v in violations:
            print(f"  FAIL: {v}")
        raise GateFailure(f"Found {len(violations)} emoji characters in interface components.")
    print("  PASS: Zero emoji interface icons detected.")

def check_no_pill_buttons():
    print("[CHECK 4] Scanning buttons and badge containers for unapproved pill shapes...")
    violations = []
    # Button or span badge with rounded-full
    pill_badge_btn = re.compile(r"<(button|span|div)[^>]*className=[\"'][^\"']*\brounded-full\b[^\"']*(px-[2-9]|py-[1-9]|text-|btn)[^\"']*[\"']", re.IGNORECASE)

    for path in (FRONTEND_DIR / "src").rglob("*.tsx"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(content.splitlines(), start=1):
            # Status indicator dots like `w-2 h-2 rounded-full` or ping rings are allowed, but badge pills/buttons are prohibited
            if pill_badge_btn.search(line) and not ("w-1.5 h-1.5" in line or "w-2 h-2" in line or "w-3 h-1" in line or "animate-ping" in line):
                violations.append(f"{path.relative_to(ROOT_DIR)}:{line_no} -> {line.strip()}")

    if violations:
        for v in violations:
            print(f"  FAIL: {v}")
        raise GateFailure(f"Found {len(violations)} unapproved pill-shaped buttons/badges.")
    print("  PASS: Restrained rectangular button and badge radii enforced.")

def check_favicon_and_identity():
    print("[CHECK 5] Verifying favicon assets and HTML references...")
    svg_favicon = FRONTEND_DIR / "public" / "favicon.svg"
    if not svg_favicon.is_file():
        raise GateFailure("Missing public/favicon.svg asset.")
    
    index_html = FRONTEND_DIR / "index.html"
    content = index_html.read_text(encoding="utf-8")
    if 'rel="icon"' not in content or "favicon.svg" not in content:
        raise GateFailure("index.html does not link to favicon.svg.")
    
    if "JetBrains Mono" not in content:
        raise GateFailure("index.html does not include monospaced font reference.")
    print("  PASS: Obsidian Gold favicon and font metadata verified.")

def check_legal_pages_and_navigation():
    print("[CHECK 6] Verifying dedicated Privacy Policy, Terms, and Footer links...")
    privacy_page = FRONTEND_DIR / "src" / "pages" / "PrivacyPolicyPage.tsx"
    terms_page = FRONTEND_DIR / "src" / "pages" / "TermsPage.tsx"
    footer = FRONTEND_DIR / "src" / "components" / "Footer.tsx"
    app_tsx = FRONTEND_DIR / "src" / "App.tsx"

    if not privacy_page.is_file():
        raise GateFailure("Missing PrivacyPolicyPage.tsx.")
    if not terms_page.is_file():
        raise GateFailure("Missing TermsPage.tsx.")
    if not footer.is_file():
        raise GateFailure("Missing Footer.tsx.")

    app_content = app_tsx.read_text(encoding="utf-8")
    if "PrivacyPolicyPage" not in app_content or "TermsPage" not in app_content:
        raise GateFailure("App.tsx does not route PrivacyPolicyPage and TermsPage.")
    if "<Footer" not in app_content:
        raise GateFailure("App.tsx does not render persistent Footer component.")

    footer_content = footer.read_text(encoding="utf-8")
    if "Privacy Policy" not in footer_content or "Terms and Conditions" not in footer_content:
        raise GateFailure("Footer does not contain verified Privacy and Terms navigation.")
    print("  PASS: Independent Privacy Policy and Terms and Conditions pages active and linked.")

def check_security_production_gate():
    print("[CHECK 7] Verifying backend production API security enforcement...")
    security_file = BACKEND_DIR / "app" / "core" / "security.py"
    content = security_file.read_text(encoding="utf-8")
    if 'settings.APP_ENV == "production" and not settings.API_KEY_ENABLED' not in content:
        raise GateFailure("security.py does not enforce API_KEY_ENABLED in production mode.")
    print("  PASS: Production API key enforcement verified.")

def check_market_data_truthfulness():
    print("[CHECK 8] Verifying market data latency classification...")
    schema_file = BACKEND_DIR / "app" / "schemas" / "market_data.py"
    service_file = BACKEND_DIR / "app" / "services" / "market_data_service.py"
    
    schema_content = schema_file.read_text(encoding="utf-8")
    if "daily_historical" not in schema_content:
        raise GateFailure("market_data.py schema does not define daily_historical latency classification.")
    
    service_content = service_file.read_text(encoding="utf-8")
    if 'latency_type = "daily_historical"' not in service_content:
        raise GateFailure("market_data_service.py does not classify yfinance as daily_historical.")
    print("  PASS: Historical daily candles truthfully classified as daily_historical.")

def run_backend_tests():
    print("[CHECK 9] Executing backend test suite...")
    env = os.environ.copy()
    env["DISABLE_SQLALCHEMY_CEXT"] = "1"
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-W", "ignore::pydantic.warnings.PydanticDeprecatedSince20"]
    ret = subprocess.call(cmd, cwd=str(BACKEND_DIR), env=env)
    if ret != 0:
        raise GateFailure("Backend test suite reported failures.")
    print("  PASS: All backend tests passed.")

def run_frontend_build():
    print("[CHECK 10] Executing frontend production build (TypeScript + Vite)...")
    cmd = ["npm.cmd" if os.name == "nt" else "npm", "run", "build"]
    ret = subprocess.call(cmd, cwd=str(FRONTEND_DIR))
    if ret != 0:
        raise GateFailure("Frontend production build failed.")
    print("  PASS: Frontend compiled cleanly into production bundle.")

def main():
    log_section("MarketLab AI — Launch Readiness Quality Gate")
    try:
        check_no_purple()
        check_no_em_dashes()
        check_no_emojis_in_icons()
        check_no_pill_buttons()
        check_favicon_and_identity()
        check_legal_pages_and_navigation()
        check_security_production_gate()
        check_market_data_truthfulness()
        run_backend_tests()
        run_frontend_build()

        log_section("LAUNCH READINESS GATE: ALL 10 GATES PASSED")
        print("\nAll non-negotiable design rules, financial credibility standards,")
        print("legal disclosures, test suites, and production builds are VERIFIED.\n")
        sys.exit(0)
    except GateFailure as e:
        log_section(f"GATE BLOCKED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
