const APP_API_BASE_URL = (() => {
  const configured =
    window.__APP_CONFIG__?.apiBaseUrl ||
    window.NEXT_PUBLIC_API_URL ||
    'http://localhost:8000';

  return String(configured || 'http://localhost:8000').replace(/\/$/, '');
})();

function getErrorMessage(payload) {
  if (typeof payload === 'string') {
    return payload;
  }

  if (payload?.detail) {
    if (Array.isArray(payload.detail)) {
      return payload.detail.map((item) => item?.msg || item).join(' ');
    }
    return payload.detail;
  }

  if (payload?.message) {
    return payload.message;
  }

  return 'The request failed.';
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${APP_API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  let payload = null;
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    throw new Error(getErrorMessage(payload));
  }

  return payload;
}
