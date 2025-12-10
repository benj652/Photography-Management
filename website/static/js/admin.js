// Initialize page when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    // Initialize Navbar
    if (typeof Navbar === 'function' && window.userData) {
        const navbarContainer = document.getElementById("navbar");
        if (navbarContainer) {
            navbarContainer.innerHTML = Navbar({
                profilePicture: window.userData.profilePicture,
                firstName: window.userData.firstName,
                role: window.userData.role,
                homeUrl: window.userData.homeUrl
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
    if (typeof Breadcrumbs === 'function' && window.userData) {
        const breadcrumbsContainer = document.getElementById("breadcrumbs");
        if (breadcrumbsContainer) {
            breadcrumbsContainer.innerHTML = Breadcrumbs({
                currentPage: 'Admin Dashboard',
                userRole: window.userData.role
            });
        }
    }

    // Fetch users after navbar is initialized
    fetchUsers();
});

async function fetchUsers() {
    try {
        const response = await fetch("/admin/users/all");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Fetched users:", data);

        populateUsers(data.user); // Use data.user directly
    } catch (error) {
        console.error("Failed to fetch users:", error);
    }
}

function populateUsers(users) {
    if (!users || users.length === 0) {
        console.log("No users found.");
        return;
    }

    const container = document.querySelector("#users-container");
    container.innerHTML = ""; // Clear existing content

    users.forEach((user) => {
        const row = document.createElement("div");
        row.className = "user-row p-3 mb-3 border rounded";

        row.innerHTML = `
            <div class="row">
                <div class="col-md-2">
                    <strong>ID:</strong> ${user.id || ""}
                </div>
                <div class="col-md-2">
                    <strong>Name:</strong> ${user.first_name || ""} ${user.last_name || ""}
                </div>
                <div class="col-md-3">
                    <strong>Email:</strong> ${user.email || ""}
                </div>
                <div class="col-md-2">
                    <img src="${user.profile_picture || ''}" alt="Profile" class="img-thumbnail" style="max-width: 50px; max-height: 50px;" crossorigin="anonymous" referrerpolicy="no-referrer" />
                </div>
                <div class="col-md-3">
                    <strong>Role:</strong>
                    <select name="role" class="form-select role-select" data-user-id="${user.id}" data-current-role="${user.role || 'invalid'}">
                        <option value="invalid" ${user.role === 'invalid' ? 'selected' : ''}>Invalid</option>
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                        <option value="ta" ${user.role === 'ta' ? 'selected' : ''}>TA</option>
                        <option value="student" ${user.role === 'student' ? 'selected' : ''}>Student</option>
                    </select>
                </div>
            </div>
        `;

        container.appendChild(row);
    });

    // Add event listeners to all role select dropdowns
    document.querySelectorAll('.role-select').forEach(select => {
        select.addEventListener('change', handleRoleChange);
    });
}

async function handleRoleChange(event) {
    const select = event.target;
    const userId = select.getAttribute('data-user-id');
    const newRole = select.value;
    const currentRole = select.getAttribute('data-current-role');

    if (newRole === currentRole) {
        return; // No change
    }

    try {
        // Disable the select while processing
        select.disabled = true;
        
        // Call the appropriate API endpoint based on the new role
        const response = await fetch(`/admin/users/to-${newRole}/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to update role: ${response.status}`);
        }

        const updatedUser = await response.json();
        console.log('Role updated successfully:', updatedUser);
        
        // Update the data attribute to reflect the new role
        select.setAttribute('data-current-role', newRole);
        
        // Show success message (optional)
        showMessage(`Successfully updated user role to ${newRole}`, 'success');

    } catch (error) {
        console.error('Error updating role:', error);
        
        // Revert the select to the previous value
        select.value = currentRole;
        
        // Show error message
        showMessage('Failed to update user role. Please try again.', 'error');
    } finally {
        // Re-enable the select
        select.disabled = false;
    }
}

function showMessage(message, type) {
    // Create or update a message div
    let messageDiv = document.getElementById('admin-message');
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = 'admin-message';
        messageDiv.className = 'alert';
        document.querySelector('#users-container').parentNode.insertBefore(messageDiv, document.querySelector('#users-container'));
    }
    
    messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}
