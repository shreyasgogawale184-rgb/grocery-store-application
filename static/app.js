const $ = (id) => document.getElementById(id);
const cart = {}; // product_id -> {product, quantity}
let products = [];

async function api(path, options) {
  const res = await fetch("/api" + path, options);
  const body = res.status === 204 ? null : await res.json();
  if (!res.ok) throw new Error(body?.error || (body?.errors || []).join(", ") || "Request failed");
  return body;
}

async function loadCategories() {
  const cats = await api("/categories");
  $("category").innerHTML = '<option value="">All categories</option>' +
    cats.map((c) => `<option>${c.name}</option>`).join("");
}

async function loadProducts() {
  const params = new URLSearchParams();
  if ($("search").value) params.set("q", $("search").value);
  if ($("category").value) params.set("category", $("category").value);
  products = await api("/products?" + params);
  $("products").innerHTML = products.map((p) => `
    <div class="card">
      <h3>${p.name}</h3>
      <div class="meta">${p.category} · per ${p.unit}</div>
      <div class="price">₹${p.price.toFixed(2)}</div>
      <div class="meta">${p.stock > 0 ? p.stock + " in stock" : "Out of stock"}</div>
      <button data-id="${p.id}" ${p.stock === 0 ? "disabled" : ""}>Add to cart</button>
    </div>`).join("") || "<p>No products found.</p>";
}

function renderCart() {
  const entries = Object.values(cart);
  $("cart-items").innerHTML = entries.map(({ product, quantity }) => `
    <li><span>${product.name} × ${quantity}</span>
        <span>₹${(product.price * quantity).toFixed(2)}
        <button data-remove="${product.id}">✕</button></span></li>`).join("");
  const total = entries.reduce((s, { product, quantity }) => s + product.price * quantity, 0);
  $("cart-total").textContent = total.toFixed(2);
}

function say(text, ok) {
  $("message").textContent = text;
  $("message").className = ok ? "ok" : "err";
}

$("products").addEventListener("click", (e) => {
  const id = e.target.dataset.id;
  if (!id) return;
  const product = products.find((p) => p.id === +id);
  const current = cart[id]?.quantity || 0;
  if (current >= product.stock) return say(`Only ${product.stock} of ${product.name} available`, false);
  cart[id] = { product, quantity: current + 1 };
  say("", true);
  renderCart();
});

$("cart-items").addEventListener("click", (e) => {
  const id = e.target.dataset.remove;
  if (id) { delete cart[id]; renderCart(); }
});

$("checkout").addEventListener("click", async () => {
  try {
    const order = await api("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_name: $("customer").value,
        items: Object.values(cart).map(({ product, quantity }) => ({ product_id: product.id, quantity })),
      }),
    });
    Object.keys(cart).forEach((k) => delete cart[k]);
    renderCart();
    say(`Order #${order.id} placed! Total ₹${order.total.toFixed(2)}`, true);
    loadProducts();
  } catch (err) { say(err.message, false); }
});

$("search").addEventListener("input", loadProducts);
$("category").addEventListener("change", loadProducts);

loadCategories().then(loadProducts);
