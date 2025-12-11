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
  hasNote = false
) {
  const noteIndicator = hasNote
    ? '<span class="badge bg-success rounded-pill me-2" style="width: 8px; height: 8px; padding: 0; display: inline-block;" title="Has note"></span>'
    : '<span style="width: 8px; height: 8px; margin-right: 0.5rem; display: inline-block;"></span>';

  const canEditOrDelete =
    window.userData &&
    (window.userData.role === "Admin" || window.userData.role === "Ta");
  return canEditOrDelete
    ? `
            <td>${noteIndicator}${id}</td>
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
    : `<td>${noteIndicator}${id}</td>
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
