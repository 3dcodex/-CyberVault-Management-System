const app = document.getElementById('app');

const VAULT_URL = 'https://cybervault-management-system-production.up.railway.app/accounts/dashboard/';

function renderLogin(errorMsg) {
  app.innerHTML = `
    <div class="header">
      <div class="logo">🔐</div>
      <div class="header-text">
        <h1>CyberVault</h1>
        <p>Password Manager</p>
      </div>
    </div>
    <div class="content">
      <div class="form-group">
        <label>Username</label>
        <input type="text" id="cv-username" placeholder="Enter username" autocomplete="off">
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" id="cv-password" placeholder="Enter password">
      </div>
      <button class="btn btn-primary" id="cv-login">Sign In</button>
      ${errorMsg ? `<div class="error">${errorMsg}</div>` : ''}
    </div>
  `;

  const loginBtn = document.getElementById('cv-login');

  function doLogin() {
    const username = document.getElementById('cv-username').value.trim();
    const password = document.getElementById('cv-password').value;
    if (!username || !password) {
      renderLogin('Please enter username and password.');
      return;
    }
    loginBtn.textContent = 'Signing in…';
    loginBtn.disabled = true;
    chrome.runtime.sendMessage({ action: 'login', username, password }, response => {
      if (response && response.success) {
        renderConnected(response.username);
      } else {
        renderLogin(response?.error || 'Login failed. Try again.');
      }
    });
  }

  loginBtn.addEventListener('click', doLogin);
  document.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); }, { once: true });

  document.getElementById('cv-username').focus();
}

function renderConnected(username) {
  app.innerHTML = `
    <div class="header">
      <div class="logo">🔐</div>
      <div class="header-text">
        <h1>CyberVault</h1>
        <p>Password Manager</p>
      </div>
    </div>
    <div class="content">
      <div class="status-card">
        <div class="dot"></div>
        <div>
          <div class="status-name">${username}</div>
          <div class="status-sub">Connected · Extension active</div>
        </div>
      </div>
      <button class="btn btn-primary" id="cv-open">Open Vault</button>
      <button class="btn btn-secondary" id="cv-logout">Sign Out</button>
    </div>
  `;

  document.getElementById('cv-open').addEventListener('click', () => {
    chrome.tabs.create({ url: VAULT_URL });
  });

  document.getElementById('cv-logout').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'logout' }, () => renderLogin());
  });
}

// Check login status when popup opens
chrome.runtime.sendMessage({ action: 'getStatus' }, response => {
  if (response && response.loggedIn) {
    renderConnected(response.username);
  } else {
    renderLogin();
  }
});
