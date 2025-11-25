const API_PREFIX = "/api/v1";
window.API_PREFIX = API_PREFIX; // Make it available globally

// Add a helper function at the top of the file
function formatDateOnly(dateString) {
  if (!dateString) return "";
  // For date-only strings (YYYY-MM-DD), parse without timezone conversion
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    const [year, month, day] = dateString.split("-").map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed
    return date.toLocaleDateString();
  }
  // For ISO datetime strings, extract date components
  const parsed = new Date(dateString);
  if (Number.isNaN(parsed.getTime())) return "";
  const year = parsed.getFullYear();
  const month = parsed.getMonth();
  const day = parsed.getDate();
  const localDate = new Date(year, month, day);
  return localDate.toLocaleDateString();
}

// Function to fetch items from the server
async function fetchItems() {
  try {
    console.log("Fetching items from /items/all");
    const response = await fetch(API_PREFIX + "/items/all");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const items = await response.json();
    console.log("Fetched items:", items);
    populateTable(items);
  } catch (error) {
    console.error("Failed to fetch items:", error);
    showEmptyState("Failed to load items. Please refresh the page.");
  }
}

// Update an existing row in the table with new data (used after edit)
window.updateItemInTable = function (data) {
  try {
    const tableBody = document.getElementById("items-table-body");
    if (!tableBody) return;
    const id = data.id || data.item_id || (data.item && data.item.id);
    if (!id) return;

    // Find row that contains the id in the first column (or the cell with class item-id-<id>)
    let targetRow = null;
    const rows = tableBody.querySelectorAll("tr");
    rows.forEach((r) => {
      const cell = r.querySelector(`.item-id-${id}`) || r.cells[0];
      if (!cell) return;
      const text = cell.textContent.trim();
      if (text === String(id)) targetRow = r;
    });

    if (!targetRow) {
      // If not found, add as new
      if (typeof window.addItemToTable === "function") {
        window.addItemToTable(data);
      }
      return;
    }

    const tags = Array.isArray(data.tags)
      ? data.tags.join(", ")
      : data.tags || "";
    const expires = data.expires ? formatDateOnly(data.expires) : "";
    const lastUpdated = data.last_updated
      ? new Date(data.last_updated).toLocaleString()
      : "";

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

// Function to populate the table
function populateTable(items) {
  const tableBody = document.getElementById("items-table-body");
  tableBody.innerHTML = "";
  items = items.items;
  if (items && items.length > 0) {
    items.forEach((item) => {
      const row = document.createElement("tr");

      // Handle tags display - could be array or string
      const tags = Array.isArray(item.tags)
        ? item.tags.join(", ")
        : item.tags || "";

      // Format dates properly
      const expires = item.expires ? formatDateOnly(item.expires) : "";
      const lastUpdated = item.last_updated
        ? new Date(item.last_updated).toLocaleString()
        : "";

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
                    <button class="btn btn-sm btn-link text-primary p-0" onclick="openEditModal(${
                      item.id
                    })" title="Edit item">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteItem(${
                      item.id
                    })" title="Delete item">
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
    if (!resp.ok)
      throw new Error(`Failed to fetch item ${itemId}: ${resp.status}`);
    const data = await resp.json();

    // Make the fetched item available for the modal initializer
    window.editingItemData = data;
    // Also expose the numeric id explicitly so the modal script can read it directly
    window.editingItemId = itemId;

    // Update modal UI elements immediately (preserve spinner span if present)
    const titleEl = document.getElementById("addItemModalLabel");
    const submitBtn = document.getElementById("createItemBtn");
    if (titleEl) titleEl.textContent = "Edit Item";
    if (submitBtn) {
      const textNodes = [];
      for (const node of Array.from(submitBtn.childNodes)) {
        if (node.nodeType === Node.TEXT_NODE) {
          textNodes.push(node);
        }
      }
      textNodes.forEach((node) => node.remove());
      submitBtn.appendChild(document.createTextNode(" Save Changes"));
    }

    // Show modal - the modal's shown handler will read window.editingItemData and prefill after tags/locations are loaded
    const modalEl = document.getElementById("addItemModal");
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  } catch (err) {
    console.error("Failed to open edit modal:", err);
    alert("Failed to load item for editing. Please refresh and try again.");
  }
}

