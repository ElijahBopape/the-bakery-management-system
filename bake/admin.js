(function () {
  "use strict";
  var KEY = "the-bakery-menu";
  var seed = [
    { id:"caramel-frappe", name:"Caramel Frappe", category:"Frappes", price:45, visible:true },
    { id:"oreo-frappe", name:"Oreo Frappe", category:"Frappes", price:54, visible:true },
    { id:"chocolate-frappe", name:"Chocolate Frappe", category:"Frappes", price:35, visible:true },
    { id:"vanilla-frappe", name:"Vanilla Frappe", category:"Frappes", price:35, visible:true },
    { id:"vanilla-cake", name:"Vanilla Cake", category:"Cakes", price:35, visible:true },
    { id:"chocolate-cake", name:"Chocolate Cake", category:"Cakes", price:45, visible:true },
    { id:"chocolate-oreo-cake", name:"Chocolate Oreo Cake", category:"Cakes", price:45, visible:true },
    { id:"carrot-cake", name:"Carrot Cake", category:"Cakes", price:35, visible:true },
    { id:"red-velvet-cake", name:"Red Velvet Cake", category:"Cakes", price:45, visible:true },
    { id:"water", name:"Water", category:"Drinks & Extras", price:10, visible:true },
    { id:"power-rate", name:"Power Rate", category:"Drinks & Extras", price:22, visible:true },
    { id:"coke", name:"Coke", category:"Drinks & Extras", price:15, visible:true },
    { id:"scones", name:"Scones", category:"Drinks & Extras", price:10, visible:true }
  ];
  function read() { try { var value = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(value) ? value : seed.slice(); } catch (e) { return seed.slice(); } }
  function save(items) { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) {} }
  if (!localStorage.getItem(KEY)) save(seed);
  var items = read(), editing = null;
  var form = document.getElementById("item-form"), name = document.getElementById("item-name"), category = document.getElementById("item-category"), price = document.getElementById("item-price"), id = document.getElementById("item-id"), body = document.getElementById("inventory-body"), message = document.getElementById("form-message"), search = document.getElementById("search-items"), filter = document.getElementById("filter-category");
  function slug(value) { return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") + "-" + Date.now(); }
  function render() {
    var query = search.value.toLowerCase().trim(), selected = filter.value;
    var visible = items.filter(function (item) { return (!query || item.name.toLowerCase().indexOf(query) > -1) && (selected === "all" || item.category === selected); });
    document.getElementById("inventory-count").textContent = items.length + (items.length === 1 ? " item" : " items");
    document.getElementById("admin-empty").hidden = visible.length !== 0;
    body.innerHTML = visible.map(function (item) { return '<tr><td><strong>' + escapeHtml(item.name) + '</strong></td><td><span class="category-label">' + escapeHtml(item.category) + '</span></td><td>R' + item.price + '</td><td><button class="status-button ' + (item.visible ? "" : "hidden-status") + '" data-action="toggle" data-id="' + item.id + '">' + (item.visible ? "Visible" : "Hidden") + '</button></td><td><div class="row-actions"><button class="table-action" data-action="edit" data-id="' + item.id + '">Edit</button><button class="table-action delete" data-action="delete" data-id="' + item.id + '">Delete</button></div></td></tr>'; }).join("");
  }
  function escapeHtml(value) { return value.replace(/[&<>"']/g, function (char) { return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[char]); }); }
  function notify(text) { message.textContent = text; window.setTimeout(function () { message.textContent = ""; }, 2200); }
  form.addEventListener("submit", function (event) { event.preventDefault(); var itemName = name.value.trim(), itemPrice = Number(price.value); if (!itemName || !Number.isInteger(itemPrice) || itemPrice < 1) { notify("Enter a name and whole-number price."); return; } if (editing) { items = items.map(function (item) { return item.id === editing ? { id:item.id, name:itemName, category:category.value, price:itemPrice, visible:item.visible } : item; }); notify("Menu item updated."); } else { items.push({ id:slug(itemName), name:itemName, category:category.value, price:itemPrice, visible:true }); notify("Menu item added."); } save(items); resetForm(); render(); });
  body.addEventListener("click", function (event) { var button = event.target.closest("button[data-action]"); if (!button) return; var item = items.find(function (entry) { return entry.id === button.dataset.id; }); if (!item) return; if (button.dataset.action === "toggle") { item.visible = !item.visible; save(items); render(); notify(item.visible ? "Item is now visible." : "Item hidden from public menu."); } if (button.dataset.action === "delete" && window.confirm("Remove " + item.name + " from the menu?")) { items = items.filter(function (entry) { return entry.id !== item.id; }); save(items); render(); notify("Menu item removed."); } if (button.dataset.action === "edit") { editing = item.id; id.value = item.id; name.value = item.name; category.value = item.category; price.value = item.price; document.getElementById("editor-title").textContent = "Edit menu item"; document.getElementById("save-item").textContent = "Save changes"; document.getElementById("cancel-edit").hidden = false; name.focus(); } });
  function resetForm() { editing = null; form.reset(); id.value = ""; document.getElementById("editor-title").textContent = "Add menu item"; document.getElementById("save-item").textContent = "Add item"; document.getElementById("cancel-edit").hidden = true; }
  document.getElementById("cancel-edit").addEventListener("click", resetForm);
  document.getElementById("reset-data").addEventListener("click", function () { if (window.confirm("Restore the original menu?")) { items = seed.slice(); save(items); resetForm(); render(); notify("Demo menu restored."); } });
  search.addEventListener("input", render); filter.addEventListener("change", render); render();
})();
