"""Optional full browser check: requires Playwright and Chromium. External services are blocked."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright, expect
import shutil
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
origin=f'http://127.0.0.1:{server.server_port}'
errors=[];bad=[];checked=0
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True)
  context=browser.new_context(viewport={'width':1440,'height':1000})
  context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin) else route.abort())
  page=context.new_page()
  page.on('pageerror',lambda e:errors.append((page.url,str(e))))
  page.on('response',lambda r:bad.append((r.url,r.status)) if r.url.startswith(origin) and r.status>=400 else None)
  paths=[x for x in sorted(ROOT.rglob('*.html')) if x.name not in ['nav.html','footer.html']]
  for path in paths:
   route='/'+path.relative_to(ROOT).as_posix()
   page.goto(origin+route,wait_until='load')
   if path.name!='thanks.html':
    expect(page.locator('#navbar header')).to_be_visible()
    expect(page.locator('#header-lang-selector .th-lang-toggle')).to_be_visible()
   if page.locator('#footer').count():expect(page.locator('#footer .donation-section')).to_be_attached()
   page.wait_for_timeout(30)
   checked+=1
  print('Loaded pages:',checked,flush=True)
  assert not errors,errors
  assert not bad,bad
  page.goto(origin+'/html/tips.html?view=all#hero',wait_until='load')
  page.locator('.th-lang-toggle').click()
  page.locator('.th-lang-option[data-lang="ja"]').click()
  page.wait_for_url('**/ja/html/tips.html?view=all#hero')
  expect(page.locator('.th-lang-toggle')).to_be_visible()
  assert page.evaluate('localStorage.getItem("topheroes-lang")')=='ja'
  page.locator('.th-lang-toggle').focus();page.keyboard.press('ArrowDown')
  expect(page.locator('.th-lang-menu')).to_be_visible()
  page.keyboard.press('Escape')
  expect(page.locator('.th-lang-toggle')).to_have_attribute('aria-expanded','false')
  page.goto(origin+'/ko/html/tips.html',wait_until='load')
  for value in ['108','1107','older']:
   # Use the actual option values supplied by the official English table.
   if page.locator(f'#castle-switch option[value="{value}"]').count():
    page.locator('#castle-switch').select_option(value)
    expect(page.locator('#wrap-castle-'+value)).to_be_visible()
  for tab in page.locator('.th-tab').all():
   tab.click();target=tab.get_attribute('data-target')
   expect(page.locator('#wrap-'+target)).to_have_class('th-wrap th-visible')
  for section in ['troopskin','rune','pet','villager']:
   expect(page.locator('#'+section)).to_be_attached()
  page.goto(origin+'/tc/html/quick-tips.html',wait_until='load')
  for button in page.locator('.faq-toggle').all():
   button.click();expect(button).to_have_attribute('aria-expanded','true')
   button.click();expect(button).to_have_attribute('aria-expanded','false')
  page.goto(origin+'/',wait_until='load')
  mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
  mobile.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin) else route.abort())
  m=mobile.new_page();m.on('pageerror',lambda e:errors.append((m.url,str(e))));m.goto(origin+'/',wait_until='load')
  heroes=m.locator('nav li.has-sub').first
  heroes.locator(':scope > a').tap()
  expect(heroes.locator(':scope > .dropdown')).to_be_visible()
  heroes.locator('.flyout-toggle').tap()
  expect(heroes.locator('.flyout')).to_be_visible()
  m.locator('.site-title').tap()
  expect(heroes.locator(':scope > .dropdown')).not_to_be_visible()
  assert m.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'mobile horizontal overflow'
  # Storage restrictions must not prevent a language change.
  isolated=browser.new_context()
  isolated.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin) else route.abort())
  isolated.add_init_script("Object.defineProperty(window, 'localStorage', {get() {throw new DOMException('Blocked', 'SecurityError');}})")
  q=isolated.new_page();q.on('pageerror',lambda e:errors.append((q.url,str(e))));q.goto(origin+'/html/heroes.html?test=1#shards',wait_until='load')
  q.locator('.th-lang-toggle').click();q.locator('.th-lang-option[data-lang="de"]').click()
  q.wait_for_url('**/de/html/heroes.html?test=1#shards')
  assert not errors,errors
  assert not bad,bad
  print('PASS: desktop/mobile menus, flyouts, keyboard, language switching with query/hash and blocked storage, tabs and FAQ toggles.',flush=True)
  browser.close()
finally:
 server.shutdown();server.server_close()
