// The Bakery — account page: sign in / create account, then profile + order history.
// SSO: when the page opens, a saved sign-in is checked with the server (GET /auth/sso).
// If it is still valid the sign-in form is skipped; if it has expired it is cleared.
(function () {
  "use strict";

  const API = window.BakeryAPI;
  const $ = (id) => document.getElementById(id);
  const esc = API.escapeHtml;

  const views = { loading: $("account-loading"), offline: $("offline-view"), auth: $("auth-view"), account: $("account-view") };
  const STEPS = ["pending", "confirmed", "preparing", "ready", "delivered"]; // order statuses in the backend
  const label = (status) => status.charAt(0).toUpperCase() + status.slice(1);

  // Where to go after signing in (e.g. back to the cart). Only pages on this site are allowed.
  const next = new URLSearchParams(location.search).get("next");
  const safeNext = next && /^[a-z0-9-]+\.html(#[a-z0-9-]+)?$/i.test(next) ? next : null;

  function show(name) {
    Object.keys(views).forEach((key) => { views[key].hidden = key !== name; });
  }

  // ---- 1. Start: SSO check ----
  async function start(check) {
    show("loading");
    let user;
    try {
      user = await check;
    } catch (err) {
      $("offline-message").textContent = err.message;
      show("offline");
      return;
    }
    if (user) showAccount(user);
    else show("auth");
  }

  // ---- 2. Signed in: profile + orders ----
  function showAccount(user) {
    if (safeNext) { location.replace(safeNext); return; }
    const isAdmin = user.role === "admin";
    $("account-name").textContent = user.name.split(" ")[0];
    $("account-details").textContent =
      user.email + (user.phone ? " · " + user.phone : "") + " · Member since " + API.formatDate(user.created_at).split(",")[0];
    $("admin-link").hidden = !isAdmin;
    $("orders-title").textContent = isAdmin ? "All orders" : "My orders";
    show("account");
    loadOrders();
  }

  function renderOrder(order) {
    const step = STEPS.indexOf(order.status);
    const items = order.items.map((item) => {
      const name = item.product ? item.product.name : "Product #" + item.product_id;
      return "<li>" + item.quantity + " × " + esc(name) + ' <span class="muted">' + API.formatPrice(item.unit_price * item.quantity) + "</span></li>";
    }).join("");
    const progress = order.status === "cancelled" ? "" :
      '<ol class="order-progress" aria-label="Progress: ' + label(order.status) + '">' +
        STEPS.map((s, i) => '<li class="' + (i <= step ? "done" : "") + '">' + label(s) + "</li>").join("") +
      "</ol>";
    return (
      '<li class="order-card">' +
        '<div class="order-top">' +
          '<span class="order-id">Order #' + order.id + "</span>" +
          '<span class="status-badge status-' + esc(order.status) + '">' + label(order.status) + "</span>" +
        "</div>" +
        '<p class="order-meta">' + API.formatDate(order.created_at) + " · Total " + API.formatPrice(order.total) + "</p>" +
        progress +
        '<ul class="order-items">' + items + "</ul>" +
        (order.delivery_address ? '<p class="order-meta">Deliver to: ' + esc(order.delivery_address) + "</p>" : "") +
        (order.notes ? '<p class="order-meta">Note: ' + esc(order.notes) + "</p>" : "") +
      "</li>"
    );
  }

  async function loadOrders() {
    const status = $("orders-status");
    const list = $("order-list");
    status.hidden = false;
    status.textContent = "Loading your orders…";
    try {
      const orders = await API.api("/orders"); // customers get their own; admins get all
      list.innerHTML = orders.map(renderOrder).join("");
      if (orders.length) status.hidden = true;
      else status.innerHTML = 'No orders yet. <a href="index.html#menu" class="text-link">Browse the menu</a>';
    } catch (err) {
      if (err.status === 401) { show("auth"); $("login-error").textContent = "Your sign-in has expired. Please sign in again."; return; }
      list.innerHTML = "";
      status.textContent = err.message;
    }
  }

  // ---- 3. Sign in / create account ----
  const tabs = [$("tab-login"), $("tab-register")];
  const forms = [$("login-form"), $("register-form")];

  function selectTab(index) {
    tabs.forEach((tab, i) => {
      tab.setAttribute("aria-selected", i === index ? "true" : "false");
      tab.tabIndex = i === index ? 0 : -1;
      forms[i].hidden = i !== index;
    });
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => selectTab(i));
    tab.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") { const j = 1 - i; selectTab(j); tabs[j].focus(); }
    });
  });

  async function submitForm(form, errorEl, busyText, action) {
    const button = form.querySelector('button[type="submit"]');
    const idleText = button.textContent;
    errorEl.textContent = "";
    if (!form.checkValidity()) {
      const bad = form.querySelector(":invalid");
      errorEl.textContent = bad.validationMessage;
      bad.focus();
      return;
    }
    button.disabled = true;
    button.textContent = busyText;
    try {
      const user = await action();
      form.reset();
      showAccount(user);
    } catch (err) {
      errorEl.textContent = err.message;
    } finally {
      button.disabled = false;
      button.textContent = idleText;
    }
  }

  $("login-form").addEventListener("submit", (e) => {
    e.preventDefault();
    submitForm(e.currentTarget, $("login-error"), "Signing in…", () =>
      API.login($("login-email").value.trim(), $("login-password").value));
  });

  $("register-form").addEventListener("submit", (e) => {
    e.preventDefault();
    submitForm(e.currentTarget, $("register-error"), "Creating account…", () =>
      API.register({
        name: $("register-name").value.trim(),
        email: $("register-email").value.trim(),
        phone: $("register-phone").value.trim() || null,
        password: $("register-password").value,
      }));
  });

  // ---- 4. Other buttons ----
  $("logout-btn").addEventListener("click", () => {
    API.logout();
    $("order-list").innerHTML = "";
    selectTab(0);
    show("auth");
  });
  $("orders-refresh").addEventListener("click", loadOrders);
  $("offline-retry").addEventListener("click", () => start(API.sso()));

  if (location.hash === "#register") selectTab(1);
  start(API.ready);
})();
