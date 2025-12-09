const API_BASE = "/api/v1/lab_equipment";

// Load equipment on page load
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Navbar
  if (typeof Navbar === "function" && window.userData) {
    const navbarContainer = document.getElementById("navbar");
    if (navbarContainer) {
      navbarContainer.innerHTML = Navbar({
        profilePicture: window.userData.profilePicture,
        firstName: window.userData.firstName,
        role: window.userData.role,
        homeUrl: window.userData.homeUrl,
      });

      // Set up logout button handler after navbar is loaded
      setTimeout(() => {
        const logoutButton = document.getElementById("logoutButton");
        if (logoutButton) {
          logoutButton.addEventListener("click", () => {
            window.location.href = "/auth/logout";
          });
        }
      }, 100);
    }
  }

  // Initialize Breadcrumbs
  if (typeof Breadcrumbs === "function" && window.userData) {
    const breadcrumbsContainer = document.getElementById("breadcrumbs");
    if (breadcrumbsContainer) {
      breadcrumbsContainer.innerHTML = Breadcrumbs({
        currentPage: "Lab Equipment",
        userRole: window.userData.role,
      });
    }
  }

  loadEquipment();
  setupDeleteHandler();

  // Load notes cache
  if (typeof loadNotesCache === "function") {
    loadNotesCache();
  }
});

// Load all equipment
async function loadEquipment() {
  try {
    const response = await fetch(`${API_BASE}/all`);
    const data = await response.json();
    const equipment = data.lab_equipment || [];

    // Initialize pagination
    Pagination.init(equipment);
    Pagination.setOnPageChange(() => {
      renderPaginatedTable();
    });

    renderPaginatedTable();
    Pagination.render();
  } catch (error) {
    console.error("Error loading equipment:", error);
    showEmptyState("Failed to load lab equipment");
  }
}

// Function to render table with pagination
function renderPaginatedTable() {
  const tbody = document.getElementById("lab-equipment-table-body");
  if (!tbody) return;

  tbody.innerHTML = "";
  const itemsToShow = Pagination.getCurrentPageItems();

  if (!itemsToShow || itemsToShow.length === 0) {
    showEmptyState('No lab equipment found. Click "Add Item" to get started.');
    return;
  }

  itemsToShow.forEach((item) => {
    const row = document.createElement("tr");

    // Format dates and values using centralized functions
    const lastServiced = item.last_serviced_on
      ? formatDateDisplay(item.last_serviced_on)
      : EMPTY_PLACEHOLDER;
    const lastUpdated = formatDateDisplay(item.last_updated, true);
    const tags = formatTagsDisplay(item.tags);
    const name = formatDisplayValue(item.name);
    const serviceFreq = formatDisplayValue(item.service_frequency);
    const lastServicedBy = formatDisplayValue(item.last_serviced_by);

    row.innerHTML = LabRow(
      item.id,
      name,
      tags,
      serviceFreq,
      lastServiced,
      lastServicedBy,
      lastUpdated,
      item,
      typeof itemHasNote === "function"
        ? itemHasNote("lab_equipment", item.id)
        : false
    );
    tbody.appendChild(row);

    // Open notes modal
    row.style.cursor = "pointer";
    row.addEventListener("click", function (e) {
      if (e.target.closest("button") || e.target.closest("a")) {
        return;
      }
      if (typeof openNotesModal === "function") {
        openNotesModal("lab_equipment", item.id, name);
      }
    });
  });
}
window.refreshTablesWithNotes = renderPaginatedTable;

// Display equipment in table
function displayEquipment(equipment) {
  Pagination.init(equipment || []);
  Pagination.setOnPageChange(() => {
    renderPaginatedTable();
  });

  renderPaginatedTable();
  Pagination.render();
}

// Show empty state
function showEmptyState(message) {
  const tbody = document.getElementById("lab-equipment-table-body");
  if (!tbody) return;
  const row = document.createElement("tr");
  row.innerHTML = `
        <td colspan="8" class="text-center text-muted py-4">
            ${message}
        </td>
    `;
  tbody.appendChild(row);
}

// Open edit modal
async function openEditModal(itemId) {
  try {
    const response = await fetch(`${API_BASE}/one/${itemId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch equipment: ${response.status}`);
    }

    const item = await response.json();

    // Make the fetched item available for the modal initializer
    window.editingItemData = item;
    window.editingItemId = itemId;

    // Update modal UI elements
    const titleEl = document.getElementById("addItemModalLabel");
    const submitBtn = document.getElementById("createItemBtn");
    if (titleEl) titleEl.textContent = "Edit Lab Equipment";
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

    // Show modal - the modal's shown handler will prefill
    const modalEl = document.getElementById("addItemModal");
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  } catch (error) {
    console.error("Error opening edit modal:", error);
    alert("Failed to load equipment for editing:" + error.message);
  }
}

