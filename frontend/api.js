const APP_API_BASE_URL = (() => {
  const configured =
    window.APP_CONFIG?.apiBaseUrl || window.NEXT_PUBLIC_API_URL;

  return String(
    configured || "https://pulse-ai-interview-backend.onrender.com",
  ).replace(/\/$/, "");
})();

function getErrorMessage(payload) {
  if (typeof payload === "string") {
    return payload;
  }

  if (payload?.detail) {
    if (Array.isArray(payload.detail)) {
      return payload.detail.map((item) => item?.msg || item).join(" ");
    }

    return payload.detail;
  }

  if (payload?.message) {
    return payload.message;
  }

  return "The request failed.";
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${APP_API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  let payload = null;

  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    throw new Error(getErrorMessage(payload));
  }

  return payload;
}
