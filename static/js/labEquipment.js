const API_BASE = '/api/v1/lab_equipment';

let isEditing = false;
let editingId = null;
let allTags = [];
let selectedTags = [];

// Load equipment on page load
document.addEventListener('DOMContentLoaded', function () {
    loadEquipment();
});


// Load all equipment
async function loadEquipment() {
    try {
        const response = await fetch(`${API_BASE}/all`);
        const data = await response.json();
        displayEquipment(data.lab_equipment || []);
    } catch (error) {
        console.error('Error loading equipment:', error);
        alert('Failed to load equipment');
    }
}

// Load all tags
async function loadTags() {
    try {
        const response = await fetch('/api/v1/tags/all');
        const data = await response.json();
        allTags = data.tags || [];
    } catch (error) {
        console.error('Error loading tags:', error);
    }
}

function displayEquipment(equipment) {
    const tbody = document.getElementById('items-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!Array.isArray(equipment) || equipment.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.dataset.empty = "true";
        emptyRow.innerHTML = `
      <td colspan="7" class="text-center text-muted">No equipment found.</td>
    `;
        tbody.appendChild(emptyRow);
        return;
    }

    equipment.forEach(item => {
        const row = document.createElement('tr');
        row.classList.add(`item-id-${item.id}`);

        const lastServiced = item.last_serviced_on
            ? new Date(item.last_serviced_on).toLocaleDateString()
            : '—';

        const serviceFreq = item.service_frequency || '—';

        // tags may be ["name"] or [{name:""}]
        let tagsText = '—';
        if (Array.isArray(item.tags) && item.tags.length) {
            tagsText = item.tags
                .map(t => (typeof t === 'string' ? t : t?.name || ''))
                .filter(Boolean)
                .join(', ') || '—';
        }

        const lastServicedBy = item.last_serviced_by || '—';

        row.innerHTML = `
      <td>${item.id}</td>
      <td>${item.name || ''}</td>
      <td>${tagsText}</td>
      <td>${serviceFreq}</td>
      <td>${lastServiced}</td>
      <td>${lastServicedBy}</td>
      <td class="text-end">
        <button class="btn btn-sm btn-link text-primary p-0 me-2"
                onclick="editEquipment(${item.id})" title="Edit">
          <i class="fas fa-edit"></i>
        </button>
        <button class="btn btn-sm btn-link text-danger p-0"
                onclick="deleteEquipment(${item.id})" title="Delete">
          <i class="fas fa-trash"></i>
        </button>
      </td>
    `;
        tbody.appendChild(row);
    });
}



// Setup tag input functionality
function setupTagInput() {
    const tagsInput = document.getElementById('tags');
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'tags-container mb-2';
    tagsInput.parentNode.insertBefore(tagsContainer, tagsInput);

    // Create tag input wrapper
    const tagInputWrapper = document.createElement('div');
    tagInputWrapper.className = 'tag-input-wrapper';
    tagInputWrapper.innerHTML = `
        <input type="text" class="form-control" id="tagInput" placeholder="Type to search or add tags...">
        <div id="tagDropdown" class="tag-dropdown" style="display: none;"></div>
    `;
    tagsInput.parentNode.insertBefore(tagInputWrapper, tagsInput);

    // Hide original tags input
    tagsInput.style.display = 'none';

    const tagInput = document.getElementById('tagInput');
    const tagDropdown = document.getElementById('tagDropdown');

    // Handle tag input
    tagInput.addEventListener('input', function (e) {
        const query = e.target.value.trim().toLowerCase();

        if (query === '') {
            tagDropdown.style.display = 'none';
            return;
        }

        // Filter tags that match query and aren't selected
        const matchingTags = allTags.filter(tag =>
            tag.name.toLowerCase().includes(query) &&
            !selectedTags.includes(tag.name)
        );

        if (matchingTags.length > 0) {
            tagDropdown.innerHTML = matchingTags.map(tag => `
                <div class="tag-dropdown-item" onclick="selectTag('${tag.name}')">
                    ${tag.name}
                </div>
            `).join('');
            tagDropdown.style.display = 'block';
        } else {
            // Show option to create new tag
            tagDropdown.innerHTML = `
                <div class="tag-dropdown-item" onclick="createAndSelectTag('${query}')">
                    Create "${query}"
                </div>
            `;
            tagDropdown.style.display = 'block';
        }
    });

    // Handle Enter key to add tag
    tagInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = e.target.value.trim();
            if (query) {
                createAndSelectTag(query);
            }
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function (e) {
        if (!tagInputWrapper.contains(e.target)) {
            tagDropdown.style.display = 'none';
        }
    });
}