// Function to show empty state
function showEmptyState(message) {
  const tableBody = document.getElementById("items-table-body");
  const row = document.createElement("tr");
  row.innerHTML = `
		<td colspan="9" class="text-center text-muted py-4">
			${message}
		</td>
	`;
  tableBody.appendChild(row);
}

// Function to calculate and update stats
async function updateStats() {
  try {
    const response = await fetch(API_PREFIX + "/items/all");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const items = data.items || [];
    const totalItems = items.length;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // In stock
    const inStockCount = items.filter((item) => {
      if (item.quantity <= 0) return false;
      if (!item.expires) return true;
      const expiresDate = new Date(item.expires);
      expiresDate.setHours(0, 0, 0, 0);
      return expiresDate >= today;
    }).length;

    // Out of stock
    const outOfStockCount = items.filter((item) => {
      if (item.quantity > 0) return false;
      if (!item.expires) return true;
      const expiresDate = new Date(item.expires);
      expiresDate.setHours(0, 0, 0, 0);
      return expiresDate >= today;
    }).length;

    // Expired
    const expiredCount = items.filter((item) => {
      if (!item.expires) return false;
      const expiresDate = new Date(item.expires);
      expiresDate.setHours(0, 0, 0, 0);
      return expiresDate < today;
    }).length;

    // Update stat cards
    document.getElementById("stat-total").textContent = `${totalItems} Items`;
    document.getElementById(
      "stat-in-stock"
    ).textContent = `${inStockCount} Items`;
    document.getElementById(
      "stat-out-of-stock"
    ).textContent = `${outOfStockCount} Items`;
    document.getElementById(
      "stat-expired"
    ).textContent = `${expiredCount} Items`;
  } catch (error) {
    console.error("Failed to update stats:", error);
  }
}

