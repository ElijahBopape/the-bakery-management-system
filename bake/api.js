// The Bakery — connection to the backend API (the FastAPI server in backend/)
// Every page that talks to the server loads this file before its own scripts.
// It follows the team's "How to Connect to the Backend API" guide.

// 1. Server address. To switch servers you only change this ONE line.
const API_BASE = "https://the-bakery-api-production.up.railway.app";
// const API_BASE = "http://localhost:8000"; // local backend: cd backend, then uvicorn main:app --reload

(function () {
  "use strict";

  const TOKEN_KEY = "token";      // same localStorage key as the guide (and the app wireframe)
  const USER_KEY = "bakery-user"; // saved profile, so pages can show the name straight away
  const TIMEOUT_MS = 20000;       // the server can take a few seconds to wake up

  class ApiError extends Error {
    constructor(message, status) {
      super(message);
      this.status = status; // 0 = no answer from the server
    }
  }

  // ---- Saved sign-in (localStorage can be blocked, so every access is wrapped) ----
  function getToken() {
    try { return localStorage.getItem(TOKEN_KEY); } catch (e) { return null; }
  }
  function getUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch (e) { return null; }
  }
  function saveSession(token, user) {
    try {
      if (token) localStorage.setItem(TOKEN_KEY, token);
      if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch (e) {}
    updateAccountLinks();
  }
  function clearSession() {
    try { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); } catch (e) {}
    updateAccountLinks();
  }

  // FastAPI sends errors as { "detail": "message" } or, for form mistakes, a list
  function errorMessage(data, status) {
    const detail = data && data.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length) {
      const first = detail[0];
      const field = Array.isArray(first.loc) ? first.loc[first.loc.length - 1] : "";
      return (field ? field + ": " : "") + first.msg;
    }
    return "Something went wrong (error " + status + "). Please try again.";
  }

  // 2. Request helper: adds the token, and turns failures into readable messages.
  //    Use it for every call:  await api("/products")
  async function api(path, options = {}) {
    const token = getToken();
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    let res;
    try {
      res = await fetch(API_BASE + path, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: "Bearer " + token } : {}),
          ...options.headers,
        },
      });
    } catch (err) {
      throw new ApiError(
        err.name === "AbortError"
          ? "The server is taking too long to answer. Please try again."
          : "Can't reach the bakery server. Check your internet connection and try again.",
        0
      );
    } finally {
      clearTimeout(timer);
    }

    if (res.status === 204) return null; // e.g. after a DELETE
    let data = null;
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) {
      if (res.status === 401) clearSession(); // token expired or no longer valid
      throw new ApiError(errorMessage(data, res.status), res.status);
    }
    return data;
  }

  // 3. Sign in / create account / sign out
  async function login(email, password) {
    const data = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    saveSession(data.access_token, data.user);
    return data.user;
  }
  async function register(details) {
    const data = await api("/auth/register", { method: "POST", body: JSON.stringify(details) });
    saveSession(data.access_token, data.user);
    return data.user;
  }
  function logout() {
    clearSession();
  }

  // 4. SSO: is the saved token still valid? Returns the user, or null if signed out.
  //    Throws only when the server can't be reached (so pages can say so).
  async function sso() {
    if (!getToken()) return null;
    try {
      const user = await api("/auth/sso");
      saveSession(null, user);
      return user;
    } catch (err) {
      if (err.status === 401 || err.status === 403) { clearSession(); return null; }
      throw err;
    }
  }

  // ---- Small shared helpers ----
  function formatPrice(value) {
    const n = Number(value) || 0;
    return "R" + (Number.isInteger(n) ? n : n.toFixed(2));
  }
  // The server sends UTC times without a "Z" on the end, so add it before converting
  function formatDate(value) {
    if (!value) return "";
    const iso = /[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : value + "Z";
    const date = new Date(iso);
    return isNaN(date) ? value : date.toLocaleString("en-ZA", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
  }
  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
  }

  // The account icon in the navbar shows whether someone is signed in
  function updateAccountLinks() {
    const user = getToken() ? getUser() : null;
    document.querySelectorAll("[data-account-link]").forEach((link) => {
      link.classList.toggle("signed-in", !!user);
      const label = user ? "My account (" + user.name + ")" : "Sign in or create an account";
      link.setAttribute("aria-label", label);
      link.title = label;
    });
  }

  updateAccountLinks();

  // SSO on every page: re-check a saved sign-in once when the page opens, so an
  // expired token is cleared. Pages that need the result use: await BakeryAPI.ready
  const ready = sso();
  ready.catch(() => {}); // server unreachable: pages that care handle it themselves

  window.BakeryAPI = { base: API_BASE, api, ready, login, register, logout, sso, getToken, getUser, formatPrice, formatDate, escapeHtml, ApiError };
})();
