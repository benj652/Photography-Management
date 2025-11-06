// // Small script to open the Add Item modal when the button is clicked.
// document.addEventListener('DOMContentLoaded', function () {
//     var btn = document.getElementById('openAddItemBtn');
//     if (!btn) return;
//     btn.addEventListener('click', function (e) {
//         try {
//             if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
//                 var modalEl = document.getElementById('addItemModal');
//                 if (modalEl) {
//                     var m = bootstrap.Modal.getOrCreateInstance(modalEl);
//                     m.show();
//                 }
//             } else {
//                 console.warn('Bootstrap JS not found; modal may not work.');
//             }
//         } catch (err) {
//             console.error('Error showing modal:', err);
//         }
//     });
// });

document.addEventListener("DOMContentLoaded", function () {
  console.log("Modal script loaded");

  const form = document.getElementById("addItemForm");
  const submitBtn = document.getElementById("createItemBtn");
  const spinner = submitBtn.querySelector(".spinner-border");
  const modalAlert = document.getElementById("modalAlert");

  // Tags functionality
  const tagsInput = document.getElementById("tags-input");
  const tagsDropdown = document.getElementById("tags-dropdown");
  const createTagBtnContainer = document.getElementById(
    "create-tag-btn-container"
  );
  const createTagBtn = document.getElementById("createTagBtn");
  const newTagNameSpan = document.getElementById("new-tag-name");
  const selectedTagsContainer = document.getElementById("selected-tags");
  const hiddenTagsInput = document.getElementById("tags");

  let allTags = [];
  let selectedTag = null;

  // Fetch all tags from the database
  async function fetchTags() {
    try {
      const response = await fetch("/tags/all");
      if (!response.ok) {
        throw new Error("Failed to fetch tags");
      }
      const data = await response.json();
      allTags = data.tags || [];
      return allTags;
    } catch (error) {
      console.error("Error fetching tags:", error);
      return [];
    }
  }

  // Initialize tags on modal open
  document
    .getElementById("addItemModal")
    .addEventListener("shown.bs.modal", async function () {
      await fetchTags();
      selectedTag = null;
      updateSelectedTagDisplay();
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      tagsInput.disabled = false;
    });

  // Handle tags input
  tagsInput.addEventListener("input", function (e) {
    // If a tag is already selected, don't show dropdown
    if (selectedTag) {
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      return;
    }

    const query = e.target.value.trim().toLowerCase();

    if (query === "") {
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      return;
    }

    // Filter tags that match the query
    const matchingTags = allTags.filter((tag) =>
      tag.name.toLowerCase().includes(query)
    );

    // Check if the query exactly matches an existing tag
    const exactMatch = allTags.find((tag) => tag.name.toLowerCase() === query);

    if (exactMatch) {
      // Exact match found, show only that tag
      tagsDropdown.innerHTML = `
                <div class="tags-dropdown-item" onclick="selectTag('${exactMatch.name}')">
                    ${exactMatch.name}
                </div>
            `;
      createTagBtnContainer.classList.add("d-none");
    } else if (matchingTags.length > 0) {
      // Show matching tags
      tagsDropdown.innerHTML = matchingTags
        .map(
          (tag) => `
                <div class="tags-dropdown-item" onclick="selectTag('${tag.name}')">
                    ${tag.name}
                </div>
            `
        )
        .join("");
      createTagBtnContainer.classList.add("d-none");
    } else {
      // No matches, show create tag button
      tagsDropdown.innerHTML = "";
      newTagNameSpan.textContent = query;
      createTagBtnContainer.classList.remove("d-none");
    }
  });

  // Handle tag selection
  window.selectTag = function (tagName) {
    selectedTag = tagName;
    updateSelectedTagDisplay();
    tagsInput.value = "";
    tagsDropdown.innerHTML = "";
    createTagBtnContainer.classList.add("d-none");
    tagsInput.disabled = true;
  };

  // Handle tag removal
  window.removeTag = function () {
    selectedTag = null;
    updateSelectedTagDisplay();
    tagsInput.disabled = false;
    tagsInput.focus();
  };

  // Update selected tag display
  function updateSelectedTagDisplay() {
    if (!selectedTag) {
      selectedTagsContainer.innerHTML = "";
      hiddenTagsInput.value = "";
    } else {
      selectedTagsContainer.innerHTML = `
                <span class="badge bg-primary me-1 mb-1" style="font-size: 0.875rem;">
                    ${selectedTag}
                    <button type="button" class="btn-close btn-close-white ms-1" onclick="removeTag()" aria-label="Remove"></button>
                </span>
            `;
      hiddenTagsInput.value = selectedTag;
    }
  }

  // Handle create tag button
  createTagBtn.addEventListener("click", async function () {
    const newTagName = tagsInput.value.trim();
    if (!newTagName) return;

    try {
      const response = await fetch("/tags/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: newTagName }),
      });

      if (!response.ok) {
        throw new Error("Failed to create tag");
      }

      const newTag = await response.json();

      allTags.push(newTag);
      selectedTag = newTag.name;
      updateSelectedTagDisplay();

      // Clear input
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      tagsInput.disabled = true;
    } catch (error) {
      console.error("Error creating tag:", error);
      showAlert("Failed to create tag. Please try again.", "danger");
    }
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (!tagsInput.contains(e.target) && !tagsDropdown.contains(e.target)) {
      tagsDropdown.innerHTML = "";
    }
  });

  if (!form) {
    console.error("Form not found!");
    return;
  }

  form.addEventListener("submit", function (e) {
    console.log("Form submitted - preventing default");
    e.preventDefault();
    e.stopPropagation();

    // Show loading state
    submitBtn.disabled = true;
    spinner.classList.remove("d-none");
    hideAlert();

    // Get form data
    const formData = new FormData(form);
    const data = {
      name: formData.get("name"),
      quantity: parseInt(formData.get("quantity")) || 1,
      tags: selectedTag ? [selectedTag] : [],
      location_id: formData.get("location_id")
        ? parseInt(formData.get("location_id"))
        : null,
      expires: formData.get("expires") || null,
    };

    console.log("Sending data:", data);

    // Send request
    fetch("/items/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        console.log("Response status:", response.status);
        console.log("Response headers:", response.headers);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Success response:", data);
        showAlert("Item created successfully!", "success");

        // Try to add to table
        if (typeof window.addItemToTable === "function") {
          console.log("Adding item to table");
          window.addItemToTable(data);
        } else {
          console.log("addItemToTable function not found, reloading page");
          setTimeout(() => window.location.reload(), 100);
        }

        // Close modal after delay
        setTimeout(() => {
          const modal = bootstrap.Modal.getInstance(
            document.getElementById("addItemModal")
          );
          if (modal) {
            modal.hide();
          }
          form.reset();
          hideAlert();
        }, 1500);
      })
      .catch((error) => {
        console.error("Error:", error);
        showAlert("Error: " + error.message, "danger");
      })
      .finally(() => {
        // Reset button state
        submitBtn.disabled = false;
        spinner.classList.add("d-none");
      });

    return false; // Extra prevention of form submission
  });

  function showAlert(message, type) {
    modalAlert.textContent = message;
    modalAlert.className = `alert alert-${type}`;
    modalAlert.classList.remove("d-none");
  }

  function hideAlert() {
    modalAlert.classList.add("d-none");
  }

  // Reset form when modal is closed
  document
    .getElementById("addItemModal")
    .addEventListener("hidden.bs.modal", function () {
      form.reset();
      hideAlert();
    });
});