// Function to add a new item to the table (called from modal) - MAKE IT GLOBAL
window.addItemToTable = function (item) {
  console.log("Adding item to table:", item);
  const tableBody = document.getElementById("items-table-body");

  if (!tableBody) {
    console.error("Table body not found!");
    return;
  }

  // Remove "no items" message if it exists
  const noItemsRow = tableBody.querySelector('td[colspan="9"]');
  if (noItemsRow) {
    noItemsRow.parentElement.remove();
  }

  // Create new row - handle both response formats
  const row = document.createElement("tr");
  const tags = Array.isArray(item.tags)
    ? item.tags.join(", ")
    : item.tags || "";
  const expires = item.expires ? formatDateOnly(item.expires) : "";
  const last_updated = item.last_updated
    ? new Date(item.last_updated).toLocaleString()
    : "";

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
			<div class="d-inline-flex gap-3 align-items-center">
				<button 
					class="btn btn-sm btn-link text-primary p-0" 
					onclick="openEditModal(${item.id})"
					title="Edit item"
				>
					<i class="fas fa-edit"></i>
				</button>
				<button 
					class="btn btn-sm btn-link text-danger p-0" 
					onclick="deleteItem(${item.id})"
					title="Delete item"
				>
					<i class="fas fa-trash"></i>
				</button>
			</div>
		</td>
	`;
  row.classList.add("item-row");

  tableBody.insertBefore(row, tableBody.firstChild);

  row.classList.add("table-success");
  setTimeout(() => {
    row.classList.remove("table-success");
  }, 1000);

  // Update stats after adding item
  updateStats();

  console.log("Item added to table successfully");
};

function filterTable() {
  // Get search input value
  const searchValue =
    document.getElementById("search-input")?.value.toLowerCase() || "";

  // Get specific filter values
  const nameFilter =
    document.getElementById("filter-name")?.value.toLowerCase() || "";
  const tagsFilter =
    document.getElementById("filter-tags")?.value.toLowerCase() || "";
  const locationFilter =
    document.getElementById("filter-location")?.value.toLowerCase() || "";

  const rows = document.querySelectorAll("#items-table-body tr");

  rows.forEach((row) => {
    // Skip the "no items" row
    if (row.querySelector('td[colspan="9"]')) {
      return;
    }

    const cells = row.cells;
    const itemName = cells[1].textContent.toLowerCase();
    const itemTags = cells[3].textContent.toLowerCase();
    const itemLocation = cells[4].textContent.toLowerCase();

    // Search input searches across all fields
    const searchMatch =
      !searchValue ||
      itemName.includes(searchValue) ||
      itemTags.includes(searchValue) ||
      itemLocation.includes(searchValue);

    // Specific filters take precedence if they have values
    const nameMatch = !nameFilter || itemName.includes(nameFilter);

    // Handle comma-separated tags: split by comma, trim, and check if any match
    let tagsMatch = true;
    if (tagsFilter) {
      const filterTags = tagsFilter
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0);
      tagsMatch = filterTags.some((tag) => itemTags.includes(tag));
    }

    const locationMatch =
      !locationFilter || itemLocation.includes(locationFilter);

    // Show if search matches or all specific filters match (if any have values)
    const hasSpecificFilters = nameFilter || tagsFilter || locationFilter;
    const shouldShow =
      searchMatch &&
      (!hasSpecificFilters || (nameMatch && tagsMatch && locationMatch));

    if (shouldShow) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}

function clearFilters() {
  document.getElementById("search-input").value = "";
  document.getElementById("filter-name").value = "";
  document.getElementById("filter-tags").value = "";
  document.getElementById("filter-location").value = "";

  // Show all rows
  const rows = document.querySelectorAll("#items-table-body tr");
  rows.forEach((row) => {
    row.style.display = "";
  });
}

// Make functions global for HTML onclick handlers
window.filterTable = filterTable;
window.clearFilters = clearFilters;

// Make updateStats globally accessible
window.updateStats = updateStats;

// Function to delete an item
async function deleteItem(itemId) {
  // Store the item ID in a data attribute on the confirm button
  const confirmBtn = document.getElementById("confirmDeleteBtn");
  confirmBtn.setAttribute("data-item-id", itemId);

  // Show the modal
  const modal = new bootstrap.Modal(
    document.getElementById("deleteConfirmModal")
  );
  modal.show();
}

// Handle the actual deletion when confirmed
document.addEventListener("DOMContentLoaded", () => {
  console.log("Home.js loaded - DOMContentLoaded event fired");
  console.log("Navbar function available:", typeof Navbar);
  console.log("Window userData:", window.userData);
  
  fetchItems();
  filterTable();

  // Initialize Navbar using the global Navbar function (loaded via script tag)
  const navbarContainer = document.getElementById("navbar");
  console.log("Navbar container element:", navbarContainer);
  
  if (typeof Navbar === 'function' && window.userData) {
    console.log("Attempting to render navbar with data:", window.userData);
    const navbarHTML = Navbar({
      profilePicture: window.userData.profilePicture,
      firstName: window.userData.firstName,
      role: window.userData.role,
      homeUrl: window.userData.homeUrl
    });
    console.log("Generated navbar HTML:", navbarHTML);
    
    if (navbarContainer) {
      navbarContainer.innerHTML = navbarHTML;
      console.log("Navbar HTML inserted into container");
    } else {
      console.error("Navbar container element not found!");
    }

    // Set up logout button handler after navbar is loaded
    setTimeout(() => {
      const logoutButton = document.getElementById("logoutButton");
      console.log("Logout button found:", logoutButton);
      if (logoutButton) {
        logoutButton.addEventListener("click", () => {
          window.location.href = "/auth/logout";
        });
        console.log("Logout button click handler added");
      }
    }, 100);
  } else {
    console.error("Navbar function not available or user data missing");
    console.error("Navbar function type:", typeof Navbar);
    console.error("User data:", window.userData);
  }

  // Set up delete confirmation button handler
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", async function () {
      const itemId = this.getAttribute("data-item-id");

      if (!itemId) {
        console.error("No item ID found");
        return;
      }

      // Disable button during deletion
      this.disabled = true;
      // this.innerHTML =
      //   '<span class="spinner-border spinner-border-sm me-2"></span>Deleting...';

      try {
        const response = await fetch(`${API_PREFIX}/items/${itemId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close the modal
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("deleteConfirmModal")
        );
        modal.hide();

        // Remove the row from the table
        const rows = document.querySelectorAll("#items-table-body tr");
        rows.forEach((row) => {
          const deleteBtn = row.querySelector(
            `button[onclick="deleteItem(${itemId})"]`
          );
          if (deleteBtn) {
            row.classList.add("table-danger");
            setTimeout(() => {
              row.remove();
              // Refresh table and stats
              fetchItems();
              updateStats();
            }, 500);
          }
        });
      } catch (error) {
        console.error("Failed to delete item:", error);
        alert("Failed to delete item. Please try again.");
      } finally {
        // Re-enable button
        this.disabled = false;
        this.innerHTML = "Delete Item";
      }
    });
  }
});
