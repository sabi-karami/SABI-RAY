'''Playwright assertions; screenshots contain only synthetic CI data.'''
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_browser(base,user,password):
    Path('test-artifacts').mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000},locale='fa-IR')
        errors=[]
        page.on('pageerror',lambda error:errors.append(type(error).__name__))
        page.goto(base+'/dashboard/');page.wait_for_load_state('networkidle')
        assert 'SABI-RAY' in page.title()
        assert page.locator('input[name="username"]').count()==1
        assert page.locator('input[name="password"]').count()==1
        page.screenshot(path='test-artifacts/login-desktop.png',full_page=True)
        page.locator('input[name="username"]').fill(user)
        page.locator('input[name="password"]').fill(password)
        page.locator('form button[type="submit"]').click()
        page.locator('input[name="username"]').wait_for(state='detached',timeout=30000)
        page.wait_for_load_state('networkidle')
        page.screenshot(path='test-artifacts/dashboard-desktop.png',full_page=True)
        page.goto(base+'/statics/sabi-ray/protocols.html');page.wait_for_load_state('networkidle')
        assert page.locator('.item').count()==9
        page.locator('#search').fill('trojan');assert page.locator('.item').count()==1
        assert 'q=trojan' in page.url
        page.reload();page.wait_for_load_state('networkidle');assert page.locator('.item').count()==1
        page.locator('#search').fill('');page.locator('#kind').select_option('manual');assert page.locator('.item').count()==4
        page.locator('#kind').select_option('all')
        page.screenshot(path='test-artifacts/protocols-desktop.png',full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path='test-artifacts/protocols-mobile.png',full_page=True)
        assert not errors,'JavaScript runtime errors'
        browser.close()
    print('PASS: browser login, authenticated dashboard, protocol filters, URL/reload state, mobile overflow, no JS runtime errors.')
