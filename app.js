"use strict";

const state = { catalog: null, nodeId: "home", typeId: "all", query: "", sort: "featured" };
const $ = (selector) => document.querySelector(selector);

function indexById(items) { return new Map(items.map((item) => [item.id, item])); }
function normalize(value) { return value.toLocaleLowerCase("it").normalize("NFD").replace(/[\u0300-\u036f]/g, ""); }

function descendants(nodeId) {
  const found = new Set([nodeId]);
  let changed = true;
  while (changed) {
    changed = false;
    state.catalog.navigationNodes.forEach((node) => {
      if (found.has(node.parentId) && !found.has(node.id)) { found.add(node.id); changed = true; }
    });
  }
  return found;
}

function visibleResources() {
  const nodes = descendants(state.nodeId);
  const topics = indexById(state.catalog.topics);
  const types = indexById(state.catalog.resourceTypes);
  const query = normalize(state.query);
  return state.catalog.resources.filter((resource) => {
    const inNode = state.nodeId === "home" || resource.navigationNodeIds.some((id) => nodes.has(id));
    const inType = state.typeId === "all" || resource.typeId === state.typeId;
    const haystack = normalize([resource.title, resource.description, types.get(resource.typeId)?.label,
      ...resource.topicIds.map((id) => topics.get(id)?.label || "")].join(" "));
    return inNode && inType && (!query || haystack.includes(query));
  }).sort((a, b) => {
    if (state.sort === "title") return a.title.localeCompare(b.title, "it");
    if (state.sort === "type") return (types.get(a.typeId)?.label || "").localeCompare(types.get(b.typeId)?.label || "", "it");
    return Number(Boolean(b.featured)) - Number(Boolean(a.featured)) || a.title.localeCompare(b.title, "it");
  });
}

function renderTree() {
  const children = new Map();
  state.catalog.navigationNodes.forEach((node) => {
    const key = node.parentId || "root";
    children.set(key, [...(children.get(key) || []), node]);
  });
  const countFor = (id) => state.catalog.resources.filter((r) => id === "home" || r.navigationNodeIds.some((n) => descendants(id).has(n))).length;
  const branch = (parentId) => `<ul class="tree-list">${(children.get(parentId) || []).sort((a,b) => a.order-b.order).map((node) =>
    `<li><button class="tree-button ${node.id === state.nodeId ? "active" : ""}" data-node="${node.id}"><span>${node.label}</span><span class="tree-count">${countFor(node.id)}</span></button>${branch(node.id)}</li>`).join("")}</ul>`;
  $("#tree").innerHTML = branch("root");
  $("#tree").querySelectorAll("button").forEach((button) => button.addEventListener("click", () => { state.nodeId = button.dataset.node; render(); }));
}

function renderFilters() {
  const available = new Set(state.catalog.resources.map((r) => r.typeId));
  const options = [{ id: "all", label: "Tutte" }, ...state.catalog.resourceTypes.filter((t) => available.has(t.id))];
  $("#type-filters").innerHTML = options.map((type) => `<button class="chip ${type.id === state.typeId ? "active" : ""}" data-type="${type.id}">${type.label}</button>`).join("");
  $("#type-filters").querySelectorAll("button").forEach((button) => button.addEventListener("click", () => { state.typeId = button.dataset.type; renderResults(); renderFilters(); }));
}

function renderResults() {
  const resources = visibleResources();
  const nodes = indexById(state.catalog.navigationNodes);
  const types = indexById(state.catalog.resourceTypes);
  const topics = indexById(state.catalog.topics);
  const selected = nodes.get(state.nodeId);
  $("#section-title").textContent = selected.label;
  $("#breadcrumb").textContent = `Catalogo / ${selected.label}`;
  $("#result-count").textContent = `${resources.length} ${resources.length === 1 ? "risorsa" : "risorse"}`;
  $("#resources").innerHTML = resources.map((resource) => `<article class="resource-card">
    <div class="card-top"><span class="type">${types.get(resource.typeId)?.label}</span>${resource.featured ? '<span class="star" title="In evidenza">◆</span>' : ""}</div>
    <h3>${resource.title}</h3><p>${resource.description}</p>
    <div class="tags">${resource.topicIds.map((id) => `<span class="tag">${topics.get(id)?.label}</span>`).join("")}</div>
    <a class="card-link" href="${resource.url}" target="_blank" rel="noopener">Apri la risorsa <span aria-hidden="true">↗</span></a>
  </article>`).join("");
  $("#empty").hidden = resources.length > 0;
}

function render() { renderTree(); renderFilters(); renderResults(); }

function start() {
  if (!window.CATALOG_DATA) {
    $("#resources").innerHTML = "<p>Impossibile caricare il catalogo locale.</p>";
    return;
  }
  state.catalog = window.CATALOG_DATA;
  render();
}

$("#search").addEventListener("input", (event) => { state.query = event.target.value; renderResults(); });
$("#sort").addEventListener("change", (event) => { state.sort = event.target.value; renderResults(); });
$("#menu-toggle").addEventListener("click", (event) => {
  const collapsed = $(".sidebar").classList.toggle("collapsed");
  event.currentTarget.textContent = collapsed ? "+" : "−";
  event.currentTarget.setAttribute("aria-expanded", String(!collapsed));
});
document.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key === "k") { event.preventDefault(); $("#search").focus(); } });
start();
