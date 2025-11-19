const API_BASE = "/api/v1/camera_gear";

// Load camera gear on page load
document.addEventListener("DOMContentLoaded", function () {
  loadCameraGear();
  setupDeleteHandler();

  // Logout button
  const logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      window.location.href = "/auth/logout";
    });
  }
});

// Load all camera gear
async function loadCameraGear() {
  try {
    const response = await fetch(`${API_BASE}/all`);
    const data = await response.json();
    displayCameraGear(data.camera_gear || []);
  } catch (error) {
    console.error("Error loading camera gear:", error);
    showEmptyState("Failed to load camera gear");
  }
}

// Display camera gear in table
function displayCameraGear(gear) {
  const tbody = document.getElementById("camera-gear-table-body");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (gear.length === 0) {
    showEmptyState('No camera gear found. Click "Add Item" to get started.');
    return;
  }

  gear.forEach((item) => {
    const row = document.createElement("tr");

    // Determine checkout status
    const isCheckedOut = item.checked_out_by;
    const status = isCheckedOut
      ? '<span class="badge bg-warning">Checked Out</span>'
      : '<span class="badge bg-success">Available</span>';

    // Add checked-out styling
    if (isCheckedOut) {
      row.classList.add("checked-out-row");
    }

    // Use location name directly from API response
    const locationName = item.location || "—";
    const tags = Array.isArray(item.tags)
      ? item.tags.join(", ")
      : item.tags || "";
    const lastUpdated = item.last_updated
      ? new Date(item.last_updated).toLocaleString()
      : "—";

    row.innerHTML = `
            <td class="text-center">${item.id}</td>
            <td class="text-start">${item.name}</td>
            <td class="text-start">${tags}</td>
            <td class="text-start">${locationName}</td>
            <td class="text-center">${status}</td>
            <td class="text-center">${item.checked_out_by || "—"}</td>
            <td class="text-center">${lastUpdated}</td>
            <td class="text-end">
                <div class="d-inline-flex gap-2 align-items-center">
                    <button class="btn btn-sm btn-warning me-1" onclick="openEditModal(${
                      item.id
                    })" title="Edit item">
                        Edit
                    </button>
                    ${
                      isCheckedOut
                        ? `<button class="btn btn-sm btn-info me-1" onclick="checkInGear(${item.id})" title="Check In" style="white-space: nowrap;">
                            Check In
                        </button>`
                        : `<button class="btn btn-sm btn-success me-1" onclick="checkOutGear(${item.id})" title="Check Out" style="white-space: nowrap;">
                            Check Out
                        </button>`
                    }
                    <button class="btn btn-sm btn-danger" onclick="deleteCameraGear(${
                      item.id
                    })" title="Delete item">
                        Delete
                    </button>
                </div>
            </td>
        `;
    tbody.appendChild(row);
  });
}

// Show empty state
function showEmptyState(message) {
  const tbody = document.getElementById("camera-gear-table-body");
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
      throw new Error(`Failed to fetch camera gear: ${response.status}`);
    }

    const item = await response.json();

    // Make the fetched item available for the modal initializer
    window.editingItemData = item;
    window.editingItemId = itemId;

    // Update modal UI elements
    const titleEl = document.getElementById("addItemModalLabel");
    const submitBtn = document.getElementById("createItemBtn");
    if (titleEl) titleEl.textContent = "Edit Camera Gear";
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
    alert("Failed to load camera gear for editing");
  }
}

// Check out camera gear
async function checkOutGear(id) {
  try {
    const response = await fetch(`${API_BASE}/checkout/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    });

    if (response.ok) {
      loadCameraGear();
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to check out camera gear");
    }
  } catch (error) {
    console.error("Error checking out camera gear:", error);
    alert("Failed to check out camera gear: " + error.message);
  }
}

// Check in camera gear
async function checkInGear(id) {
  try {
    const response = await fetch(`${API_BASE}/checkin/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    });

    if (response.ok) {
      loadCameraGear();
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to check in camera gear");
    }
  } catch (error) {
    console.error("Error checking in camera gear:", error);
    alert("Failed to check in camera gear: " + error.message);
  }
}

// Delete camera gear
async function deleteCameraGear(id) {
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
          loadCameraGear();
        } else {
          throw new Error("Failed to delete camera gear");
        }
      } catch (error) {
        console.error("Error deleting camera gear:", error);
        alert("Failed to delete camera gear");
      } finally {
        this.disabled = false;
      }
    });
  }
}

// Add item to table (called from modal)
window.addCameraGearToTable = function (item) {
  loadCameraGear();
};

// Update item in table (called from modal)
window.updateCameraGearInTable = function (data) {
  loadCameraGear();
};

// Filter table
function filterTable() {
  const searchValue =
    document.getElementById("search-input")?.value.toLowerCase() || "";
  const nameFilter =
    document.getElementById("filter-name")?.value.toLowerCase() || "";
  const tagsFilter =
    document.getElementById("filter-tags")?.value.toLowerCase() || "";
  const locationFilter =
    document.getElementById("filter-location")?.value.toLowerCase() || "";
  const statusFilter = document.getElementById("filter-status")?.value || "";

  const rows = document.querySelectorAll("#camera-gear-table-body tr");

  rows.forEach((row) => {
    if (row.querySelector("td[colspan]")) return; // Skip empty state row

    const cells = row.cells;
    if (cells.length < 8) return;

    const itemName = cells[1].textContent.toLowerCase();
    const itemTags = cells[2].textContent.toLowerCase();
    const itemLocation = cells[3].textContent.toLowerCase();
    const itemStatus = cells[4].textContent.toLowerCase();

    const searchMatch =
      !searchValue ||
      itemName.includes(searchValue) ||
      itemTags.includes(searchValue) ||
      itemLocation.includes(searchValue);

    const nameMatch = !nameFilter || itemName.includes(nameFilter);
    const tagsMatch =
      !tagsFilter || itemTags.includes(tagsFilter.toLowerCase());
    const locationMatch =
      !locationFilter || itemLocation.includes(locationFilter);
    const statusMatch =
      !statusFilter ||
      (statusFilter === "available" && itemStatus.includes("available")) ||
      (statusFilter === "checked-out" && itemStatus.includes("checked out"));

    const hasSpecificFilters =
      nameFilter || tagsFilter || locationFilter || statusFilter;
    const shouldShow =
      searchMatch &&
      (!hasSpecificFilters ||
        (nameMatch && tagsMatch && locationMatch && statusMatch));

    row.style.display = shouldShow ? "" : "none";
  });
}

function clearFilters() {
  document.getElementById("search-input").value = "";
  document.getElementById("filter-name").value = "";
  document.getElementById("filter-tags").value = "";
  document.getElementById("filter-location").value = "";
  document.getElementById("filter-status").value = "";
  filterTable();
}

// Make functions global
window.openEditModal = openEditModal;
window.deleteCameraGear = deleteCameraGear;
window.checkOutGear = checkOutGear;
window.checkInGear = checkInGear;
window.filterTable = filterTable;
window.clearFilters = clearFilters;
