const API_BASE = '/api/v1/lab_equipment';

let isEditing = false;
let editingId = null;
let allTags = [];
let selectedTags = [];

// Load equipment on page load
document.addEventListener('DOMContentLoaded', function() {
    loadEquipment();
    loadTags();
    setupForm();
    setupTagInput();
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

// Display equipment in table
function displayEquipment(equipment) {
    const tbody = document.getElementById('equipmentTableBody');
    tbody.innerHTML = '';
    
    equipment.forEach(item => {
        const row = document.createElement('tr');
        
        // Format dates properly
        const lastServiced = item.last_serviced_on
            ? new Date(item.last_serviced_on).toLocaleDateString()
            : '—';
        
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${Array.isArray(item.tags) ? item.tags.join(', ') : item.tags || ''}</td>
            <td>${item.service_frequency || '—'}</td>
            <td>${lastServiced}</td>
            <td>${item.last_serviced_by || '—'}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editEquipment(${item.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteEquipment(${item.id})">Delete</button>
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
        // Still allow selection even if creation failed
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
    const form = document.getElementById('equipmentForm');
    const cancelBtn = document.getElementById('cancelBtn');
    
    form.addEventListener('submit', async function(e) {
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

// Edit equipment - Fixed to use correct parameter name
async function editEquipment(id) {
    try {
        const response = await fetch(`${API_BASE}/one/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch equipment: ${response.status}`);
        }
        
        const item = await response.json();
        
        document.getElementById('equipmentId').value = item.id;
        document.getElementById('name').value = item.name;
        document.getElementById('serviceFrequency').value = item.service_frequency || '';
        document.getElementById('lastServiced').value = item.last_serviced_on || '';
        
        // Set selected tags
        selectedTags = Array.isArray(item.tags) ? [...item.tags] : [];
        updateTagDisplay();
        
        isEditing = true;
        editingId = id;
        
        document.getElementById('form-title').textContent = 'Edit Lab Equipment';
        document.getElementById('submitBtn').textContent = 'Update Equipment';
        document.getElementById('cancelBtn').style.display = 'inline-block';
        
        // Scroll to form
        document.getElementById('equipmentForm').scrollIntoView({ behavior: 'smooth' });
        
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

// Make functions global for onclick handlers
window.editEquipment = editEquipment;
window.deleteEquipment = deleteEquipment;
window.selectTag = selectTag;
window.createAndSelectTag = createAndSelectTag;
window.removeTag = removeTag;
