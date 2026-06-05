const API_BASE = 'https://cybervault-management-system-production.up.railway.app/api';

async function getToken() {
  return new Promise(resolve => {
    chrome.storage.local.get('cvToken', data => resolve(data.cvToken || null));
  });
}

async function apiLogin(username, password) {
  try {
    const res = await fetch(`${API_BASE}/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (res.ok) {
      await chrome.storage.local.set({ cvToken: data.token, cvUsername: data.username });
      return { success: true, username: data.username };
    }
    return { success: false, error: data.error };
  } catch {
    return { success: false, error: 'Cannot reach CyberVault server.' };
  }
}

async function apiLogout() {
  const token = await getToken();
  if (token) {
    try {
      await fetch(`${API_BASE}/logout/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${token}` },
      });
    } catch {}
  }
  await chrome.storage.local.remove(['cvToken', 'cvUsername']);
}

async function apiSaveCredential(siteUrl, username, password) {
  const token = await getToken();
  if (!token) return { success: false, error: 'Not logged in' };
  try {
    let siteName = siteUrl;
    try { siteName = new URL(siteUrl).hostname; } catch {}
    const res = await fetch(`${API_BASE}/vault/save/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`,
      },
      body: JSON.stringify({ site_name: siteName, username, password }),
    });
    const data = await res.json();
    return res.ok ? { success: true } : { success: false, error: data.error };
  } catch {
    return { success: false, error: 'Cannot reach CyberVault server.' };
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'login') {
    apiLogin(msg.username, msg.password).then(sendResponse);
    return true;
  }
  if (msg.action === 'logout') {
    apiLogout().then(() => sendResponse({ success: true }));
    return true;
  }
  if (msg.action === 'saveCredential') {
    apiSaveCredential(msg.siteUrl, msg.username, msg.password).then(sendResponse);
    return true;
  }
  if (msg.action === 'getStatus') {
    chrome.storage.local.get(['cvToken', 'cvUsername'], data => {
      sendResponse({ loggedIn: !!data.cvToken, username: data.cvUsername || '' });
    });
    return true;
  }
});
