// The Bakery — public menu, loaded from the backend (GET /categories + GET /products).
// The menu written in index.html is a backup: if the server can't be reached,
// visitors still see it, and the cart offers WhatsApp ordering instead (cart.js).
(function () {
  "use strict";

  const grid = document.querySelector("#menu .menu-grid");
  if (!grid || !window.BakeryAPI) return;
  const { api, formatPrice, escapeHtml } = window.BakeryAPI;

  const SVG = 'class="icon gold" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
  const ICONS = {
    cup: '<svg ' + SVG + '><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>',
    cake: '<svg ' + SVG + '><path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8"/><path d="M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1"/><path d="M2 21h20"/><path d="M7 8v3"/><path d="M12 8v3"/><path d="M17 8v3"/><path d="M7 4h.01"/><path d="M12 4h.01"/><path d="M17 4h.01"/></svg>',
    glass: '<svg ' + SVG + '><path d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M5 7l1.5 12.5A2 2 0 0 0 8.5 21h7a2 2 0 0 0 2-1.5L19 7"/><path d="M9 11h6"/></svg>',
  };

  // Picture + icon for each category. A category not listed here uses DEFAULT_LOOK.
  const LOOKS = {
    "Frappes": { img: "images/frappe.png", icon: ICONS.cup },
    "Cakes": { img: "images/cake.png", icon: ICONS.cake },
    "Drinks & Extras": { img: "images/drink.png", icon: ICONS.glass },
    "Beverages": { img: "images/drink.png", icon: ICONS.glass },
  };
  const DEFAULT_LOOK = { img: "images/about-interior.png", icon: ICONS.cake };

  function renderItem(p) {
    const name = escapeHtml(p.name);
    return (
      '<li><span class="item-name">' + name + "</span>" +
      '<span class="item-actions"><span class="price">' + formatPrice(p.price) + "</span>" +
      '<button type="button" class="btn-add" data-id="' + p.id + '" data-name="' + name + '" data-price="' + p.price + '" aria-label="Add ' + name + ' to cart">Add</button>' +
      "</span></li>"
    );
  }

  function renderCard(category, items) {
    const look = LOOKS[category.name] || DEFAULT_LOOK;
    const name = escapeHtml(category.name);
    return (
      '<article class="menu-card">' +
        '<div class="menu-img-wrap"><img src="' + look.img + '" alt="' + name + '" class="menu-img" loading="lazy" /><div class="menu-img-fade" aria-hidden="true"></div></div>' +
        '<div class="menu-body"><div class="menu-cat">' + look.icon + "<h3>" + name + "</h3></div>" +
        '<ul class="item-list">' + items.map(renderItem).join("") + "</ul></div>" +
      "</article>"
    );
  }

  async function loadMenu() {
    grid.setAttribute("aria-busy", "true");
    try {
      const [categories, products] = await Promise.all([api("/categories"), api("/products")]);
      // One card per category that has products on sale (the API only sends available ones)
      const cards = categories
        .map((cat) => ({ cat, items: products.filter((p) => p.category_id === cat.id) }))
        .filter((group) => group.items.length);
      grid.innerHTML = cards.length
        ? cards.map((group) => renderCard(group.cat, group.items)).join("")
        : '<p class="menu-status">The menu is being updated. Please check back soon.</p>';
      // Tell the cart which products exist, so it can match items added earlier
      document.dispatchEvent(new CustomEvent("bakery:menu-loaded", { detail: products }));
    } catch (err) {
      console.warn("Menu: showing the built-in menu because the server could not be reached.", err);
    } finally {
      grid.removeAttribute("aria-busy");
    }
  }

  loadMenu();
})();