// // Select existing tag
// function selectTag(tagName) {
//     if (!selectedTags.includes(tagName)) {
//         selectedTags.push(tagName);
//         updateTagDisplay();
//     }
//     document.getElementById('tagInput').value = '';
//     document.getElementById('tagDropdown').style.display = 'none';
// }

// // Create and select new tag
// async function createAndSelectTag(tagName) {
//     try {
//         // Check if tag already exists
//         const existingTag = allTags.find(tag => tag.name.toLowerCase() === tagName.toLowerCase());
//         if (existingTag) {
//             selectTag(existingTag.name);
//             return;
//         }

//         // Create new tag
//         const response = await fetch('/api/v1/tags/', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ name: tagName })
//         });

//         if (response.ok) {
//             const newTag = await response.json();
//             allTags.push(newTag);
//             selectTag(newTag.name);
//         }
//     } catch (error) {
//         console.error('Error creating tag:', error);
//         // Still allow selection even if creation failed
//         selectTag(tagName);
//     }
// }

// // Remove tag
// function removeTag(tagName) {
//     selectedTags = selectedTags.filter(tag => tag !== tagName);
//     updateTagDisplay();
// }

// Update tag display
function updateTagDisplay() {
    const container = document.querySelector('.tags-container');
    const hiddenInput = document.getElementById('tags');

    container.innerHTML = selectedTags.map(tag => `
        <span class="badge bg-primary me-1 mb-1">
            ${tag}
            <button type="button" class="btn-close btn-close-white ms-1" onclick="removeTag('${tag}')" aria-label="Remove"></button>
        </span>
    `).join('');

    // Update hidden input
    hiddenInput.value = selectedTags.join(',');
}

// Setup form submission
function setupForm() {
    const form = document.getElementById('equipmentForm');
    const cancelBtn = document.getElementById('cancelBtn');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = {
            name: document.getElementById('name').value,
            tags: selectedTags,
            service_frequency: document.getElementById('serviceFrequency').value || null,
            last_serviced_on: document.getElementById('lastServiced').value || null
        };

        try {
            let response;
            if (isEditing) {
                response = await fetch(`${API_BASE}/${editingId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
            } else {
                response = await fetch(`${API_BASE}/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
            }

            if (response.ok) {
                resetForm();
                loadEquipment();
                alert(isEditing ? 'Equipment updated!' : 'Equipment added!');
            } else {
                const errorText = await response.text();
                throw new Error(`Failed to save equipment: ${errorText}`);
            }
        } catch (error) {
            console.error('Error saving equipment:', error);
            alert('Failed to save equipment: ' + error.message);
        }
    });

    cancelBtn.addEventListener('click', resetForm);
}

/// Edit equipment: open the modal and let add_equipment_modal.js prefill the form
async function editEquipment(id) {
    try {
        const response = await fetch(`${API_BASE}/one/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch equipment: ${response.status}`);
        }

        const item = await response.json();

        // Make the fetched item available for the modal initializer
        window.editingItemData = item;
        window.editingItemId = id;

        // Update modal title + button label (parallel to consumables openEditModal)
        const titleEl = document.getElementById("addItemModalLabel");
        const submitBtn = document.getElementById("createItemBtn");
        if (titleEl) titleEl.textContent = "Edit Equipment";
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
        console.error('Error loading equipment for edit:', error);
        alert('Failed to load equipment for editing: ' + error.message);
    }
}



// Delete equipment - Fixed to use correct parameter name
async function deleteEquipment(id) {
    if (!confirm('Are you sure you want to delete this equipment?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadEquipment();
            alert('Equipment deleted!');
        } else {
            const errorText = await response.text();
            throw new Error(`Failed to delete equipment: ${errorText}`);
        }
    } catch (error) {
        console.error('Error deleting equipment:', error);
        alert('Failed to delete equipment: ' + error.message);
    }
}

// Reset form
function resetForm() {
    document.getElementById('equipmentForm').reset();
    document.getElementById('equipmentId').value = '';

    selectedTags = [];
    updateTagDisplay();
    document.getElementById('tagInput').value = '';

    isEditing = false;
    editingId = null;

    document.getElementById('form-title').textContent = 'Add Lab Equipment';
    document.getElementById('submitBtn').textContent = 'Add Equipment';
    document.getElementById('cancelBtn').style.display = 'none';
}

