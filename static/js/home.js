// Function to fetch items from the server
async function fetchItems() {
  try {
    console.log("Fetching items from /items/all");
    const response = await fetch("/items/all");
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
      const expires = item.expires
        ? new Date(item.expires).toLocaleDateString()
        : "";
      const lastUpdated = item.last_updated
        ? new Date(item.last_updated).toLocaleString()
        : "";

      row.innerHTML = `
                <td>${item.id || ""}</td>
                <td>${item.name || ""}</td>
                <td>${item.quantity || ""}</td>
                <td>${tags}</td>
                <td>${item.location || ""}</td>
                <td>${expires}</td>
                <td>${lastUpdated}</td>
                <td>${item.updated_by || ""}</td>
            `;
      row.classList.add("item-row");

      tableBody.appendChild(row);
    });
  } else {
    showEmptyState("No items found. Click 'Add Item' to get started.");
  }
}

// Function to show empty state
function showEmptyState(message) {
  const tableBody = document.getElementById("items-table-body");
  const row = document.createElement("tr");
  row.innerHTML = `
		<td colspan="8" class="text-center text-muted py-4">
			${message}
		</td>
	`;
  tableBody.appendChild(row);
}

// Function to calculate and update stats
async function updateStats() {
  try {
    const response = await fetch("/items/all");
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
  const noItemsRow = tableBody.querySelector('td[colspan="8"]');
  if (noItemsRow) {
    noItemsRow.parentElement.remove();
  }

  // Create new row - handle both response formats
  const row = document.createElement("tr");
  const tags = Array.isArray(item.tags)
    ? item.tags.join(", ")
    : item.tags || "";
  const expires = item.expires
    ? new Date(item.expires).toLocaleDateString()
    : "";
  const last_updated = item.last_updated
    ? new Date(item.last_updated).toLocaleString()
    : "";

  row.innerHTML = `
		<td>${item.id || ""}</td>
		<td>${item.name || ""}</td>
		<td>${item.quantity || ""}</td>
		<td>${tags}</td>
		<td>${item.location || item.location_id || ""}</td>
		<td>${expires}</td>
		<td>${last_updated}</td>
		<td>${item.updated_by || ""}</td>
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
    if (row.querySelector('td[colspan="8"]')) {
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

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("Home.js loaded");
  fetchItems();
  filterTable();
});

document.getElementById("logoutButton").addEventListener("click", () => {
  window.location.href = "/auth/logout";
});
