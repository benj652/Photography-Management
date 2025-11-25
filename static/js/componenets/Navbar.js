function Navbar({ profilePicture, firstName, role, homeUrl }) {
  // console.log("Navbar function called with:", { profilePicture, firstName, role, homeUrl });
  
  const navbarHTML = `
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm sticky-top">
      <div class="container-fluid px-4">

        <!-- Logo -->
        <a class="navbar-brand d-flex align-items-center" href="${homeUrl}">
          <div class="landing-logo">
            <span class="logo-icon">📸</span>
            <span class="logo-text">PhotoInventory</span>
          </div>
        </a>

        <!-- User profile and logout -->
        <div class="d-flex align-items-center">
          <div class="user-profile d-flex align-items-center me-4">

            ${
              profilePicture
                ? `<img src="${profilePicture}" alt="Profile" class="user-avatar rounded-circle me-2" height="45" width="45" />`
                : `<div class="user-avatar-placeholder rounded-circle d-flex align-items-center justify-content-center me-2">${firstName[0].toUpperCase()}</div>`
            }

            <div class="d-flex flex-column align-items-start">
              <span class="fw-semibold text-dark">${firstName}</span>
              <small class="text-muted">${role}</small>
            </div>
          </div>

          <button id="logoutButton" class="btn btn-outline-dark btn-sm">
            <i class="fas fa-sign-out-alt me-1"></i>Log Out
          </button>

        </div>
      </div>
    </nav>
  `;
  

  return navbarHTML;
}



