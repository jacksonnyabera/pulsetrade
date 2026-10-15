const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

let refreshing: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  const refresh = localStorage.getItem("pulsetrade_refresh_token");
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem("pulsetrade_access_token", data.access_token);
    localStorage.setItem("pulsetrade_refresh_token", data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function apiFetch(path: string, options: RequestInit = {}, retried = false): Promise<any> {
  const isBrowser = typeof window !== "undefined";
  const token = isBrowser ? localStorage.getItem("pulsetrade_access_token") : null;

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (res.status === 401 && !retried && isBrowser && !path.includes("/auth/login")) {
    refreshing = refreshing ?? refreshAccessToken().finally(() => (refreshing = null));
    if (await refreshing) return apiFetch(path, options, true);
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}