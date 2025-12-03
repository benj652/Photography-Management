function LabRow(
    id,
    name,
    tags,
    serviceFreq,
    lastServiced,
    lastServicedBy,
    lastUpdated,
    item,
) {
    const canEditOrDelete =
        window.userData.role &&
        (window.userData.role === "Admin" || window.userData.role === "Ta");
    return canEditOrDelete
        ? `
            <td class="text-center">${id}</td>
            <td class="text-start">${name}</td>
            <td class="text-start">${tags}</td>
            <td class="text-start">${serviceFreq}</td>
            <td class="text-start">${lastServiced}</td>
            <td class="text-start">${lastServicedBy}</td>
            <td class="text-start">${lastUpdated}</td>
            <td class="text-end">
                <div class="d-inline-flex gap-3 align-items-center">
                    <button class="btn btn-sm btn-link text-primary p-0" onclick="openEditModal(${item.id})" title="Edit item">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteEquipment(${item.id})" title="Delete item">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `
        : `
            <td class="text-center">${id}</td>
            <td class="text-start">${name}</td>
            <td class="text-start">${tags}</td>
            <td class="text-start">${serviceFreq}</td>
            <td class="text-start">${lastServiced}</td>
            <td class="text-start">${lastServicedBy}</td>
            <td class="text-start">${lastUpdated}</td>
            <td class="text-end">
                <div class="d-inline-flex gap-3 align-items-center">
                    None
                </div>
            </td>
        `;
}
