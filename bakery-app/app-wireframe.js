// The Bakery App (wireframe) — connected to the backend API, following the team's
// "How to Connect to the Backend API" guide (the Android app does the same with Retrofit).

// 1. Server address. Change this ONE line to switch servers (the website's is in bake/api.js).
const API_BASE = 'https://the-bakery-api-production.up.railway.app';
// const API_BASE = 'http://localhost:8000'; // local backend

const TOKEN_KEY = 'token';      // same key as the website, so one sign-in works for both
const CART_KEY = 'app-cart';
const PREFS_KEY = 'app-preferences';
const PROTECTED = ['home', 'order', 'settings']; // screens that need a signed-in user

let user = null;
let products = [];
let cart = readJSON(CART_KEY, []); // [{ id, name, price, qty }]

function readJSON(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
}
function writeJSON(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}
const getToken = () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } };
const setToken = (token) => { try { token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY); } catch {} };
const rand = (n) => `R${Number.isInteger(n) ? n : Number(n).toFixed(2)}`;
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[c]));
const when = (iso) => new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : `${iso}Z`).toLocaleString('en-ZA', { dateStyle: 'medium', timeStyle: 'short' });

// 2. Request helper: attaches the token. On 401 (expired sign-in) it goes back to login.
async function api(path, options = {}) {
  const token = getToken();
  let res;
  try {
    res = await fetch(API_BASE + path, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Can't reach the bakery server. Check your connection and try again.");
  }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (res.status === 401 && path !== '/auth/login') {
    signOut('Your sign-in has expired. Please log in again.');
    throw new Error('Signed out');
  }
  if (!res.ok) {
    const detail = data?.detail;
    throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0].msg : `Error ${res.status}`);
  }
  return data;
}

// ---- Screens ----
const screens = document.querySelectorAll('.screen');
const showScreen = (id) => {
  if (PROTECTED.includes(id) && !user) id = 'login';
  screens.forEach((screen) => screen.classList.toggle('active', screen.id === id));
  history.replaceState(null, '', `#${id}`);
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (id === 'order') { renderCart(); loadOrders(); }
};

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const id = link.getAttribute('href').slice(1);
    if (document.getElementById(id)?.classList.contains('screen')) {
      event.preventDefault();
      showScreen(id);
    }
  });
});

// ---- Signed in / out ----
function signedIn(profile, token) {
  if (token) setToken(token);
  user = profile;
  const hour = new Date().getHours();
  const part = hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';
  document.getElementById('greeting').textContent = `Good ${part}, ${profile.name.split(' ')[0]}`;
  document.getElementById('profile-name').textContent = profile.name;
  document.getElementById('profile-email').textContent = profile.email;
  document.getElementById('profile-phone').textContent = profile.phone || 'Not added';
  document.getElementById('profile-since').textContent = when(profile.created_at).split(',')[0];
  loadMenu();
}

function signOut(message) {
  setToken(null);
  user = null;
  document.getElementById('login-error').textContent = message || '';
  showScreen('login');
}

// 3. SSO on app start: a valid saved token skips the login screen
async function start() {
  const message = document.getElementById('splash-message');
  const retry = document.getElementById('splash-retry');
  const wanted = location.hash.slice(1);
  showScreen('splash');
  retry.hidden = true;
  message.textContent = 'Checking your sign-in…';
  if (!getToken()) { showScreen(wanted === 'register' ? 'register' : 'login'); return; }
  try {
    signedIn(await api('/auth/sso'));
    showScreen(PROTECTED.includes(wanted) ? wanted : 'home');
  } catch (err) {
    if (err.message === 'Signed out') return; // expired token: already on the login screen
    message.textContent = err.message;
    retry.hidden = false;
  }
}
document.getElementById('splash-retry').addEventListener('click', start);

// ---- Login + register ----
async function submit(form, errorEl, action) {
  errorEl.textContent = '';
  if (!form.checkValidity()) {
    const bad = form.querySelector(':invalid');
    errorEl.textContent = bad.validationMessage;
    bad.focus();
    return;
  }
  const button = form.querySelector('button');
  const text = button.textContent;
  button.disabled = true;
  button.textContent = 'Please wait…';
  try {
    const data = await action();
    signedIn(data.user, data.access_token);
    form.reset();
    showScreen('home');
  } catch (err) {
    errorEl.textContent = err.message;
  } finally {
    button.disabled = false;
    button.textContent = text;
  }
}

document.getElementById('login-form').addEventListener('submit', (event) => {
  event.preventDefault();
  submit(event.currentTarget, document.getElementById('login-error'), () => api('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email: document.getElementById('email').value.trim(), password: document.getElementById('password').value }),
  }));
});

document.getElementById('register-form').addEventListener('submit', (event) => {
  event.preventDefault();
  submit(event.currentTarget, document.getElementById('register-error'), () => api('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name: document.getElementById('reg-name').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      phone: document.getElementById('reg-phone').value.trim() || null,
      password: document.getElementById('reg-password').value,
    }),
  }));
});

document.getElementById('logout').addEventListener('click', (event) => {
  event.preventDefault();
  signOut();
});

// ---- Home: menu from GET /products ----
async function loadMenu() {
  const status = document.getElementById('menu-status');
  status.hidden = false;
  status.textContent = 'Loading the menu…';
  try {
    products = await api('/products');
    renderMenu();
  } catch (err) {
    status.textContent = err.message;
  }
}

