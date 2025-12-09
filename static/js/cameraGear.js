const API_BASE = "/api/v1/camera_gear";

function renderCameraRow(
    id,
    name,
    tags,
    locationName,
    status,
    checkedOutBy,
    lastUpdated,
    editButton,
    toggleCheckoutButton,
    deleteButton,
) {
    const canEditOrDelete =
        window.userData &&
        (window.userData.role === "Admin" || window.userData.role === "Manager");
    return canEditOrDelete
        ? `
            <td>${id}</td>
            <td>${formatDisplayValue(name)}</td>
            <td>${tags}</td>
            <td>${locationName}</td>
            <td>${status}</td>
            <td>${checkedOutBy}</td>
            <td>${lastUpdated}</td>
            <td class="text-end">
                <div class="d-inline-flex gap-2 align-items-center">
                    ${editButton}
                    ${toggleCheckoutButton}
                    ${deleteButton}
                </div>
            </td>
        `
        : `<td>${id}</td>
            <td>${formatDisplayValue(name)}</td>
            <td>${tags}</td>
            <td>${locationName}</td>
            <td>${status}</td>
            <td>${checkedOutBy}</td>
            <td>${lastUpdated}</td>
            <td class="text-end">
                <div class="d-inline-flex gap-2 align-items-center">
                    ${toggleCheckoutButton}
                </div>
            </td>
        `;
}

// Load camera gear on page load
document.addEventListener("DOMContentLoaded", function() {
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
                currentPage: "Camera Gear",
                userRole: window.userData.role,
            });
        }
    }

    loadCameraGear();
    setupDeleteHandler();
});

// Load all camera gear
async function loadCameraGear() {
    try {
        const response = await fetch(`${API_BASE}/all`);
        const data = await response.json();
        const gear = data.camera_gear || [];

        // Initialize pagination
        Pagination.init(gear);
        Pagination.setOnPageChange(() => {
            renderPaginatedTable();
        });

        renderPaginatedTable();
        Pagination.render();
    } catch (error) {
        console.error("Error loading camera gear:", error);
        showEmptyState("Failed to load camera gear");
    }
}

// Function to render table with pagination
function renderPaginatedTable() {
    const tbody = document.getElementById("items-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    const itemsToShow = Pagination.getCurrentPageItems();

    if (!itemsToShow || itemsToShow.length === 0) {
        showEmptyState('No camera gear found. Click "Add Item" to get started.');
        return;
    }

    itemsToShow.forEach((item) => {
        const row = document.createElement("tr");

        // Determine checkout status
        const isCheckedOut = item.checked_out_by;
        const status = isCheckedOut
            ? '<span class="badge rounded-pill bg-warning-subtle text-warning-emphasis border border-warning-subtle">Checked Out</span>'
            : '<span class="badge rounded-pill bg-success-subtle text-success-emphasis border border-success-subtle">Available</span>';

        // Add checked-out styling
        if (isCheckedOut) {
            row.classList.add("checked-out-row");
        }

        // Use location name directly from API response
        const locationName = formatDisplayValue(item.location);
        const tags = formatTagsDisplay(item.tags);
        const checkedOutBy = formatDisplayValue(item.checked_out_by);
        const lastUpdated = formatDateDisplay(item.last_updated, true);

        const editButton = `
            <button class="btn btn-sm btn-link text-primary p-0 me-2" onclick="openEditModal(${item.id})" title="Edit item">
                <i class="fas fa-edit"></i>
            </button>`;

        const toggleCheckoutButton = isCheckedOut
            ? `
            <button class="btn btn-sm btn-link text-info p-0 me-2" onclick="checkInGear(${item.id})" title="Check In">
                <i class="fas fa-sign-in-alt"></i>
            </button>`
            : `
            <button class="btn btn-sm btn-link text-success p-0 me-2" onclick="checkOutGear(${item.id})" title="Check Out">
                <i class="fas fa-sign-out-alt"></i>
            </button>`;

        const deleteButton = `
            <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteCameraGear(${item.id})" title="Delete item">
                <i class="fas fa-trash"></i>
            </button>`;

        row.innerHTML = CameraRow(
            item.id,
            item.name,
            tags,
            locationName,
            status,
            checkedOutBy,
            lastUpdated,
            editButton,
            toggleCheckoutButton,
            deleteButton,
        );
        tbody.appendChild(row);
    });
}

// Display camera gear in table
function displayCameraGear(gear) {
    Pagination.init(gear || []);
    Pagination.setOnPageChange(() => {
        renderPaginatedTable();
    });

    renderPaginatedTable();
    Pagination.render();
}

// Show empty state
function showEmptyState(message) {
    const tbody = document.getElementById("items-table-body");
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
        console.error("Error loading camera gear for edit:", error);
        alert("Failed to load camera gear for editing: " + error.message);
    }
}

