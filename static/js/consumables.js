const API_PREFIX = "/api/v1";
let filterManager;

async function fetchItems() {
  try {
    console.log("Fetching items from /items/all");
    const response = await fetch(API_PREFIX+"/items/all");
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const items = await response.json();
    console.log("Fetched items:", items);
    populateTable(items);
    initializeFilters();
  } catch (error) {
    console.error("Failed to fetch items:", error);
    showEmptyState("Failed to load items. Please refresh the page.");
  }
}

async function initializeFilters() {
    filterManager = new FilterManager('items-table-body');
    await populateTagFilter();
    await populateLocationFilter();
    setupFilterEvents();
}

async function populateTagFilter() {
    try {
        const response = await fetch('/api/v1/tags/all');
        const data = await response.json();
        const tagsDropdown = document.getElementById('filter-tags-dropdown');
        
        if (tagsDropdown) {
            tagsDropdown.innerHTML = '<option value="">All Tags</option>';
            data.tags.forEach(tag => {
                const option = document.createElement('option');
                option.value = tag.name;
                option.textContent = tag.name;
                tagsDropdown.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading tags for filter:', error);
    }
}

async function populateLocationFilter() {
    try {
        const response = await fetch('/api/v1/location/all');
        const data = await response.json();
        const locationDropdown = document.getElementById('filter-location-dropdown');
        
        if (locationDropdown) {
            locationDropdown.innerHTML = '<option value="">All Locations</option>';
            data.locations.forEach(location => {
                const option = document.createElement('option');
                option.value = location.name;
                option.textContent = location.name;
                locationDropdown.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading locations for filter:', error);
    }
}

function setupFilterEvents() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.addEventListener('input', (e) => filterManager.updateFilter('search', e.target.value));
    
    const nameInput = document.getElementById('filter-name');
    if (nameInput) nameInput.addEventListener('input', (e) => filterManager.updateFilter('name', e.target.value));
    
    const tagsDropdown = document.getElementById('filter-tags-dropdown');
    if (tagsDropdown) tagsDropdown.addEventListener('change', (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions).map(opt => opt.value).filter(val => val);
        filterManager.updateFilter('tags', selectedOptions);
    });
    
    const locationDropdown = document.getElementById('filter-location-dropdown');
    if (locationDropdown) locationDropdown.addEventListener('change', (e) => filterManager.updateFilter('location', e.target.value));
}

window.updateItemInTable = function (data) {
  try {
    const tableBody = document.getElementById("items-table-body");
    if (!tableBody) return;
    const id = data.id || data.item_id || (data.item && data.item.id);
    if (!id) return;

    let targetRow = null;
    const rows = tableBody.querySelectorAll("tr");
    rows.forEach((r) => {
      const cell = r.querySelector(`.item-id-${id}`) || r.cells[0];
      if (!cell) return;
      const text = cell.textContent.trim();
      if (text === String(id)) targetRow = r;
    });

    if (!targetRow) {
      if (typeof window.addItemToTable === "function") window.addItemToTable(data);
      return;
    }

    const tags = Array.isArray(data.tags) ? data.tags.join(", ") : data.tags || "";
    const expires = data.expires ? new Date(data.expires).toLocaleDateString() : "";
    const lastUpdated = data.last_updated ? new Date(data.last_updated).toLocaleString() : "";

    targetRow.innerHTML = `
      <td class="item-id-${id}">${id}</td>
      <td>${data.name || ""}</td>
      <td>${data.quantity}</td>
      <td>${tags}</td>
      <td>${data.location || data.location_id || ""}</td>
      <td>${expires}</td>
      <td>${lastUpdated}</td>
      <td>${data.updated_by || ""}</td>
      <td class="text-end">
        <div class="d-inline-flex gap-2 align-items-center">
          <button class="btn btn-sm btn-link text-primary p-0" onclick="openEditModal(${id})" title="Edit item"><i class="fas fa-edit"></i></button>
          <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteItem(${id})" title="Delete item"><i class="fas fa-trash"></i></button>
        </div>
      </td>
    `;

    targetRow.classList.add("table-warning");
    setTimeout(() => targetRow.classList.remove("table-warning"), 1200);
    updateStats();
  } catch (err) {
    console.error("Failed to update table row:", err);
  }
};

function populateTable(items) {
  const tableBody = document.getElementById("items-table-body");
  tableBody.innerHTML = "";
  items = items.items;
  if (items && items.length > 0) {
    items.forEach((item) => {
      const row = document.createElement("tr");

      const tags = Array.isArray(item.tags) ? item.tags.join(", ") : item.tags || "";
      const expires = item.expires ? new Date(item.expires).toLocaleDateString() : "";
      const lastUpdated = item.last_updated ? new Date(item.last_updated).toLocaleString() : "";

      row.innerHTML = `
                <td class="item-id-${item.id}">${item.id || ""}</td>
                <td>${item.name || ""}</td>
                <td>${item.quantity}</td>
                <td>${tags}</td>
                <td>${item.location || ""}</td>
                <td>${expires}</td>
                <td>${lastUpdated}</td>
                <td>${item.updated_by || ""}</td>
                <td class="text-end">
                  <div class="d-inline-flex gap-3 align-items-center">
                    <button class="btn btn-sm btn-link text-primary p-0" onclick="openEditModal(${item.id})" title="Edit item">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteItem(${item.id})" title="Delete item">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
            `;
      row.classList.add("item-row");
      tableBody.appendChild(row);
    });
  } else {
    showEmptyState("No items found. Click 'Add Item' to get started.");
  }
}

async function openEditModal(itemId) {
  try {
    const resp = await fetch(`${API_PREFIX}/items/one/${itemId}`);
    if (!resp.ok) throw new Error(`Failed to fetch item ${itemId}: ${resp.status}`);
    const data = await resp.json();

    window.editingItemData = data;
    window.editingItemId = itemId;

    const titleEl = document.getElementById("addItemModalLabel");
    const submitBtn = document.getElementById("createItemBtn");
    if (titleEl) titleEl.textContent = "Edit Item";
    if (submitBtn) {
      for (const node of Array.from(submitBtn.childNodes)) {
        if (node.nodeType === Node.TEXT_NODE) {
          node.nodeValue = ' Save Changes';
          break;
        }
      }
    }

    const modalEl = document.getElementById("addItemModal");
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  } catch (err) {
    console.error("Failed to open edit modal:", err);
    alert("Failed to load item for editing. Please refresh and try again.");
  }
}

function showEmptyState(message) {
  const tableBody = document.getElementById("items-table-body");
  const row = document.createElement("tr");
  row.innerHTML = `<td colspan="9" class="text-center text-muted py-4">${message}</td>`;
  tableBody.appendChild(row);
}

async function updateStats() {
  try {
    const response = await fetch(API_PREFIX + "/items/all");
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    const items = data.items || [];
    const totalItems = items.length;
    const today = new Date(); today.setHours(0, 0, 0, 0);

    const inStockCount = items.filter((item) => {
      if (item.quantity <= 0) return false;
      if (!item.expires) return true;
      const expiresDate = new Date(item.expires); expiresDate.setHours(0, 0, 0, 0);
      return expiresDate >= today;
    }).length;

    const outOfStockCount = items.filter((item) => {
      if (item.quantity > 0) return false;
      if (!item.expires) return true;
      const expiresDate = new Date(item.expires); expiresDate.setHours(0, 0, 0, 0);
      return expiresDate >= today;
    }).length;

    const expiredCount = items.filter((item) => {
      if (!item.expires) return false;
      const expiresDate = new Date(item.expires); expiresDate.setHours(0, 0, 0, 0);
      return expiresDate < today;
    }).length;

    document.getElementById("stat-total").textContent = `${totalItems} Items`;
    document.getElementById("stat-in-stock").textContent = `${inStockCount} Items`;
    document.getElementById("stat-out-of-stock").textContent = `${outOfStockCount} Items`;
    document.getElementById("stat-expired").textContent = `${expiredCount} Items`;
  } catch (error) {
    console.error("Failed to update stats:", error);
  }
}

window.addItemToTable = function (item) {
  console.log("Adding item to table:", item);
  const tableBody = document.getElementById("items-table-body");
  if (!tableBody) { console.error("Table body not found!"); return; }

  const noItemsRow = tableBody.querySelector('td[colspan="9"]');
  if (noItemsRow) noItemsRow.parentElement.remove();

  const row = document.createElement("tr");
  const tags = Array.isArray(item.tags) ? item.tags.join(", ") : item.tags || "";
  const expires = item.expires ? new Date(item.expires).toLocaleDateString() : "";
  const last_updated = item.last_updated ? new Date(item.last_updated).toLocaleString() : "";

  row.innerHTML = `
		<td>${item.id || ""}</td>
		<td>${item.name || ""}</td>
		<td>${item.quantity}</td>
		<td>${tags}</td>
		<td>${item.location || item.location_id || ""}</td>
		<td>${expires}</td>
		<td>${last_updated}</td>
		<td>${item.updated_by || ""}</td>
		<td class="text-end">
		<button class="btn btn-sm btn-link text-primary edit-btn p-0 me-2 display-inline" onclick="openEditModal(${item.id})" title="Edit item">
		<i class="fas fa-edit"></i>
		</button>
		<button class="btn btn-sm btn-link text-danger delete-btn p-0 display-inline" onclick="deleteItem(${item.id})" title="Delete item">
        <i class="fas fa-trash"></i>
      </button>
    </td>
	`;
  row.classList.add("item-row");
  tableBody.insertBefore(row, tableBody.firstChild);
  row.classList.add("table-success");
  setTimeout(() => row.classList.remove("table-success"), 1000);
  updateStats();
  console.log("Item added to table successfully");
};

function filterTable() { if (filterManager) filterManager.applyFilters(); }
function clearFilters() { if (filterManager) filterManager.clearFilters(); }

window.filterTable = filterTable;
window.clearFilters = clearFilters;
window.updateStats = updateStats;

async function deleteItem(itemId) {
  const confirmBtn = document.getElementById("confirmDeleteBtn");
  confirmBtn.setAttribute("data-item-id", itemId);
  const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));
  modal.show();
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("consumable.js loaded");
  fetchItems();

  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", async function () {
      const itemId = this.getAttribute("data-item-id");
      if (!itemId) { console.error("No item ID found"); return; }

      this.disabled = true;

      try {
        const response = await fetch(`${API_PREFIX}/items/${itemId}`, {
          method: "DELETE", headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const modal = bootstrap.Modal.getInstance(document.getElementById("deleteConfirmModal"));
        modal.hide();

        const rows = document.querySelectorAll("#items-table-body tr");
        rows.forEach((row) => {
          const deleteBtn = row.querySelector(`button[onclick="deleteItem(${itemId})"]`);
          if (deleteBtn) {
            row.classList.add("table-danger");
            setTimeout(() => { row.remove(); fetchItems(); updateStats(); }, 500);
          }
        });
      } catch (error) {
        console.error("Failed to delete item:", error);
        alert("Failed to delete item. Please try again.");
      } finally {
        this.disabled = false;
        this.innerHTML = "Delete Item";
      }
    });
  }
});

document.getElementById("logoutButton").addEventListener("click", () => {
  window.location.href = "/auth/logout";
});