// Delete equipment
async function deleteEquipment(id) {
  const confirmBtn = document.getElementById("confirmDeleteBtn");
  if (confirmBtn) {
    confirmBtn.setAttribute("data-item-id", id);
    const modal = new bootstrap.Modal(
      document.getElementById("deleteConfirmModal")
    );
    modal.show();
  }
}

// Setup delete confirmation handler
function setupDeleteHandler() {
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", async function () {
      const itemId = this.getAttribute("data-item-id");
      if (!itemId) return;

      this.disabled = true;

      try {
        const response = await fetch(`${API_BASE}/${itemId}`, {
          method: "DELETE",
        });

        if (response.ok) {
          const modal = bootstrap.Modal.getInstance(
            document.getElementById("deleteConfirmModal")
          );
          if (modal) modal.hide();

          // Remove from pagination data and refresh
          const allItems = Pagination.getAllItems();
          const filteredItems = allItems.filter((item) => item.id != itemId);
          Pagination.init(filteredItems);
          Pagination.setOnPageChange(() => {
            renderPaginatedTable();
          });
          renderPaginatedTable();
          Pagination.render();
        } else {
          throw new Error("Failed to delete equipment");
        }
      } catch (error) {
        console.error("Error deleting equipment:", error);
        alert("Failed to delete equipment:" + error.message);
      } finally {
        this.disabled = false;
      }
    });
  }
}

// Add item to table (called from modal)
window.addLabEquipmentToTable = function (item) {
  // Get current items and add new one
  const allItems = Pagination.getAllItems();
  allItems.unshift(item);

  // Reinitialize pagination with updated items
  Pagination.init(allItems);
  Pagination.setOnPageChange(() => {
    renderPaginatedTable();
  });

  // Render table and pagination
  renderPaginatedTable();
  Pagination.render();
};

// Update item in table (called from modal)
window.updateLabEquipmentInTable = function (data) {
  loadEquipment();
};

// Filter table
function filterTable() {
  const searchValue =
    document.getElementById("search-input")?.value.toLowerCase() || "";
  const nameFilter =
    document.getElementById("filter-name")?.value.toLowerCase() || "";
  const tagsFilter =
    document.getElementById("filter-tags")?.value.toLowerCase() || "";
  const serviceFrequencyFilter =
    document.getElementById("filter-service-frequency")?.value || "";

  // Get all items from pagination
  const allItems = Pagination.getAllItems();

  // Filter items
  const filteredItems = allItems.filter((item) => {
    const itemName = (item.name || "").toLowerCase();
    const itemTags = Array.isArray(item.tags)
      ? item.tags.join(", ").toLowerCase()
      : (item.tags || "").toLowerCase();
    const itemServiceFreq = (item.service_frequency || "").toLowerCase();

    const searchMatch =
      !searchValue ||
      itemName.includes(searchValue) ||
      itemTags.includes(searchValue);

    const nameMatch = !nameFilter || itemName.includes(nameFilter);
    const tagsMatch =
      !tagsFilter || itemTags.includes(tagsFilter.toLowerCase());
    const serviceFreqMatch =
      !serviceFrequencyFilter ||
      itemServiceFreq.includes(serviceFrequencyFilter.toLowerCase());

    const hasSpecificFilters =
      nameFilter || tagsFilter || serviceFrequencyFilter;
    return (
      searchMatch &&
      (!hasSpecificFilters || (nameMatch && tagsMatch && serviceFreqMatch))
    );
  });

  // Update pagination with filtered items
  Pagination.setFilteredItems(filteredItems);

  // Re-render table and pagination
  renderPaginatedTable();
  Pagination.render();
}

function clearFilters() {
  document.getElementById("search-input").value = "";
  document.getElementById("filter-name").value = "";
  document.getElementById("filter-tags").value = "";
  document.getElementById("filter-service-frequency").value = "";

  // Reset to show all items
  const allItems = Pagination.getAllItems();
  Pagination.setFilteredItems(allItems);
  renderPaginatedTable();
  Pagination.render();
}

// Make functions global
window.openEditModal = openEditModal;
window.deleteEquipment = deleteEquipment;
window.filterTable = filterTable;
window.clearFilters = clearFilters;
