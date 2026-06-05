let bannerShown = false;

function getCredentialsFromForm(form) {
  const passwordInputs = form.querySelectorAll('input[type="password"]');
  if (!passwordInputs.length) return null;

  const usernameInput = form.querySelector(
    'input[type="email"], ' +
    'input[autocomplete="username"], ' +
    'input[autocomplete="email"], ' +
    'input[name*="email"], input[name*="user"], ' +
    'input[id*="email"], input[id*="user"]'
  );

  const password = passwordInputs[0].value;
  if (!password) return null;

  return {
    username: usernameInput ? usernameInput.value : '',
    password,
  };
}

function showSaveBanner(credentials, form) {
  if (bannerShown || document.getElementById('cv-banner')) return;
  bannerShown = true;

  const banner = document.createElement('div');
  banner.id = 'cv-banner';
  banner.style.cssText = [
    'position:fixed', 'top:20px', 'right:20px', 'z-index:2147483647',
    'background:#1e293b', 'color:#e2e8f0',
    'padding:16px 18px', 'border-radius:12px',
    'box-shadow:0 8px 32px rgba(0,0,0,0.5)',
    'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
    'font-size:14px', 'width:310px',
    'border:1px solid #334155',
    'transition:opacity 0.3s ease',
  ].join(';');

  banner.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
      <div style="width:34px;height:34px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🔐</div>
      <div style="flex:1;">
        <div style="font-weight:600;font-size:14px;">Save to CyberVault?</div>
        <div style="color:#64748b;font-size:12px;margin-top:1px;">${location.hostname}</div>
      </div>
      <div id="cv-close" style="cursor:pointer;color:#64748b;font-size:20px;line-height:1;padding:4px;">&times;</div>
    </div>
    <div style="background:#0f172a;border-radius:8px;padding:10px 12px;margin-bottom:12px;font-size:12px;color:#94a3b8;">
      Username: <span style="color:#e2e8f0;font-weight:500;">${credentials.username || '(not detected)'}</span>
    </div>
    <div style="display:flex;gap:8px;">
      <button id="cv-save" style="flex:1;background:#3b82f6;color:#fff;border:none;border-radius:8px;padding:9px;font-size:13px;font-weight:600;cursor:pointer;">Save Password</button>
      <button id="cv-skip" style="background:#1e293b;color:#64748b;border:1px solid #334155;border-radius:8px;padding:9px 12px;font-size:13px;cursor:pointer;">Skip</button>
    </div>
    <div id="cv-msg" style="margin-top:10px;font-size:12px;text-align:center;min-height:16px;"></div>
  `;

  document.body.appendChild(banner);

  const msg = document.getElementById('cv-msg');

  function continueSubmit() {
    banner.remove();
    bannerShown = false;
    if (form) {
      // Submit without triggering our listener again
      const realSubmit = HTMLFormElement.prototype.submit;
      realSubmit.call(form);
    }
  }

  document.getElementById('cv-close').addEventListener('click', continueSubmit);

  document.getElementById('cv-skip').addEventListener('click', continueSubmit);

  document.getElementById('cv-save').addEventListener('click', () => {
    const btn = document.getElementById('cv-save');
    btn.textContent = 'Saving…';
    btn.disabled = true;

    chrome.runtime.sendMessage({
      action: 'saveCredential',
      siteUrl: location.href,
      username: credentials.username,
      password: credentials.password,
    }, response => {
      if (response && response.success) {
        msg.style.color = '#22c55e';
        msg.textContent = '✓ Saved! Continuing…';
        setTimeout(continueSubmit, 1500);
      } else if (response && response.error === 'Not logged in') {
        msg.style.color = '#f59e0b';
        msg.textContent = '⚠ Open the CyberVault extension icon and log in first.';
        btn.textContent = 'Save Password';
        btn.disabled = false;
      } else {
        msg.style.color = '#f87171';
        msg.textContent = '✕ ' + (response?.error || 'Save failed — check extension login.');
        btn.textContent = 'Save Password';
        btn.disabled = false;
      }
    });
  });
}

// Intercept form submissions with password fields
document.addEventListener('submit', e => {
  const credentials = getCredentialsFromForm(e.target);
  if (credentials && !bannerShown) {
    e.preventDefault();
    e.stopImmediatePropagation();
    showSaveBanner(credentials, e.target);
  }
}, true);
