function NormalRow(
  id,
  nameText,
  quantityText,
  tagsText,
  locationText,
  expires,
  lastUpdated,
  updatedByText,
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
        <td class="item-id-${id}">${noteIndicator}${id}</td>
        <td>${nameText}</td>
        <td>${quantityText}</td>
        <td>${tagsText}</td>
        <td>${locationText}</td>
        <td>${expires}</td>
        <td>${lastUpdated}</td>
        <td>${updatedByText}</td>
        <td class="text-end">
        <div class="d-inline-flex gap-2 align-items-center">
          <button class="btn btn-sm btn-link text-primary p-0" onclick="openEditModal(${id})" title="Edit item"><i class="fas fa-edit"></i></button>
          <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteItem(${id})" title="Delete item"><i class="fas fa-trash"></i></button>
          </div>
        </td>
`
    : `
        <td class="item-id-${id}">${noteIndicator}${id}</td>
        <td>${nameText}</td>
        <td>${quantityText}</td>
        <td>${tagsText}</td>
        <td>${locationText}</td>
        <td>${expires}</td>
        <td>${lastUpdated}</td>
        <td>${updatedByText}</td>
        <td class="text-end">
        <div class="d-inline-flex gap-2 align-items-center">
           None 
          </div>
        </td>
`;
}