function renderMenu() {
  const query = document.getElementById('search').value.toLowerCase().trim();
  const shown = products.filter((p) => !query || p.name.toLowerCase().includes(query) || (p.category?.name || '').toLowerCase().includes(query));
  const status = document.getElementById('menu-status');
  status.hidden = shown.length > 0;
  status.textContent = products.length ? 'Nothing matches your search.' : 'The menu is being updated.';
  document.getElementById('menu-list').innerHTML = shown.map((p) => `
    <article>
      <div><h4>${esc(p.name)}</h4><p>${esc(p.description || p.category?.name || '')}</p></div>
      <p>${rand(p.price)} <button type="button" data-id="${p.id}" aria-label="Add ${esc(p.name)} to order">Add</button></p>
    </article>`).join('');
}

document.getElementById('search').addEventListener('input', renderMenu);
document.getElementById('search-form').addEventListener('submit', (event) => event.preventDefault());

document.getElementById('menu-list').addEventListener('click', (event) => {
  const button = event.target.closest('button[data-id]');
  if (!button) return;
  const product = products.find((p) => p.id === Number(button.dataset.id));
  const item = cart.find((i) => i.id === product.id);
  if (item) item.qty += 1;
  else cart.push({ id: product.id, name: product.name, price: product.price, qty: 1 });
  saveCart();
  button.textContent = 'Added';
  setTimeout(() => { button.textContent = 'Add'; }, 900);
});

// ---- Order: cart + POST /orders ----
function saveCart() {
  writeJSON(CART_KEY, cart);
  const count = cart.reduce((sum, i) => sum + i.qty, 0);
  document.querySelectorAll('.order-link').forEach((link) => { link.textContent = count ? `Order (${count})` : 'Order'; });
}

function renderCart() {
  document.getElementById('cart-empty').hidden = cart.length > 0;
  document.getElementById('cart-list').innerHTML = cart.map((item, index) => `
    <article>
      <h4>${esc(item.name)}</h4>
      <p>${rand(item.price)} <label for="qty-${index}">Quantity</label> <input id="qty-${index}" data-index="${index}" type="number" min="0" value="${item.qty}"></p>
    </article>`).join('');
  document.getElementById('cart-total').textContent = rand(cart.reduce((sum, i) => sum + i.price * i.qty, 0));
  document.getElementById('place-order').disabled = cart.length === 0;
}

document.getElementById('cart-list').addEventListener('change', (event) => {
  const input = event.target.closest('input[data-index]');
  if (!input) return;
  const qty = Math.max(0, Math.floor(Number(input.value) || 0));
  const index = Number(input.dataset.index);
  if (qty === 0) cart.splice(index, 1);
  else cart[index].qty = qty;
  saveCart();
  renderCart();
});

document.getElementById('place-order').addEventListener('click', async () => {
  const button = document.getElementById('place-order');
  const message = document.getElementById('order-message');
  button.disabled = true;
  message.className = 'message';
  message.textContent = 'Placing your order…';
  try {
    const order = await api('/orders', {
      method: 'POST',
      body: JSON.stringify({
        items: cart.map((i) => ({ product_id: i.id, quantity: i.qty })),
        delivery_address: document.getElementById('address').value.trim() || null,
        notes: document.getElementById('notes').value.trim() || null,
      }),
    });
    cart = [];
    saveCart();
    document.getElementById('address').value = '';
    document.getElementById('notes').value = '';
    message.textContent = `Thank you! Order #${order.id} is placed (${rand(order.total)}). Status: ${order.status}.`;
    renderCart();
    loadOrders();
  } catch (err) {
    message.className = 'error';
    message.textContent = err.message;
    button.disabled = cart.length === 0;
  }
});

// Recent orders: GET /orders (a customer only gets their own)
async function loadOrders() {
  const status = document.getElementById('history-status');
  const list = document.getElementById('history-list');
  status.hidden = false;
  status.textContent = 'Loading your orders…';
  try {
    const orders = (await api('/orders')).slice(0, 5);
    status.hidden = orders.length > 0;
    status.textContent = 'No orders yet.';
    list.innerHTML = orders.map((o) => `
      <article>
        <div><h4>Order #${o.id}</h4><p>${when(o.created_at)} · ${o.items.map((i) => `${i.quantity} × ${esc(i.product?.name || `Product #${i.product_id}`)}`).join(', ')}</p></div>
        <p>${rand(o.total)} <strong class="status">${esc(o.status)}</strong></p>
      </article>`).join('');
  } catch (err) {
    status.textContent = err.message;
  }
}

// ---- Settings: preferences are saved on this device only ----
const prefsForm = document.getElementById('preferences-form');
const prefs = readJSON(PREFS_KEY, null);
if (prefs) {
  prefsForm.notifications.checked = prefs.notifications;
  prefsForm.offers.checked = prefs.offers;
  prefsForm.theme.value = prefs.theme;
}
prefsForm.addEventListener('submit', (event) => {
  event.preventDefault();
  writeJSON(PREFS_KEY, { notifications: prefsForm.notifications.checked, offers: prefsForm.offers.checked, theme: prefsForm.theme.value });
  const button = prefsForm.querySelector('button');
  button.textContent = 'Saved';
  setTimeout(() => { button.textContent = 'Save preferences'; }, 1400);
});

saveCart();
start();
