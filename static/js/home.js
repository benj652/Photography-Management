const API_PREFIX = "/api/v1";
window.API_PREFIX = API_PREFIX; // Make it available globally

// Function to fetch items from the server
async function fetchItems() {
  try {
    console.log("Fetching items from /items/all");
    const response = await fetch(API_PREFIX + "/items/all");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const items = await response.json();
    console.log("Fetched items:", items);
    return items;
  } catch (error) {
    console.error("Failed to fetch items:", error);
    showEmptyState("Failed to load items. Please refresh the page.");
  }
}

// Function to calculate and update stats
async function updateStats() {
  try {

    const data = await fetchItems();
    const items = data.items || [];
    const totalItems = items.length;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // In stock
    const inStockCount = items.filter((item) => {
      if (item.quantity <= 0) return false;
      if (!item.expires) return true;
      const expiresDate = new Date(item.expires);
      expiresDate.setHours(0, 0, 0, 0);
      return expiresDate >= today;
    }).length;

    // Out of stock
    const outOfStockCount = items.filter((item) => {
      if (item.quantity > 0) return false;
      if (!item.expires) return true;
      const expiresDate = new Date(item.expires);
      expiresDate.setHours(0, 0, 0, 0);
      return expiresDate >= today;
    }).length;

    // Expired
    const expiredCount = items.filter((item) => {
      if (!item.expires) return false;
      const expiresDate = new Date(item.expires);
      expiresDate.setHours(0, 0, 0, 0);
      return expiresDate < today;
    }).length;

    // Update stat cards
    document.getElementById("stat-total").textContent = `${totalItems} Items`;
    document.getElementById(
      "stat-in-stock"
    ).textContent = `${inStockCount} Items`;
    document.getElementById(
      "stat-out-of-stock"
    ).textContent = `${outOfStockCount} Items`;
    document.getElementById(
      "stat-expired"
    ).textContent = `${expiredCount} Items`;
  } catch (error) {
    console.error("Failed to update stats:", error);
  }
}

// Handle the actual deletion when confirmed
document.addEventListener("DOMContentLoaded", () => {
  console.log("Home.js loaded - DOMContentLoaded event fired");
  console.log("Navbar function available:", typeof Navbar);
  console.log("Window userData:", window.userData);
  
  fetchItems();
  // filterTable();

  // Initialize Navbar using the global Navbar function (loaded via script tag)
  const navbarContainer = document.getElementById("navbar");
  console.log("Navbar container element:", navbarContainer);
  
  if (typeof Navbar === 'function' && window.userData) {
    console.log("Attempting to render navbar with data:", window.userData);
    const navbarHTML = Navbar({
      profilePicture: window.userData.profilePicture,
      firstName: window.userData.firstName,
      role: window.userData.role,
      homeUrl: window.userData.homeUrl
    });
    console.log("Generated navbar HTML:", navbarHTML);
    
    if (navbarContainer) {
      navbarContainer.innerHTML = navbarHTML;
      console.log("Navbar HTML inserted into container");
    } else {
      console.error("Navbar container element not found!");
    }

    // Set up logout button handler after navbar is loaded
    setTimeout(() => {
      const logoutButton = document.getElementById("logoutButton");
      console.log("Logout button found:", logoutButton);
      if (logoutButton) {
        logoutButton.addEventListener("click", () => {
          window.location.href = "/auth/logout";
        });
        console.log("Logout button click handler added");
      }
    }, 100);
  } else {
    console.error("Navbar function not available or user data missing");
    console.error("Navbar function type:", typeof Navbar);
    console.error("User data:", window.userData);
  }

  // Initialize Breadcrumbs
  if (typeof Breadcrumbs === 'function' && window.userData) {
    const breadcrumbsContainer = document.getElementById("breadcrumbs");
    if (breadcrumbsContainer) {
      breadcrumbsContainer.innerHTML = Breadcrumbs({
        currentPage: 'Home',
        userRole: window.userData.role
      });
    }
  }
});