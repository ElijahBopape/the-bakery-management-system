// The Bakery — staff dashboard. Everything here is read from and saved to the backend API.
//  - SSO: the saved sign-in is checked when the page opens; only admins get in.
//  - Orders: GET /orders (admins see every order), PUT /orders/{id}/status
//  - Menu:   GET /categories, GET /products?available_only=false, POST/PUT/DELETE /products
(function () {
  "use strict";

  const API = window.BakeryAPI;
  const $ = (id) => document.getElementById(id);
  const esc = API.escapeHtml;
  const STATUSES = ["pending", "confirmed", "preparing", "ready", "delivered", "cancelled"];
  const label = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const SIGN_IN_PAGE = "account.html?next=admin.html";

  let categories = [];
  let products = [];
  let orders = [];
  let editingId = null; // id of the product being edited, or null when adding

  // ---- Messages ----
  function notify(el, text, isError) {
    el.textContent = text;
    el.classList.toggle("error", !!isError);
    clearTimeout(el._timer);
    if (text && !isError) el._timer = setTimeout(() => { el.textContent = ""; }, 3000);
  }
  // A 401 means the sign-in expired: go and sign in again, then come back here
  function handleError(err, el) {
    if (err.status === 401) { location.replace(SIGN_IN_PAGE); return; }
    notify(el, err.message, true);
  }

  // ---- 1. Start: who is signed in? ----
  function showDenied(title, text, buttonText, onClick) {
    $("admin-loading").hidden = true;
    $("admin-denied-title").textContent = title;
    $("admin-denied-text").textContent = text;
    $("admin-denied-action").textContent = buttonText;
    $("admin-denied-action").onclick = onClick;
    $("admin-denied").hidden = false;
  }

  async function start() {
    let user;
    try {
      user = await API.ready;
    } catch (err) {
      showDenied("Can't reach the bakery server", err.message, "Try again", () => location.reload());
      return;
    }
    if (!user) { location.replace(SIGN_IN_PAGE); return; }
    if (user.role !== "admin") {
      showDenied("Staff only",
        "You're signed in as " + user.name + ", which is a customer account. This dashboard is for bakery staff.",
        "Sign in as admin", () => { API.logout(); location.href = SIGN_IN_PAGE; });
      return;
    }
    $("admin-user-name").textContent = user.name;
    $("admin-logout").hidden = false;
    $("admin-loading").hidden = true;
    $("admin-dashboard").hidden = false;
    loadOrders();
    loadMenu();
  }

  // ---- 2. Orders ----
  async function loadOrders() {
    notify($("orders-message"), "Loading orders…");
    try {
      orders = await API.api("/orders");
      notify($("orders-message"), "");
      renderOrders();
    } catch (err) {
      handleError(err, $("orders-message"));
    }
  }

  function renderOrders() {
    const filter = $("orders-filter").value;
    const shown = orders.filter((o) => filter === "all" || o.status === filter);
    const pending = orders.filter((o) => o.status === "pending").length;
    $("orders-count").textContent = orders.length + (orders.length === 1 ? " order" : " orders") + " · " + pending + " pending";
    $("orders-empty").hidden = shown.length !== 0;
    $("orders-body").innerHTML = shown.map((o) => {
      const items = o.items.map((i) => i.quantity + " × " + esc(i.product ? i.product.name : "Product #" + i.product_id)).join("<br>");
      const extra =
        (o.delivery_address ? '<span class="cell-note">Deliver to: ' + esc(o.delivery_address) + "</span>" : "") +
        (o.notes ? '<span class="cell-note">Note: ' + esc(o.notes) + "</span>" : "");
      const options = STATUSES.map((s) => '<option value="' + s + '"' + (s === o.status ? " selected" : "") + ">" + label(s) + "</option>").join("");
      return (
        "<tr>" +
          "<td><strong>#" + o.id + "</strong></td>" +
          '<td class="nowrap">' + API.formatDate(o.created_at) + "</td>" +
          "<td>Customer #" + o.user_id + "</td>" + // the API only returns the customer's id
          "<td>" + items + extra + "</td>" +
          "<td>" + API.formatPrice(o.total) + "</td>" +
          '<td class="right"><select class="status-select status-' + o.status + '" data-id="' + o.id + '" aria-label="Status of order #' + o.id + '">' + options + "</select></td>" +
        "</tr>"
      );
    }).join("");
  }

  $("orders-body").addEventListener("change", async (e) => {
    const select = e.target.closest(".status-select");
    if (!select) return;
    const order = orders.find((o) => o.id === Number(select.dataset.id));
    const previous = order.status;
    select.disabled = true;
    try {
      const updated = await API.api("/orders/" + order.id + "/status", { method: "PUT", body: JSON.stringify({ status: select.value }) });
      order.status = updated.status;
      notify($("orders-message"), "Order #" + order.id + " is now " + label(updated.status) + ".");
    } catch (err) {
      order.status = previous;
      handleError(err, $("orders-message"));
    }
    renderOrders();
  });
  $("orders-filter").addEventListener("change", renderOrders);
  $("orders-refresh").addEventListener("click", loadOrders);

  // ---- 3. Menu ----
  async function loadMenu() {
    try {
      [categories, products] = await Promise.all([API.api("/categories"), API.api("/products?available_only=false")]);
      fillCategorySelects();
      renderProducts();
    } catch (err) {
      handleError(err, $("inventory-message"));
    }
  }

  function fillCategorySelects() {
    const options = categories.map((c) => '<option value="' + c.id + '">' + esc(c.name) + "</option>").join("");
    const editor = $("item-category");
    const filter = $("filter-category");
    const keepEditor = editor.value;
    const keepFilter = filter.value;
    editor.innerHTML = options;
    filter.innerHTML = '<option value="all">All categories</option>' + options;
    if (keepEditor) editor.value = keepEditor;
    filter.value = keepFilter || "all";
  }

  const categoryName = (id) => (categories.find((c) => c.id === id) || {}).name || "—";

  function renderProducts() {
    const query = $("search-items").value.toLowerCase().trim();
    const category = $("filter-category").value;
    const shown = products
      .filter((p) => (!query || p.name.toLowerCase().includes(query)) && (category === "all" || p.category_id === Number(category)))
      .sort((a, b) => (b.is_available - a.is_available) || a.id - b.id); // items on sale first
    const live = products.filter((p) => p.is_available).length;
    $("inventory-count").textContent = products.length + " items · " + live + " on the menu";
    $("admin-empty").hidden = shown.length !== 0;
    $("inventory-body").innerHTML = shown.map((p) =>
      "<tr>" +
        "<td><strong>" + esc(p.name) + "</strong>" + (p.description ? '<span class="cell-note">' + esc(p.description) + "</span>" : "") + "</td>" +
        '<td><span class="category-label">' + esc(categoryName(p.category_id)) + "</span></td>" +
        "<td>" + API.formatPrice(p.price) + "</td>" +
        '<td><button class="status-button ' + (p.is_available ? "" : "hidden-status") + '" data-action="toggle" data-id="' + p.id + '">' + (p.is_available ? "Visible" : "Hidden") + "</button></td>" +
        '<td><div class="row-actions"><button class="table-action" data-action="edit" data-id="' + p.id + '">Edit</button><button class="table-action delete" data-action="delete" data-id="' + p.id + '">Delete</button></div></td>' +
      "</tr>"
    ).join("");
  }

  function resetForm() {
    editingId = null;
    $("item-form").reset();
    $("editor-title").textContent = "Add menu item";
    $("save-item").textContent = "Add item";
    $("cancel-edit").hidden = true;
  }

  $("item-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = $("item-name").value.trim();
    const price = Number($("item-price").value);
    if (!name || !(price > 0)) { notify($("form-message"), "Enter a name and a price above R0.", true); return; }
    const body = {
      name: name,
      category_id: Number($("item-category").value),
      price: Math.round(price * 100) / 100,
      description: $("item-description").value.trim() || null,
    };
    const button = $("save-item");
    button.disabled = true;
    try {
      if (editingId) {
        await API.api("/products/" + editingId, { method: "PUT", body: JSON.stringify(body) });
        notify($("form-message"), "Menu item updated.");
      } else {
        await API.api("/products", { method: "POST", body: JSON.stringify(body) });
        notify($("form-message"), "Menu item added.");
      }
      resetForm();
      await loadMenu();
    } catch (err) {
      handleError(err, $("form-message"));
    } finally {
      button.disabled = false;
    }
  });

  $("inventory-body").addEventListener("click", async (e) => {
    const button = e.target.closest("button[data-action]");
    if (!button) return;
    const product = products.find((p) => p.id === Number(button.dataset.id));
    if (!product) return;
    const action = button.dataset.action;

    if (action === "edit") {
      editingId = product.id;
      $("item-name").value = product.name;
      $("item-category").value = product.category_id;
      $("item-price").value = product.price;
      $("item-description").value = product.description || "";
      $("editor-title").textContent = "Edit menu item";
      $("save-item").textContent = "Save changes";
      $("cancel-edit").hidden = false;
      $("item-name").focus();
      return;
    }

    button.disabled = true;
    try {
      if (action === "toggle") {
        await API.api("/products/" + product.id, { method: "PUT", body: JSON.stringify({ is_available: !product.is_available }) });
        notify($("inventory-message"), product.is_available ? product.name + " is hidden from the menu." : product.name + " is back on the menu.");
      }
      if (action === "delete") {
        if (!window.confirm("Delete " + product.name + " from the server? To keep it for later, use Hidden instead.")) { button.disabled = false; return; }
        await API.api("/products/" + product.id, { method: "DELETE" });
        notify($("inventory-message"), product.name + " was deleted.");
        if (editingId === product.id) resetForm();
      }
      await loadMenu();
    } catch (err) {
      button.disabled = false;
      handleError(err, $("inventory-message"));
    }
  });

  $("cancel-edit").addEventListener("click", resetForm);
  $("search-items").addEventListener("input", renderProducts);
  $("filter-category").addEventListener("change", renderProducts);
  $("admin-logout").addEventListener("click", () => { API.logout(); location.href = "index.html"; });

  start();
})();