// Check out camera gear
async function checkOutGear(id) {
    if (!confirm("\nColby College Photography:\n\nBy signing out this equipment, I understand that I take liability for its proper care and keeping, and will be responsible for any damages or loss.\n\nI have verified with with Prof. Nelson, and I have filled out the proper paperwork before checking out this equipment")) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/checkout/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
        });

        if (response.ok) {
            // Reload data from server to get updated checkout status
            loadCameraGear();
            alert("Camera gear checked out successfully!");
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
    if (!confirm("\nColby College Photography:\n\nBefore checking in this equipment, I have verified with with Prof. Nelson, and I have filled out the proper check-in paperwork")) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/checkin/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
        });

        if (response.ok) {
            // Reload data from server to get updated checkout status
            loadCameraGear();
            alert("Camera gear checked in successfully!");
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
            document.getElementById("deleteConfirmModal"),
        );
        modal.show();
    }
}

// Setup delete confirmation handler
function setupDeleteHandler() {
    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener("click", async function() {
            const itemId = this.getAttribute("data-item-id");
            if (!itemId) return;

            this.disabled = true;

            try {
                const response = await fetch(`${API_BASE}/${itemId}`, {
                    method: "DELETE",
                });

                if (response.ok) {
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("deleteConfirmModal"),
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
                    const errorText = await response.text();
                    throw new Error(`Failed to delete camera gear: ${errorText}`);
                }
            } catch (error) {
                console.error("Error deleting camera gear:", error);
                alert("Failed to delete camera gear: " + error.message);
            }
        });
    }
}

// Add item to table (called from modal)
window.addCameraGearToTable = function(item) {
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
window.updateCameraGearInTable = function(data) {
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

    // Get all items from pagination
    const allItems = Pagination.getAllItems();

    // Filter items
    const filteredItems = allItems.filter((item) => {
        const itemName = (item.name || "").toLowerCase();
        const itemTags = Array.isArray(item.tags)
            ? item.tags.join(", ").toLowerCase()
            : (item.tags || "").toLowerCase();
        const itemLocation = (item.location || "").toLowerCase();
        const isCheckedOut = !!item.checked_out_by;
        const itemStatus = isCheckedOut ? "checked out" : "available";

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
            (statusFilter === "available" && !isCheckedOut) ||
            (statusFilter === "checked-out" && isCheckedOut);

        const hasSpecificFilters =
            nameFilter || tagsFilter || locationFilter || statusFilter;
        return (
            searchMatch &&
            (!hasSpecificFilters ||
                (nameMatch && tagsMatch && locationMatch && statusMatch))
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
    document.getElementById("filter-location").value = "";
    document.getElementById("filter-status").value = "";

    // Reset to show all items
    const allItems = Pagination.getAllItems();
    Pagination.setFilteredItems(allItems);
    renderPaginatedTable();
    Pagination.render();
}

// Make functions global
window.openEditModal = openEditModal;
window.deleteCameraGear = deleteCameraGear;
window.checkOutGear = checkOutGear;
window.checkInGear = checkInGear;
window.filterTable = filterTable;
window.clearFilters = clearFilters;
