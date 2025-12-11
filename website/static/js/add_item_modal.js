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

  // Detect page type from URL
  function getPageType() {
    const path = window.location.pathname;
    if (path.includes("/camera-gear")) {
      return "camera-gear";
    } else if (path.includes("/lab-equipment")) {
      return "lab-equipment";
    } else if (path.includes("/consumables")) {
      return "consumables";
    }
    return "home"; // default to home/items
  }

  // Show/hide fields based on page type
  function configureModalForPageType() {
    const pageType = getPageType();
    const quantityField = document.getElementById("quantity").closest(".mb-3");
    const expiresField = document.getElementById("expires").closest(".mb-3");
    const locationField = document
      .getElementById("location-input")
      .closest(".mb-3");
    const serviceFrequencyField = document.getElementById(
      "service-frequency-field"
    );
    const lastServicedField = document.getElementById("last-serviced-field");

    // Hide all optional fields first
    if (quantityField) quantityField.style.display = "none";
    if (expiresField) expiresField.style.display = "none";
    if (locationField) locationField.style.display = "none";
    if (serviceFrequencyField) serviceFrequencyField.style.display = "none";
    if (lastServicedField) lastServicedField.style.display = "none";

    // Show fields based on page type
    if (pageType === "home") {
      if (quantityField) quantityField.style.display = "block";
      if (expiresField) expiresField.style.display = "block";
      if (locationField) locationField.style.display = "block";
    } else if (pageType === "consumables") {
      if (quantityField) quantityField.style.display = "block";
      if (expiresField) expiresField.style.display = "block";
      if (locationField) locationField.style.display = "block";
    } else if (pageType === "camera-gear") {
      if (locationField) locationField.style.display = "block";
    } else if (pageType === "lab-equipment") {
      if (serviceFrequencyField) serviceFrequencyField.style.display = "block";
      if (lastServicedField) lastServicedField.style.display = "block";
    }
  }

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

  // Location functionality
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

  function updateItem(itemId, updatedData, endpoint) {
    const updateEndpoint = endpoint || `${window.API_PREFIX || "/api/v1"}/items/${itemId}`;
    fetch(updateEndpoint, {
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
        else if (typeof window.updateCameraGearInTable === "function")
          window.updateCameraGearInTable(data);
        else if (typeof window.updateLabEquipmentInTable === "function")
          window.updateLabEquipmentInTable(data);
      })
      .catch((err) => console.error("Failed to update item:", err));
  }
  // Fetch all tags from the database
  async function fetchTags() {
    try {
      const response = await fetch((window.API_PREFIX || "/api/v1") + "/tags/all");
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

  // Fetch all locations from the database
  async function fetchLocations() {
    try {
      const response = await fetch((window.API_PREFIX || "/api/v1") + "/location/all");
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
      // Configure fields based on page type
      configureModalForPageType();

      // Initialize tags
      await fetchTags();
      selectedTags = [];
      updateSelectedTagDisplay();
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      tagsInput.disabled = false;

      // Initialize locations
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
        const pageType = getPageType();
        console.log("Prefilling form for editing:", item.id);

        // Name (always present)
        document.getElementById("name").value = item.name || "";

        // Page-specific fields
        if (pageType === "consumables") {
          // Consumables
          document.getElementById("quantity").value = item.quantity;
          document.getElementById("expires").value = item.expires
            ? typeof item.expires === "string"
              ? item.expires.split("T")[0]
              : item.expires.split("T")[0]
            : "";
        } else if (pageType === "lab-equipment") {
          // Lab equipment
          const serviceFreqField = document.getElementById("service-frequency");
          if (serviceFreqField) {
            serviceFreqField.value = item.service_frequency || "";
          }
          const lastServicedField = document.getElementById("last-serviced");
          if (lastServicedField) {
            lastServicedField.value = item.last_serviced_on
              ? typeof item.last_serviced_on === "string"
                ? item.last_serviced_on.split("T")[0]
                : item.last_serviced_on.split("T")[0]
              : "";
          }
        }

        // Tags - select all tags if present
        if (Array.isArray(item.tags) && item.tags.length > 0) {
          // Set all tags from the item
          selectedTags = item.tags.map((tag) =>
            typeof tag === "string" ? tag : tag.name
          );
          updateSelectedTagDisplay();
        }

        if (
          (pageType === "home" ||
            pageType === "consumables" ||
            pageType === "camera-gear") &&
          item.location_id
        ) {
          // Find location name from allLocations
          const locationObj = allLocations.find(
            (loc) => loc.id === item.location_id
          );
          if (locationObj && typeof window.selectLocation === "function") {
            window.selectLocation(locationObj.name);
          } else {
            document.getElementById("location_id").value =
              item.location_id || "";
          }
        } else if (item.location) {
          // If location name is provided directly
          if (typeof window.selectLocation === "function") {
            window.selectLocation(item.location);
          }
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
    const query = e.target.value.trim().toLowerCase();

    if (query === "") {
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      return;
    }

    // Filter tags that match the query and are not already selected
    const matchingTags = allTags.filter((tag) => {
      const tagNameLower = tag.name.toLowerCase();
      const isMatching = tagNameLower.includes(query);
      const isNotSelected = !selectedTags.includes(tag.name);
      return isMatching && isNotSelected;
    });

    // Check if the query exactly matches an existing tag (that's not selected)
    const exactMatch = allTags.find(
      (tag) =>
        tag.name.toLowerCase() === query && !selectedTags.includes(tag.name)
    );

    if (exactMatch) {
      // Exact match found, show only that tag
      tagsDropdown.innerHTML = `
                <div class="tags-dropdown-item" onclick="selectTag('${exactMatch.name}')">
                    ${exactMatch.name}
                </div>
            `;
      createTagBtnContainer.classList.add("d-none");
    } else if (matchingTags.length > 0) {
      // Show matching tags (excluding already selected ones)
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
      // Check if this tag is already selected
      const queryTag = allTags.find((tag) => tag.name.toLowerCase() === query);
      if (queryTag && selectedTags.includes(queryTag.name)) {
        // Tag already selected, don't show create button
        tagsDropdown.innerHTML = "";
        createTagBtnContainer.classList.add("d-none");
      } else {
        // No matches, show create tag button
        tagsDropdown.innerHTML = "";
        newTagNameSpan.textContent = query;
        createTagBtnContainer.classList.remove("d-none");
      }
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
    // Only add if not already selected
    if (!selectedTags.includes(tagName)) {
      selectedTags.push(tagName);
      updateSelectedTagDisplay();
    }
    tagsInput.value = "";
    tagsDropdown.innerHTML = "";
    createTagBtnContainer.classList.add("d-none");
    tagsInput.focus();
  };

  // Handle location selection
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

  // Handle location removal
  window.removeLocation = function () {
    selectedLocation = null;
    updateSelectedLocationDisplay();
    locationInput.disabled = false;
    locationInput.focus();
  };

  // Update selected tag display
  function updateSelectedTagDisplay() {
    if (selectedTags.length === 0) {
      selectedTagsContainer.innerHTML = "";
      hiddenTagsInput.value = "";
    } else {
      selectedTagsContainer.innerHTML = selectedTags
        .map(
          (tag) => `
                <span class="badge bg-primary me-1 mb-1" style="font-size: 0.875rem;">
                    ${tag}
                    <button type="button" class="btn-close btn-close-white ms-1" onclick="removeTag('${tag}')" aria-label="Remove"></button>
                </span>
            `
        )
        .join("");
      hiddenTagsInput.value = selectedTags.join(", ");
    }
  }

  // Update selected location display
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

    // Check if tag already selected
    if (selectedTags.includes(newTagName)) {
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      return;
    }

    try {
      const response = await fetch((window.API_PREFIX || "/api/v1") + "/tags", {
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
      selectedTags.push(newTag.name);
      updateSelectedTagDisplay();

      // Clear input
      tagsInput.value = "";
      tagsDropdown.innerHTML = "";
      createTagBtnContainer.classList.add("d-none");
      // Don't disable input - allow adding more tags
      tagsInput.focus();
    } catch (error) {
      console.error("Error creating tag:", error);
      showAlert("Failed to create tag. Please try again.", "danger");
    }
  });

  // Handle create location button
  createLocationBtn.addEventListener("click", async function () {
    const newLocationName = locationInput.value.trim();
    if (!newLocationName) return;

    try {
      const response = await fetch((window.API_PREFIX || "/api/v1") + "/location", {
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
    const pageType = getPageType();

    // Build data object
    let data = {};

    if (pageType === "consumables") {
      // Consumables
      data = {
        name: formData.get("name"),
        quantity: parseInt(formData.get("quantity")),
        location_id: formData.get("location_id")
          ? parseInt(formData.get("location_id"))
          : null,
        expires: formData.get("expires") || null,
        tags: selectedTags,
      };
    } else if (pageType === "camera-gear") {
      // Camera gear
      data = {
        name: formData.get("name"),
        tags: selectedTags,
        location_id: formData.get("location_id")
          ? parseInt(formData.get("location_id"))
          : null,
      };
    } else if (pageType === "lab-equipment") {
      // Lab equipment
      data = {
        name: formData.get("name"),
        tags: selectedTags,
        service_frequency: formData.get("service-frequency") || null,
        last_serviced_on: formData.get("last-serviced") || null,
      };
    }

    console.log("Sending data:", data);

    // Determine if editing or creating
    const editingId = window.editingItemId;
    const apiEndpoint =
      pageType === "home"
        ? (window.API_PREFIX || "/api/v1") + "/items"
        : pageType === "consumables"
        ? (window.API_PREFIX || "/api/v1") + "/consumables/"
        : pageType === "camera-gear"
        ? (window.API_PREFIX || "/api/v1") + "/camera_gear/"
        : (window.API_PREFIX || "/api/v1") + "/lab_equipment/";

    if (editingId) {
      console.log("Editing item with ID:", editingId);
      const updateEndpoint =
        pageType === "home"
          ? `${window.API_PREFIX || "/api/v1"}/items/${editingId}`
          : pageType === "consumables"
          ? `${window.API_PREFIX || "/api/v1"}/consumables/${editingId}`
          : pageType === "camera-gear"
          ? `${window.API_PREFIX || "/api/v1"}/camera_gear/${editingId}`
          : `${window.API_PREFIX || "/api/v1"}/lab_equipment/${editingId}`;

      updateItem(editingId, data, updateEndpoint);
      showAlert("Item updated successfully!", "success");
      setTimeout(() => {
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("addItemModal")
        );
        if (modal) modal.hide();
        form.reset();
        hideAlert();
      }, 1500);
      submitBtn.disabled = false;
      spinner.classList.add("d-none");
    } else {
      // Create new item
      fetch(apiEndpoint, {
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
          } else if (typeof window.addCameraGearToTable === "function") {
            window.addCameraGearToTable(createdData);
          } else if (typeof window.addLabEquipmentToTable === "function") {
            window.addLabEquipmentToTable(createdData);
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
    }

    return false;
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
