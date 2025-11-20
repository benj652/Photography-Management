
// Ensure API_PREFIX exists on this page
if (typeof API_PREFIX === "undefined") {
  var API_PREFIX = "/api/v1";
}

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

    let allTags = [];
    let selectedTags = [];

    function updateEquipment(equipmentId, updatedData) {
        return fetch(`${API_PREFIX}/lab_equipment/${equipmentId}`, {
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
                return data;
            })
            .catch((err) => console.error("Failed to update equipment:", err));

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


    // Initialize tags on modal open
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


            if (window.editingItemData) {
                const item = window.editingItemData;
                console.log("Prefilling form for editing:", item.id);

                // Name
                document.getElementById("name").value = item.name || "";

                // Service frequency
                const freqSelect = document.getElementById("service_frequency");
                if (freqSelect) {
                    freqSelect.value = item.service_frequency || "";
                }

                // Last serviced
                const lastServicedInput = document.getElementById("last_serviced_on");
                if (lastServicedInput) {
                    lastServicedInput.value = item.last_serviced_on
                        ? item.last_serviced_on.split("T")[0]
                        : "";
                }

                // Tags - support multi-select
                if (Array.isArray(item.tags) && item.tags.length > 0) {
                    selectedTags = item.tags
                        .map((tag) =>
                            typeof tag === "string"
                                ? tag
                                : (tag && tag.name) || ""
                        )
                        .filter(Boolean);
                } else {
                    selectedTags = [];
                }
                updateSelectedTagDisplay();

                // Mark form as editing
                const formEl = document.getElementById("addItemForm");
                if (formEl) formEl.dataset.editingId = item.id;

                // Show the ID at the top
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
                // New item – reset fields
                const formEl = document.getElementById("addItemForm");
                if (formEl) {
                    formEl.reset();
                    delete formEl.dataset.editingId;
                }
                selectedTags = [];
                updateSelectedTagDisplay();

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


    // Handle tag removal
    window.removeTag = function (tagName) {
        selectedTags = selectedTags.filter((tag) => tag !== tagName);
        updateSelectedTagDisplay();
        tagsInput.focus();
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
                    <button type="button" class="btn-close btn-close-white ms-1" onclick="removeTag(${JSON.stringify(
                        tag
                    )})" aria-label="Remove"></button>
                </span>
            `
                )
                .join("");
        }
        hiddenTagsInput.value = selectedTags.length
            ? JSON.stringify(selectedTags)
            : "";
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

        // Build the payload from the form
        const formData = new FormData(form);
        const data = {
            name: formData.get("name"),
            tags: selectedTags,
            service_frequency: formData.get("service_frequency") || null,
            last_serviced_on: formData.get("last_serviced_on") || null,
        };

        console.log("Sending data:", data);

        // Determine if we're editing or creating
        const editingId = window.editingItemId;

        if (editingId) {
            // ---- EDIT PATH ----
            console.log("Editing item with ID:", editingId);
            updateEquipment(editingId, data)
                .then(() => {
                    showAlert("Item updated successfully!", "success");

                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("addItemModal")
                    );
                    if (modal) modal.hide();

                    form.reset();
                    hideAlert();
                })
                .catch((err) => {
                    console.error("Failed to update equipment:", err);
                    showAlert("Failed to update equipment: " + err.message, "danger");
                })
                .finally(() => {
                    submitBtn.disabled = false;
                    spinner.classList.add("d-none");
                });
        } else {
            // ---- CREATE PATH ----
            fetch(API_PREFIX + "/lab_equipment", {
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

                    // Try to add to table (if the page defines this hook)
                    if (typeof window.addItemToTable === "function") {
                        window.addItemToTable(createdData);
                    }

                    // Close modal after a tiny delay (to let the alert render)
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
                    submitBtn.disabled = false;
                    spinner.classList.add("d-none");
                });
        }

        return false; // extra guard against default submit
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
            if (titleEl) titleEl.textContent = "Add Equipment";
            if (submitBtn) setButtonLabel(submitBtn, "Create");

        });
});

