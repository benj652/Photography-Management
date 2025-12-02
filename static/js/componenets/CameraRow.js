function CameraRow(
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
        (window.userData.role === "Admin" || window.userData.role === "Ta");
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
