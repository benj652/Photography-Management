const API_BASE = '/api/v1/camera_gear';

let isEditing = false;
let editingId = null;
let allTags = [];
let allLocations = [];
let selectedTags = [];

// Load camera gear on page load
document.addEventListener('DOMContentLoaded', function() {
    loadCameraGear();
    loadTags();
    loadLocations();
    setupForm();
    setupTagInput();
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

// Load all locations
async function loadLocations() {
    try {
        const response = await fetch('/api/v1/location/all');
        const data = await response.json();
        allLocations = data.locations || [];
        populateLocationSelect();
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

// Populate location dropdown
function populateLocationSelect() {
    const locationSelect = document.getElementById('location');
    locationSelect.innerHTML = '<option value="">Select location...</option>';
    
    allLocations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.id;
        option.textContent = location.name;
        locationSelect.appendChild(option);
    });
}

// Display camera gear in table
function displayCameraGear(gear) {
    const tbody = document.getElementById('cameraGearTableBody');
    tbody.innerHTML = '';
    
    gear.forEach(item => {
        const row = document.createElement('tr');
        
        // Determine checkout status
        const isCheckedOut = item.checked_out_by;
        const status = isCheckedOut ? 
            '<span class="badge bg-warning">Checked Out</span>' : 
            '<span class="badge bg-success">Available</span>';
        
        // Add checked-out styling
        if (isCheckedOut) {
            row.classList.add('checked-out-row');
        }
        
        // Use location name directly from API response
        const locationName = item.location || '';
        
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${Array.isArray(item.tags) ? item.tags.join(', ') : item.tags || ''}</td>
            <td>${locationName}</td>
            <td>${status}</td>
            <td>${item.checked_out_by || '—'}</td>
            <td>
                <button class="btn btn-sm btn-warning me-1" onclick="editCameraGear(${item.id})">Edit</button>
                ${isCheckedOut ? 
                    `<button class="btn btn-sm btn-info me-1" onclick="checkInGear(${item.id})">Check In</button>` :
                    `<button class="btn btn-sm btn-success me-1" onclick="checkOutGear(${item.id})">Check Out</button>`
                }
                <button class="btn btn-sm btn-danger" onclick="deleteCameraGear(${item.id})">Delete</button>
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
    tagInput.addEventListener('input', function(e) {
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
    tagInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = e.target.value.trim();
            if (query) {
                createAndSelectTag(query);
            }
        }
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!tagInputWrapper.contains(e.target)) {
            tagDropdown.style.display = 'none';
        }
    });
}

// Select existing tag
function selectTag(tagName) {
    if (!selectedTags.includes(tagName)) {
        selectedTags.push(tagName);
        updateTagDisplay();
    }
    document.getElementById('tagInput').value = '';
    document.getElementById('tagDropdown').style.display = 'none';
}

// Create and select new tag
async function createAndSelectTag(tagName) {
    try {
        // Check if tag already exists
        const existingTag = allTags.find(tag => tag.name.toLowerCase() === tagName.toLowerCase());
        if (existingTag) {
            selectTag(existingTag.name);
            return;
        }
        
        // Create new tag
        const response = await fetch('/api/v1/tags/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: tagName })
        });
        
        if (response.ok) {
            const newTag = await response.json();
            allTags.push(newTag);
            selectTag(newTag.name);
        }
    } catch (error) {
        console.error('Error creating tag:', error);
        selectTag(tagName);
    }
}

// Remove tag
function removeTag(tagName) {
    selectedTags = selectedTags.filter(tag => tag !== tagName);
    updateTagDisplay();
}

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
    const form = document.getElementById('cameraGearForm');
    const cancelBtn = document.getElementById('cancelBtn');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value,
            tags: selectedTags,
            location_id: document.getElementById('location').value || null
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
                loadCameraGear();
                alert(isEditing ? 'Camera gear updated!' : 'Camera gear added!');
            } else {
                const errorText = await response.text();
                throw new Error(`Failed to save camera gear: ${errorText}`);
            }
        } catch (error) {
            console.error('Error saving camera gear:', error);
            alert('Failed to save camera gear: ' + error.message);
        }
    });
    
    cancelBtn.addEventListener('click', resetForm);
}

// Edit camera gear
async function editCameraGear(id) {
    try {
        const response = await fetch(`${API_BASE}/one/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch camera gear: ${response.status}`);
        }
        
        const item = await response.json();
        
        document.getElementById('gearId').value = item.id;
        document.getElementById('name').value = item.name;
        document.getElementById('location').value = item.location_id || '';
        
        // Set selected tags
        selectedTags = Array.isArray(item.tags) ? [...item.tags] : [];
        updateTagDisplay();
        
        isEditing = true;
        editingId = id;
        
        document.getElementById('form-title').textContent = 'Edit Camera Gear';
        document.getElementById('submitBtn').textContent = 'Update Camera Gear';
        document.getElementById('cancelBtn').style.display = 'inline-block';
        
        // Scroll to form
        document.getElementById('cameraGearForm').scrollIntoView({ behavior: 'smooth' });
        
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

// Reset form
function resetForm() {
    document.getElementById('cameraGearForm').reset();
    document.getElementById('gearId').value = '';
    
    selectedTags = [];
    updateTagDisplay();
    document.getElementById('tagInput').value = '';
    
    isEditing = false;
    editingId = null;
    
    document.getElementById('form-title').textContent = 'Add Camera Gear';
    document.getElementById('submitBtn').textContent = 'Add Camera Gear';
    document.getElementById('cancelBtn').style.display = 'none';
}

// Make functions global for onclick handlers
window.editCameraGear = editCameraGear;
window.deleteCameraGear = deleteCameraGear;
window.checkOutGear = checkOutGear;
window.checkInGear = checkInGear;
window.selectTag = selectTag;
window.createAndSelectTag = createAndSelectTag;
window.removeTag = removeTag;