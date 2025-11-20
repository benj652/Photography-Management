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

  // Helper to update the button label while preserving the spinner element
  function setButtonLabel(btn, text) {
    if (!btn) return;
    const textNodes = [];
    for (const node of Array.from(btn.childNodes)) {
      if (node.nodeType === Node.TEXT_NODE) {
        textNodes.push(node);
      }
    }
    textNodes.forEach((node) => node.remove());
    btn.appendChild(document.createTextNode(" " + text));
  }

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

  // Location functionality - exact mirror of tags
  const locationInput = document.getElementById("location-input");
  const locationDropdown = document.getElementById("location-dropdown");
  const createLocationBtnContainer = document.getElementById(
    "create-location-btn-container"
  );
  const createLocationBtn = document.getElementById("createLocationBtn");
  const newLocationNameSpan = document.getElementById("new-location-name");
  const selectedLocationContainer =
    document.getElementById("selected-location");
  const hiddenLocationInput = document.getElementById("location_id");

  let allTags = [];
  let allLocations = [];
  let selectedTags = [];
  let selectedLocation = null;

  function updateItem(itemId, updatedData) {
    // Simple helper that updates an item via API and then refreshes the row using updateItemInTable
    fetch(`${API_PREFIX}/items/${itemId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(updatedData),
    })
      .then((resp) => {
        if (!resp.ok) throw new Error(`HTTP error! status: ${resp.status}`);
        return resp.json();
      })
      .then((data) => {
        if (typeof window.updateItemInTable === "function")
          window.updateItemInTable(data);
      })
      .catch((err) => console.error("Failed to update item:", err));
  }
  // Fetch all tags from the database
  async function fetchTags() {
    try {
      const response = await fetch(API_PREFIX + "/tags/all");
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

  // Fetch all locations from the database - exact mirror of fetchTags
  async function fetchLocations() {
    try {
      const response = await fetch(API_PREFIX + "/location/all");
      if (!response.ok) {
        throw new Error("Failed to fetch locations");
      }
      const data = await response.json();
      allLocations = data.locations || [];
      return allLocations;
    } catch (error) {
      console.error("Error fetching locations:", error);
      return [];
    }
  }

  // Initialize tags and locations on modal open
  document
    .getElementById("addItemModal")
    .addEventListener("shown.bs.modal", async function () {
      // Initialize tags
      await fetchTags();
      selectedTags = [];
      updateSelectedTagDisplay();
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      tagsInput.disabled = false;

      // Initialize locations - exact mirror
      await fetchLocations();
      selectedLocation = null;
      updateSelectedLocationDisplay();
      locationInput.value = "";
      locationDropdown.innerHTML = "";
      createLocationBtnContainer.classList.add("d-none");
      locationInput.disabled = false;

      // If editing data was placed on the window, prefill fields now
      if (window.editingItemData) {
        const item = window.editingItemData;
        console.log("Prefilling form for editing:", item.id);
        // Name, quantity, expires
        document.getElementById("name").value = item.name || "";
        document.getElementById("quantity").value = item.quantity;
        document.getElementById("expires").value = item.expires
          ? item.expires.split("T")[0]
          : "";

        // Tags - select the first tag if present
        if (Array.isArray(item.tags) && item.tags.length > 0) {
          selectedTags = item.tags
            .map((tag) =>
              typeof tag === "string" ? tag : (tag && tag.name) || ""
            )
            .filter(Boolean);
        } else {
          selectedTags = [];
        }
        updateSelectedTagDisplay();

        // Location - prefer name, otherwise leave id
        if (item.location_id) {
          if (typeof window.selectLocation === "function") {
            window.selectLocation(item.location_id);
          } else {
            document.getElementById("location_id").value =
              item.location_id || "";
          }
        } else if (item.location_id) {
          document.getElementById("location_id").value = item.location_id;
        }

        // Mark form as editing
        const formEl = document.getElementById("addItemForm");
        if (formEl) formEl.dataset.editingId = item.id;

        // Also show the Item ID in the modal if the container exists
        const idContainer = document.getElementById("modalItemIdContainer");
        const idValue = document.getElementById("modalItemIdValue");
        const idToShow =
          window.editingItemId ||
          (window.editingItemData && window.editingItemData.id) ||
          item.id;
        if (idContainer && idValue) {
          idValue.textContent = idToShow || "";
          if (idToShow) idContainer.classList.remove("d-none");
          else idContainer.classList.add("d-none");
        }
      } else {
        // Ensure not in editing state
        const formEl = document.getElementById("addItemForm");
        if (formEl && formEl.dataset.editingId) delete formEl.dataset.editingId;
        const idContainer = document.getElementById("modalItemIdContainer");
        const idValue = document.getElementById("modalItemIdValue");
        if (idContainer && idValue) {
          idValue.textContent = "";
          idContainer.classList.add("d-none");
        }
      }
    });

  // Handle tags input
  tagsInput.addEventListener("input", function (e) {
    // If a tag is already selected, don't show dropdown
        const query = e.target.value.trim().toLowerCase();

        if (query === "") {
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      return;
    }

    // Filter tags that match the query
    const selectedLower = new Set(
      selectedTags.map((tag) => tag.toLowerCase())
    );
    const matchingTags = allTags.filter(
      (tag) =>
        tag.name.toLowerCase().includes(query) &&
        !selectedLower.has(tag.name.toLowerCase())
    );

    // Check if the query exactly matches an existing tag
    const exactMatch = allTags.find((tag) => tag.name.toLowerCase() === query);

    if (exactMatch && !selectedLower.has(exactMatch.name.toLowerCase())) {
      // Exact match found, show only that tag
      tagsDropdown.innerHTML = `
                <div class="tags-dropdown-item" onclick="selectTag('${exactMatch.name}')">
                    ${exactMatch.name}
                </div>
            `;
      createTagBtnContainer.classList.add("d-none");
    } else if (exactMatch && selectedLower.has(exactMatch.name.toLowerCase())) {
      tagsDropdown.innerHTML = `
                <div class="p-2 text-muted">Tag already selected.</div>
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

  // Handle location input - exact mirror of tags input
  locationInput.addEventListener("input", function (e) {
    // If a location is already selected, don't show dropdown
    if (selectedLocation) {
      locationDropdown.innerHTML = "";
      createLocationBtnContainer.classList.add("d-none");
      return;
    }

    const query = e.target.value.trim().toLowerCase();

    if (query === "") {
      locationDropdown.innerHTML = "";
      createLocationBtnContainer.classList.add("d-none");
      return;
    }

    // Filter locations that match the query
    const matchingLocations = allLocations.filter((location) =>
      location.name.toLowerCase().includes(query)
    );

    // Check if the query exactly matches an existing location
    const exactMatch = allLocations.find(
      (location) => location.name.toLowerCase() === query
    );

    if (exactMatch) {
      // Exact match found, show only that location
      locationDropdown.innerHTML = `
                <div class="tags-dropdown-item" onclick="selectLocation('${exactMatch.name}')">
                    ${exactMatch.name}
                </div>
            `;
      createLocationBtnContainer.classList.add("d-none");
    } else if (matchingLocations.length > 0) {
      // Show matching locations
      locationDropdown.innerHTML = matchingLocations
        .map(
          (location) => `
                <div class="tags-dropdown-item" onclick="selectLocation('${location.name}')">
                    ${location.name}
                </div>
            `
        )
        .join("");
      createLocationBtnContainer.classList.add("d-none");
    } else {
      // No matches, show create location button
      locationDropdown.innerHTML = "";
      newLocationNameSpan.textContent = query;
      createLocationBtnContainer.classList.remove("d-none");
    }
  });

  // Handle tag selection
  window.selectTag = function (tagName) {
    if (!tagName) return;
    const exists = selectedTags.some(
      (tag) => tag.toLowerCase() === tagName.toLowerCase()
    );
    if (!exists) {
      selectedTags.push(tagName);
    }
    updateSelectedTagDisplay();
    tagsInput.value = "";
    tagsDropdown.innerHTML = "";
    createTagBtnContainer.classList.add("d-none");
  };

  // Handle location selection - exact mirror of tag selection
  window.selectLocation = function (locationName) {
    selectedLocation = locationName;
    updateSelectedLocationDisplay();
    locationInput.value = "";
    locationDropdown.innerHTML = "";
    createLocationBtnContainer.classList.add("d-none");
    locationInput.disabled = true;
  };

  // Handle tag removal
  window.removeTag = function (tagName) {
    selectedTags = selectedTags.filter((tag) => tag !== tagName);
    updateSelectedTagDisplay();
    tagsInput.focus();
  };

  // Handle location removal - exact mirror of tag removal
  window.removeLocation = function () {
    selectedLocation = null;
    updateSelectedLocationDisplay();
    locationInput.disabled = false;
    locationInput.focus();
  };

  // Update selected tag display
  function updateSelectedTagDisplay() {
    if (!selectedTags.length) {
      selectedTagsContainer.innerHTML = "";
    } else {
      selectedTagsContainer.innerHTML = selectedTags
        .map(
          (tag) => `
                <span class="badge bg-primary me-1 mb-1" style="font-size: 0.875rem;">
                    ${tag}
                    <button type="button" class="btn-close btn-close-white ms-1" onclick='removeTag(${JSON.stringify(
                      tag
                    )})' aria-label="Remove"></button>
                </span>
            `
        )
        .join("");
    }
    hiddenTagsInput.value = selectedTags.length
      ? JSON.stringify(selectedTags)
      : "";
  }

  // Update selected location display - exact mirror of tag display
  function updateSelectedLocationDisplay() {
    if (!selectedLocation) {
      selectedLocationContainer.innerHTML = "";
      hiddenLocationInput.value = "";
    } else {
      selectedLocationContainer.innerHTML = `
                <span class="badge bg-secondary me-1 mb-1" style="font-size: 0.875rem;">
                    ${selectedLocation}
                    <button type="button" class="btn-close btn-close-white ms-1" onclick="removeLocation()" aria-label="Remove"></button>
                </span>
            `;
      // Find the location ID and set it in the hidden input
      const locationObj = allLocations.find(
        (loc) => loc.name === selectedLocation
      );
      hiddenLocationInput.value = locationObj ? locationObj.id : "";
    }
  }

  // Handle create tag button
  createTagBtn.addEventListener("click", async function () {
    const newTagName = tagsInput.value.trim();
    if (!newTagName) return;

    try {
      const response = await fetch(API_PREFIX + "/tags", {
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
      if (!selectedTags.includes(newTag.name)) {
        selectedTags.push(newTag.name);
        updateSelectedTagDisplay();
      }

      // Clear input
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
    } catch (error) {
      console.error("Error creating tag:", error);
      showAlert("Failed to create tag. Please try again.", "danger");
    }
  });

  // Handle create location button - exact mirror of create tag button
  createLocationBtn.addEventListener("click", async function () {
    const newLocationName = locationInput.value.trim();
    if (!newLocationName) return;

    try {
      const response = await fetch(API_PREFIX + "/location", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: newLocationName }),
      });

      if (!response.ok) {
        throw new Error("Failed to create location");
      }

      const newLocation = await response.json();

      allLocations.push(newLocation);
      selectedLocation = newLocation.name;
      updateSelectedLocationDisplay();

      // Clear input
      locationInput.value = "";
      locationDropdown.innerHTML = "";
      createLocationBtnContainer.classList.add("d-none");
      locationInput.disabled = true;
    } catch (error) {
      console.error("Error creating location:", error);
      showAlert("Failed to create location. Please try again.", "danger");
    }
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (!tagsInput.contains(e.target) && !tagsDropdown.contains(e.target)) {
      tagsDropdown.innerHTML = "";
    }
    if (
      !locationInput.contains(e.target) &&
      !locationDropdown.contains(e.target)
    ) {
      locationDropdown.innerHTML = "";
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
      quantity: parseInt(formData.get("quantity")),
      tags: selectedTags,
      location_id: formData.get("location_id")
        ? parseInt(formData.get("location_id"))
        : null,
      expires: formData.get("expires") || null,
    };

    console.log("Sending data:", data);

    // Determine if editing or creating
    const editingId = window.editingItemId;

    if (editingId) {
      console.log("Editing item with ID:", editingId);
      updateItem(editingId, data);
      showAlert("Item updated successfully!", "success");
      setTimeout(() => {
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("addItemModal")
        );
        if (modal) modal.hide();
        form.reset();
        hideAlert();
      }, 3);
      submitBtn.disabled = false;
      spinner.classList.add("d-none");
    } else {
      // Create new item (existing flow)
      fetch(API_PREFIX + "/items", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          console.log("Response status:", response.status);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((createdData) => {
          console.log("Success response:", createdData);
          showAlert("Item created successfully!", "success");

          // Try to add to table
          if (typeof window.addItemToTable === "function") {
            window.addItemToTable(createdData);
          } else {
            setTimeout(() => window.location.reload(), 100);
          }

          // Close modal after delay
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(
              document.getElementById("addItemModal")
            );
            if (modal) modal.hide();
            form.reset();
            hideAlert();
          }, 3);
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
    }

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
      // Clear edit state if any
      if (form.dataset.editingId) delete form.dataset.editingId;
      if (window.editingItemData) delete window.editingItemData;
      if (window.editingItemId) delete window.editingItemId;
      const idContainer = document.getElementById("modalItemIdContainer");
      const idValue = document.getElementById("modalItemIdValue");
      if (idContainer && idValue) {
        idValue.textContent = "";
        idContainer.classList.add("d-none");
      }
      const titleEl = document.getElementById("addItemModalLabel");
      const submitBtn = document.getElementById("createItemBtn");
      if (titleEl) titleEl.textContent = "Add Item";
      if (submitBtn) setButtonLabel(submitBtn, "Create");
    });
});
