// The Bakery — mockup cart (frontend only, no backend / no persistence)
(function () {
  "use strict";

  var cart = []; // { name, price, qty }

  var els = {
    open: document.getElementById("cart-open"),
    close: document.getElementById("cart-close"),
    overlay: document.getElementById("cart-overlay"),
    drawer: document.getElementById("cart-drawer"),
    items: document.getElementById("cart-items"),
    empty: document.getElementById("cart-empty"),
    count: document.getElementById("cart-count"),
    total: document.getElementById("cart-total"),
    checkout: document.getElementById("cart-checkout"),
  };

  function openCart() {
    els.overlay.hidden = false;
    els.drawer.classList.add("open");
    els.drawer.setAttribute("aria-hidden", "false");
  }

  function closeCart() {
    els.overlay.hidden = true;
    els.drawer.classList.remove("open");
    els.drawer.setAttribute("aria-hidden", "true");
  }

  function addItem(name, price) {
    var existing = cart.find(function (i) { return i.name === name; });
    if (existing) {
      existing.qty += 1;
    } else {
      cart.push({ name: name, price: price, qty: 1 });
    }
    render();
  }

  function changeQty(name, delta) {
    var item = cart.find(function (i) { return i.name === name; });
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) {
      cart = cart.filter(function (i) { return i.name !== name; });
    }
    render();
  }

  function render() {
    // Item rows
    els.items.innerHTML = "";
    if (cart.length === 0) {
      els.items.appendChild(els.empty);
      els.empty.style.display = "";
    } else {
      cart.forEach(function (item) {
        var row = document.createElement("div");
        row.className = "cart-row";
        row.innerHTML =
          '<div class="cart-row-info">' +
            '<span class="cart-row-name">' + item.name + "</span>" +
            '<span class="cart-row-price">R' + item.price + " each</span>" +
          "</div>" +
          '<div class="cart-qty">' +
            '<button type="button" class="qty-btn" data-action="dec" data-name="' + item.name + '" aria-label="Decrease quantity">&minus;</button>' +
            '<span class="qty-num">' + item.qty + "</span>" +
            '<button type="button" class="qty-btn" data-action="inc" data-name="' + item.name + '" aria-label="Increase quantity">+</button>' +
          "</div>" +
          '<span class="cart-row-total">R' + item.price * item.qty + "</span>";
        els.items.appendChild(row);
      });
    }

    // Totals
    var subtotal = cart.reduce(function (sum, i) { return sum + i.price * i.qty; }, 0);
    var count = cart.reduce(function (sum, i) { return sum + i.qty; }, 0);
    els.total.textContent = "R" + subtotal;
    els.count.textContent = count;
    els.count.classList.toggle("has-items", count > 0);
  }

  // Delegated listener supports menu items rendered from localStorage.
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".btn-add");
    if (!btn) return;
    addItem(btn.dataset.name, parseInt(btn.dataset.price, 10));
    btn.classList.add("added");
    btn.textContent = "Added";
    setTimeout(function () { btn.classList.remove("added"); btn.textContent = "Add"; }, 900);
  });

  // Quantity buttons (delegated)
  els.items.addEventListener("click", function (e) {
    var btn = e.target.closest(".qty-btn");
    if (!btn) return;
    changeQty(btn.dataset.name, btn.dataset.action === "inc" ? 1 : -1);
  });

  els.open.addEventListener("click", openCart);
  els.close.addEventListener("click", closeCart);
  els.overlay.addEventListener("click", closeCart);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeCart();
  });

  els.checkout.addEventListener("click", function () {
    if (cart.length === 0) return;
    els.checkout.textContent = "Thanks! (demo only)";
    els.checkout.disabled = true;
    setTimeout(function () {
      els.checkout.textContent = "Checkout";
      els.checkout.disabled = false;
    }, 1800);
  });

  render();
})();
