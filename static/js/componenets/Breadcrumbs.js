function Breadcrumbs({ currentPage, userRole }) {
    const breadcrumbsHTML = `
    <nav aria-label="breadcrumb" class="bg-light border-bottom">
      <div class="container py-2">
        <div class="d-flex justify-content-between align-items-center">
          <ol class="breadcrumb mb-0">
            ${currentPage !== 'Home' ? '<li class="breadcrumb-item"><a href="/home" class="text-decoration-none"><i class="fas fa-home me-1"></i>Home</a></li>' : ''}
            <li class="breadcrumb-item active" aria-current="page">
              ${currentPage === 'Home' ? '<i class="fas fa-home me-1"></i>' : ''}${currentPage}
            </li>
          </ol>
          <div class="breadcrumb-nav">
            <button class="btn btn-sm btn-outline-secondary me-2 ${currentPage === 'Home' ? 'disabled' : ''}" ${currentPage === 'Home' ? 'disabled' : 'onclick="window.location.href=\'/home\'"'}>
              <i class="fas fa-home me-1"></i>Home
            </button>
            <button class="btn btn-sm btn-outline-secondary me-2 ${currentPage === 'Consumables' ? 'disabled' : ''}" ${currentPage === 'Consumables' ? 'disabled' : 'onclick="window.location.href=\'/home/consumables\'"'}>
              <i class="fas fa-flask me-1"></i>Consumables
            </button>
            <button class="btn btn-sm btn-outline-secondary me-2 ${currentPage === 'Lab Equipment' ? 'disabled' : ''}" ${currentPage === 'Lab Equipment' ? 'disabled' : 'onclick="window.location.href=\'/home/lab-equipment\'"'}>
              <i class="fas fa-microscope me-1"></i>Lab Equipment
            </button>
            <button class="btn btn-sm btn-outline-secondary me-2 ${currentPage === 'Camera Gear' ? 'disabled' : ''}" ${currentPage === 'Camera Gear' ? 'disabled' : 'onclick="window.location.href=\'/home/camera-gear\'"'}>
              <i class="fas fa-camera me-1"></i>Camera Gear
            </button>
            ${userRole === 'Admin' ? `<button class="btn btn-sm btn-outline-secondary ${currentPage === 'Admin Dashboard' ? 'disabled' : ''}" ${currentPage === 'Admin Dashboard' ? 'disabled' : 'onclick="window.location.href=\'/admin/dashboard\'"'}>
              <i class="fas fa-user-shield me-1"></i>Admin
            </button>` : ''}
          </div>
        </div>
      </div>
    </nav>
    `;
    return breadcrumbsHTML;
}

console.log("Breadcrumbs.js loaded - Breadcrumbs function defined");