window.addItemToTable = function (item) {
    const tbody = document.getElementById('items-table-body');
    if (!tbody) return;

    const empty = tbody.querySelector('tr[data-empty="true"]');
    if (empty) empty.remove();

    const row = document.createElement('tr');
    row.classList.add(`item-id-${item.id}`);

    const lastServiced = item.last_serviced_on
        ? new Date(item.last_serviced_on).toLocaleDateString()
        : '—';

    const serviceFreq = item.service_frequency || '—';

    let tagsText = '—';
    if (Array.isArray(item.tags) && item.tags.length) {
        tagsText = item.tags
            .map(t => (typeof t === 'string' ? t : t?.name || ''))
            .filter(Boolean)
            .join(', ') || '—';
    }

    const lastServicedBy = item.last_serviced_by || '—';

    row.innerHTML = `
    <td>${item.id}</td>
    <td>${item.name || ''}</td>
    <td>${tagsText}</td>
    <td>${serviceFreq}</td>
    <td>${lastServiced}</td>
    <td>${lastServicedBy}</td>
    <td class="text-end">
      <button class="btn btn-sm btn-link text-primary p-0 me-2"
              onclick="editEquipment(${item.id})" title="Edit">
        <i class="fas fa-edit"></i>
      </button>
      <button class="btn btn-sm btn-link text-danger p-0"
              onclick="deleteEquipment(${item.id})" title="Delete">
        <i class="fas fa-trash"></i>
      </button>
    </td>
  `;

    tbody.prepend(row);
};


window.updateItemInTable = function (item) {
    const tbody = document.getElementById('items-table-body');
    if (!tbody) return;

    const existingRow = tbody.querySelector(`tr.item-id-${item.id}`);
    const row = document.createElement('tr');
    row.classList.add(`item-id-${item.id}`);

    const lastServiced = item.last_serviced_on
        ? new Date(item.last_serviced_on).toLocaleDateString()
        : '—';

    const serviceFreq = item.service_frequency || '—';

    let tagsText = '—';
    if (Array.isArray(item.tags) && item.tags.length) {
        tagsText = item.tags
            .map(t => (typeof t === 'string' ? t : t?.name || ''))
            .filter(Boolean)
            .join(', ') || '—';
    }

    const lastServicedBy = item.last_serviced_by || '—';

    row.innerHTML = `
    <td>${item.id}</td>
    <td>${item.name || ''}</td>
    <td>${tagsText}</td>
    <td>${serviceFreq}</td>
    <td>${lastServiced}</td>
    <td>${lastServicedBy}</td>
    <td class="text-end">
      <button class="btn btn-sm btn-link text-primary p-0 me-2"
              onclick="editEquipment(${item.id})" title="Edit">
        <i class="fas fa-edit"></i>
      </button>
      <button class="btn btn-sm btn-link text-danger p-0"
              onclick="deleteEquipment(${item.id})" title="Delete">
        <i class="fas fa-trash"></i>
      </button>
    </td>
  `;

    if (existingRow) {
        existingRow.replaceWith(row);
    } else {
        tbody.prepend(row);
    }
};


function filterTable() {
    const searchValue =
        document.getElementById("search-input")?.value.toLowerCase() || "";
    const nameFilter =
        document.getElementById("filter-name")?.value.toLowerCase() || "";
    const tagsFilter =
        document.getElementById("filter-tags")?.value.toLowerCase() || "";
    const locationFilter =
        document.getElementById("filter-location")?.value.toLowerCase() || "";

    const rows = document.querySelectorAll("#items-table-body tr");

    rows.forEach((row) => {
        const cells = row.querySelectorAll("td");
        if (cells.length === 0) return;

        const nameText = (cells[1]?.textContent || "").toLowerCase();
        const tagsText = (cells[3]?.textContent || "").toLowerCase();
        const locationText = ""; // no location column for equipment

        const matchesSearch =
            !searchValue ||
            nameText.includes(searchValue) ||
            tagsText.includes(searchValue);

        const matchesName = !nameFilter || nameText.includes(nameFilter);
        const matchesTags = !tagsFilter || tagsText.includes(tagsFilter);
        const matchesLocation =
            !locationFilter || locationText.includes(locationFilter);

        row.style.display =
            matchesSearch && matchesName && matchesTags && matchesLocation
                ? ""
                : "none";
    });
}

function clearFilters() {
    ["search-input", "filter-name", "filter-tags", "filter-location"].forEach(
        (id) => {
            const el = document.getElementById(id);
            if (el) el.value = "";
        }
    );
    filterTable();
}

window.filterTable = filterTable;
window.clearFilters = clearFilters;

// Make functions global for onclick handlers
window.editEquipment = editEquipment;
window.deleteEquipment = deleteEquipment;
// window.selectTag = selectTag;
// window.createAndSelectTag = createAndSelectTag;
// window.removeTag = removeTag;
