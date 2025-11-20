const API_BASE = '/api/v1/camera_gear';



document.addEventListener('DOMContentLoaded', function () {
    loadCameraGear();

    // Open modal in "create" mode
    const addBtn = document.getElementById('openAddItemBtn');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            window.editingItemId = null;
            window.editingItemData = null;
            const titleEl = document.getElementById("addItemModalLabel");
            const submitBtn = document.getElementById("createItemBtn");
            if (titleEl) titleEl.textContent = "Add Camera Gear";
            if (submitBtn) {
                Array.from(submitBtn.childNodes)
                    .filter(n => n.nodeType === Node.TEXT_NODE)
                    .forEach(n => n.remove());
                submitBtn.appendChild(document.createTextNode(" Create"));
            }
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
        console.error('Error loading camera gear:', error);
        alert('Failed to load camera gear');
    }
}



// Display camera gear in table
function displayCameraGear(gear) {
    const tbody = document.getElementById('items-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!Array.isArray(gear) || gear.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.dataset.empty = "true";
        emptyRow.innerHTML = `
          <td colspan="7" class="text-center text-muted">
            No camera gear found.
          </td>
        `;
        tbody.appendChild(emptyRow);
        return;
    }

    gear.forEach(item => {
        const row = buildCameraGearRow(item);
        tbody.appendChild(row);
    });
}




/// Edit camera gear – open the modal and let add_gear_modal.js prefill the form
async function editCameraGear(id) {
    try {
        const response = await fetch(`${API_BASE}/one/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch camera gear: ${response.status}`);
        }

        const item = await response.json();

        // Make the fetched item available for the modal initializer
        window.editingItemData = item;
        window.editingItemId = id;

        // Update modal title + button label (parallel to equipment)
        const titleEl = document.getElementById("addItemModalLabel");
        const submitBtn = document.getElementById("createItemBtn");
        if (titleEl) titleEl.textContent = "Edit Camera Gear";
        if (submitBtn) {
            for (const node of Array.from(submitBtn.childNodes)) {
                if (node.nodeType === Node.TEXT_NODE) {
                    node.nodeValue = " Save Changes";
                    break;
                }
            }
        }

        // Show the modal – its 'shown.bs.modal' listener will read window.editingItemData
        const modalEl = document.getElementById("addItemModal");
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    } catch (error) {
        console.error('Error loading camera gear for edit:', error);
        alert('Failed to load camera gear for editing: ' + error.message);
    }
}


// Check out camera gear
async function checkOutGear(id) {
    if (!confirm('Are you sure you want to check out this camera gear?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/checkout/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            loadCameraGear();
            alert('Camera gear checked out successfully!');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to check out camera gear');
        }
    } catch (error) {
        console.error('Error checking out camera gear:', error);
        alert('Failed to check out camera gear: ' + error.message);
    }
}

// Check in camera gear
async function checkInGear(id) {
    if (!confirm('Are you sure you want to check in this camera gear?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/checkin/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            loadCameraGear();
            alert('Camera gear checked in successfully!');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to check in camera gear');
        }
    } catch (error) {
        console.error('Error checking in camera gear:', error);
        alert('Failed to check in camera gear: ' + error.message);
    }
}

// Delete camera gear
async function deleteCameraGear(id) {
    if (!confirm('Are you sure you want to delete this camera gear?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadCameraGear();
            alert('Camera gear deleted!');
        } else {
            const errorText = await response.text();
            throw new Error(`Failed to delete camera gear: ${errorText}`);
        }
    } catch (error) {
        console.error('Error deleting camera gear:', error);
        alert('Failed to delete camera gear: ' + error.message);
    }
}


// Helper to build a table row for a single camera gear item
function buildCameraGearRow(item) {
    const row = document.createElement('tr');
    row.classList.add(`item-id-${item.id}`);

    const isCheckedOut = !!item.checked_out_by;
    if (isCheckedOut) {
        row.classList.add('checked-out-row');
    }

    const statusHtml = isCheckedOut
        ? '<span class="badge bg-warning">Checked Out</span>'
        : '<span class="badge bg-success">Available</span>';

    // tags may be ["name"] or [{name: ""}] or a plain string
    let tagsText = '—';
    if (Array.isArray(item.tags) && item.tags.length) {
        tagsText = item.tags
            .map(t => (typeof t === 'string' ? t : t?.name || ''))
            .filter(Boolean)
            .join(', ') || '—';
    } else if (typeof item.tags === 'string') {
        tagsText = item.tags || '—';
    }

    const locationName = item.location || '—';
    const checkedOutBy = item.checked_out_by || '—';

    const actionsHtml = `
      <button class="btn btn-sm btn-link text-primary p-0 me-2"
              onclick="editCameraGear(${item.id})" title="Edit">
        <i class="fas fa-edit"></i>
      </button>
      ${
        isCheckedOut
          ? `<button class="btn btn-sm btn-link text-info p-0 me-2"
                    onclick="checkInGear(${item.id})" title="Check In">
               <i class="fas fa-sign-in-alt"></i>
             </button>`
          : `<button class="btn btn-sm btn-link text-success p-0 me-2"
                    onclick="checkOutGear(${item.id})" title="Check Out">
               <i class="fas fa-sign-out-alt"></i>
             </button>`
      }
      <button class="btn btn-sm btn-link text-danger p-0"
              onclick="deleteCameraGear(${item.id})" title="Delete">
        <i class="fas fa-trash"></i>
      </button>
    `;

    row.innerHTML = `
      <td>${item.id}</td>
      <td>${item.name || ''}</td>
      <td>${tagsText}</td>
      <td>${locationName}</td>
      <td>${statusHtml}</td>
      <td>${checkedOutBy}</td>
      <td class="text-end">${actionsHtml}</td>
    `;

    return row;
}

// Called by add_gear_modal.js after a successful CREATE
window.addItemToTable = function (item) {
    const tbody = document.getElementById('items-table-body');
    if (!tbody) return;

    const emptyRow = tbody.querySelector('tr[data-empty="true"]');
    if (emptyRow) emptyRow.remove();

    const row = buildCameraGearRow(item);
    tbody.prepend(row);
};

// Called by add_gear_modal.js after a successful UPDATE
window.updateItemInTable = function (item) {
    const tbody = document.getElementById('items-table-body');
    if (!tbody) return;

    const existingRow = tbody.querySelector(`tr.item-id-${item.id}`);
    const row = buildCameraGearRow(item);

    if (existingRow) {
        existingRow.replaceWith(row);
    } else {
        tbody.prepend(row);
    }
};


// Make functions global for onclick handlers
window.editCameraGear = editCameraGear;
window.deleteCameraGear = deleteCameraGear;
window.checkOutGear = checkOutGear;
window.checkInGear = checkInGear;

