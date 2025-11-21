/**
 * Manages pagination state and rendering for the items table
 */
const Pagination = (function () {
  // Private state
  let allItems = [];
  let filteredItems = [];
  let currentPage = 1;
  const itemsPerPage = 10;
  let onPageChangeCallback = null;

  function init(items) {
    allItems = items || [];
    filteredItems = [...allItems];
    currentPage = 1;
  }

  function setFilteredItems(items) {
    filteredItems = items || [];
    currentPage = 1; // Reset to first page when filtering
  }

  function getAllItems() {
    return allItems;
  }

  function getFilteredItems() {
    return filteredItems;
  }

  function getCurrentPageItems() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredItems.slice(startIndex, endIndex);
  }

  function getCurrentPage() {
    return currentPage;
  }

  function getTotalPages() {
    return Math.ceil(filteredItems.length / itemsPerPage);
  }

  function getItemsPerPage() {
    return itemsPerPage;
  }

  function addItem(item) {
    allItems.unshift(item);
    filteredItems = [...allItems];
    currentPage = 1; // Reset to first page to show new item
  }

  function setOnPageChange(callback) {
    onPageChangeCallback = callback;
  }

  function goToPage(page) {
    const totalPages = getTotalPages();
    if (page < 1 || page > totalPages) return;

    currentPage = page;

    // Call callback if set
    if (onPageChangeCallback && typeof onPageChangeCallback === "function") {
      onPageChangeCallback();
    }

    render();

    // Scroll to top of table
    const tableContainer = document.querySelector(".table-responsive");
    if (tableContainer) {
      tableContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function resetToFirstPage() {
    currentPage = 1;
  }

  function render(containerId = "pagination-container") {
    const paginationContainer = document.getElementById(containerId);
    if (!paginationContainer) return;

    const totalPages = getTotalPages();

    // Don't show pagination if there's only one page or no items
    if (totalPages <= 1) {
      paginationContainer.innerHTML = "";
      return;
    }

    let paginationHTML = `
        <nav aria-label="Table pagination">
          <ul class="pagination justify-content-center mb-0">
            <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
              <a class="page-link" href="#" onclick="Pagination.goToPage(${
                currentPage - 1
              }); return false;" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
              </a>
            </li>
      `;

    // Calculate which page numbers to show
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (endPage - startPage < 4) {
      if (startPage === 1) {
        endPage = Math.min(5, totalPages);
      } else if (endPage === totalPages) {
        startPage = Math.max(1, totalPages - 4);
      }
    }

    // First page
    if (startPage > 1) {
      paginationHTML += `
          <li class="page-item">
            <a class="page-link" href="#" onclick="Pagination.goToPage(1); return false;">1</a>
          </li>
        `;
      if (startPage > 2) {
        paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
      }
    }

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      paginationHTML += `
          <li class="page-item ${i === currentPage ? "active" : ""}">
            <a class="page-link" href="#" onclick="Pagination.goToPage(${i}); return false;">${i}</a>
          </li>
        `;
    }

    // Last page
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
      }
      paginationHTML += `
          <li class="page-item">
            <a class="page-link" href="#" onclick="Pagination.goToPage(${totalPages}); return false;">${totalPages}</a>
          </li>
        `;
    }

    // Next button
    paginationHTML += `
            <li class="page-item ${
              currentPage === totalPages ? "disabled" : ""
            }">
              <a class="page-link" href="#" onclick="Pagination.goToPage(${
                currentPage + 1
              }); return false;" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
              </a>
            </li>
          </ul>
        </nav>
        <div class="text-center mt-2 text-muted small">
          Showing ${Math.min(
            (currentPage - 1) * itemsPerPage + 1,
            filteredItems.length
          )} - ${Math.min(
      currentPage * itemsPerPage,
      filteredItems.length
    )} of ${filteredItems.length} items
        </div>
      `;

    paginationContainer.innerHTML = paginationHTML;
  }

  return {
    init,
    setFilteredItems,
    getAllItems,
    getFilteredItems,
    getCurrentPageItems,
    getCurrentPage,
    getTotalPages,
    getItemsPerPage,
    addItem,
    setOnPageChange,
    goToPage,
    resetToFirstPage,
    render,
  };
})();
