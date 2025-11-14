async function fetchUsers() {
    try {
        const response = await fetch("/admin/users/all");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Fetched users:", data);

        populateUsers(data); // adjust to match API response
    } catch (error) {
        console.error("Failed to fetch users:", error);
    }
}

fetchUsers();

function populateUsers(users) {
    users = users.user;
    if (!users || users.length === 0) {
        console.log("No users found.");
        return;
    }

    const container = document.querySelector("#users-container");

    users.forEach((user) => {
        const row = document.createElement("div");

        row.innerHTML = `
            <div class="user-id-${user.id}">${user.id || ""}</div>
            <div>${user.first_name || ""}</div>
            <div>${user.last_name || ""}</div>
            <div>${user.email || ""}</div>
            <div>${user.location || ""}</div>
            <img src="${user.profile_picture}" />
<select name="role" id="role-select" >
    <option value="invalid">Invalid</option>
    <option value="admin">Admin</option>
    <option value="ta">TA</option>
    <option value="student">Student</option>
</select>

        `;

        container.appendChild(row);
    });
}
