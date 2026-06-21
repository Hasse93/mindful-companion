// Client-side auth: JWT stored in localStorage, with a change event so the
// AuthGate re-renders on login/logout.
import { API_URL } from "@/lib/api";

const TOKEN_KEY = "mc_token";
const EVENT = "mc-auth-change";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  window.dispatchEvent(new Event(EVENT));
}

export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event(EVENT));
}

export function onAuthChange(cb: () => void): () => void {
  window.addEventListener(EVENT, cb);
  return () => window.removeEventListener(EVENT, cb);
}

export async function register(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? "Registration failed");
  }
}

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? "Login failed");
  }
  const data = await res.json();
  setToken(data.access_token);
}
