(function () {
  "use strict";
  var KEY = "the-bakery-menu";
  var seed = [
    ["Caramel Frappe", "Frappes", 45], ["Oreo Frappe", "Frappes", 54], ["Chocolate Frappe", "Frappes", 35], ["Vanilla Frappe", "Frappes", 35],
    ["Vanilla Cake", "Cakes", 35], ["Chocolate Cake", "Cakes", 45], ["Chocolate Oreo Cake", "Cakes", 45], ["Carrot Cake", "Cakes", 35], ["Red Velvet Cake", "Cakes", 45],
    ["Water", "Drinks & Extras", 10], ["Power Rate", "Drinks & Extras", 22], ["Coke", "Drinks & Extras", 15], ["Scones", "Drinks & Extras", 10]
  ];
  function getItems() { try { var items = JSON.parse(localStorage.getItem(KEY)); if (Array.isArray(items)) return items; } catch (e) {} return seed.map(function (item, index) { return { id:"seed-" + index, name:item[0], category:item[1], price:item[2], visible:true }; }); }
  function escapeHtml(value) { return value.replace(/[&<>"']/g, function (char) { return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[char]); }); }
  document.querySelectorAll(".menu-card").forEach(function (card) {
    var heading = card.querySelector(".menu-cat h3");
    var list = card.querySelector(".item-list");
    if (!heading || !list) return;
    var category = heading.textContent.trim();
    var items = getItems().filter(function (item) { return item.visible !== false && item.category === category; });
    list.innerHTML = items.length ? items.map(function (item) { return '<li><span class="item-name">' + escapeHtml(item.name) + '</span><span class="item-actions"><span class="price">R' + item.price + '</span><button type="button" class="btn-add" data-name="' + escapeHtml(item.name) + '" data-price="' + item.price + '" aria-label="Add ' + escapeHtml(item.name) + ' to cart">Add</button></span></li>'; }).join("") : '<li class="menu-empty">Currently unavailable</li>';
  });
})();
