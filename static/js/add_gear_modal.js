// Ensure API_PREFIX exists
if (typeof API_PREFIX === "undefined") {
  var API_PREFIX = "/api/v1";
}
const GEAR_API_BASE = API_PREFIX + "/camera_gear";


document.addEventListener("DOMContentLoaded", () => {
  console.log("Gear modal loaded");

  const form = document.getElementById("addItemForm");
  const submitBtn = document.getElementById("createItemBtn");
  const spinner = submitBtn.querySelector(".spinner-border");
  const modalAlert = document.getElementById("modalAlert");
  const modalEl = document.getElementById("addItemModal");

  // UI helpers
  function showAlert(msg, type = "success") {
    modalAlert.className = `alert alert-${type}`;
    modalAlert.textContent = msg;
    modalAlert.classList.remove("d-none");
  }
  function hideAlert() {
    modalAlert.classList.add("d-none");
  }
  function setBtnText(text) {
    // preserve spinner
    Array.from(submitBtn.childNodes)
      .filter((n) => n.nodeType === Node.TEXT_NODE)
      .forEach((n) => n.remove());
    submitBtn.appendChild(document.createTextNode(" " + text));
  }

  // ===========
  // TAGS (multi)
  // ===========
  const tagSearch = document.getElementById("tag-search");
  const tagsDropdown = document.getElementById("tags-dropdown");
  const tagsHidden = document.getElementById("tags-input");
  const selectedTagsWrap = document.getElementById("selected-tags");
  let allTags = [];
  let selectedTags = [];

  async function fetchTags() {
    try {
      const resp = await fetch(`${API_PREFIX}/tags/all`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      allTags = (data.tags || []).map((t) =>
        typeof t === "string" ? t : t?.name || ""
      ).filter(Boolean);
    } catch (e) {
      console.error("Failed to fetch tags:", e);
    }
  }

  function renderSelectedTags() {
    tagsHidden.value = JSON.stringify(selectedTags);
    selectedTagsWrap.innerHTML = selectedTags
      .map(
        (t) => `
      <span class="badge bg-primary me-2 mb-2">
        ${t}
        <button type="button" class="btn-close btn-close-white btn-sm ms-1" aria-label="Remove"
          onclick="(function(tag){ 
            window.__removeGearTag(tag);
          })('${t.replace(/'/g,"\\'")}')"></button>
      </span>`
      )
      .join("");
  }
  window.__removeGearTag = (tag) => {
    selectedTags = selectedTags.filter((x) => x !== tag);
    renderSelectedTags();
  };

  function openTagDropdown(matches) {
    if (!matches.length) {
      tagsDropdown.innerHTML = `
        <div class="p-2 text-muted">No matches. Press Enter to create “${tagSearch.value.trim()}”.</div>`;
    } else {
      tagsDropdown.innerHTML = matches
        .map(
          (t) => `
        <div class="p-2 tag-dropdown-item" role="button"
             onclick="(function(tag){
               window.__selectGearTag(tag);
             })('${t.replace(/'/g,"\\'")}')">${t}</div>`
        )
        .join("");
    }
    tagsDropdown.style.display = "block";
  }

  window.__selectGearTag = (tag) => {
    if (!selectedTags.includes(tag)) selectedTags.push(tag);
    renderSelectedTags();
    tagSearch.value = "";
    tagsDropdown.style.display = "none";
  };

  async function createTag(name) {
    try {
      const resp = await fetch(`${API_PREFIX}/tags/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ name }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const newTag = await resp.json();
      const tagName = newTag?.name || name;
      if (!allTags.includes(tagName)) allTags.push(tagName);
      __selectGearTag(tagName);
    } catch (e) {
      console.warn("Create tag failed, falling back to local add:", e);
      __selectGearTag(name);
    }
  }

  tagSearch.addEventListener("input", () => {
    const q = tagSearch.value.trim().toLowerCase();
    if (!q) {
      tagsDropdown.style.display = "none";
      return;
    }
    const matches = allTags.filter((t) => t.toLowerCase().includes(q) && !selectedTags.includes(t));
    openTagDropdown(matches);
  });
  tagSearch.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const name = tagSearch.value.trim();
      if (!name) return;
      if (allTags.includes(name)) {
        __selectGearTag(name);
      } else {
        createTag(name);
      }
    }
  });
  document.addEventListener("click", (e) => {
    if (!tagsDropdown.contains(e.target) && e.target !== tagSearch) {
      tagsDropdown.style.display = "none";
    }
  });

  // ==============
  // LOCATIONS
  // ==============
  const locationSelect = document.getElementById("location-select");
  async function fetchLocations() {
    try {
      const resp = await fetch(`${API_PREFIX}/location/all`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      const list = data.locations || [];
      locationSelect.innerHTML = `<option value="">Select location…</option>` + 
        list.map((loc) => `<option value="${loc.id}">${loc.name}</option>`).join("");
    } catch (e) {
      console.error("Failed to fetch locations:", e);
    }
  }

  // ==============
  // EDIT / CREATE
  // ==============
  function prefillIfEditing() {
    const editing = window.editingItemData;
    const idSpan = document.getElementById("modalItemIdValue");
    const idWrap = document.getElementById("modalItemIdContainer");

    if (!editing) {
      setBtnText("Create");
      idWrap.classList.add("d-none");
      form.reset();
      selectedTags = [];
      renderSelectedTags();
      return;
    }

    // Title + button
    setBtnText("Update");
    idWrap.classList.remove("d-none");
    idSpan.textContent = editing.id;

    // Fields
    document.getElementById("name").value = editing.name || "";
    selectedTags = Array.isArray(editing.tags) ? [...editing.tags] : [];
    renderSelectedTags();

    // location: server sends either location_id or name; we have id via to_dict
    if (editing.location_id) {
      locationSelect.value = String(editing.location_id);
    } else {
      locationSelect.value = "";
    }
  }

  // fetch tags/locations each time the modal opens; then prefill
  modalEl.addEventListener("shown.bs.modal", async () => {
    hideAlert();
    await Promise.all([fetchTags(), fetchLocations()]);
    prefillIfEditing();
  });

  modalEl.addEventListener("hidden.bs.modal", () => {
    window.editingItemId = null;
    window.editingItemData = null;
    form.reset();
    selectedTags = [];
    renderSelectedTags();
    setBtnText("Create");
  });

  // ==========
  // SUBMIT
  // ==========
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopPropagation();

    submitBtn.disabled = true;
    spinner.classList.remove("d-none");
    hideAlert();

    const data = {
      name: document.getElementById("name").value.trim(),
      tags: selectedTags,
      location_id: locationSelect.value || null,
    };

    const editingId = window.editingItemId;

    const done = () => {
      submitBtn.disabled = false;
      spinner.classList.add("d-none");
    };

    if (editingId) {
      // EDIT
      fetch(`${GEAR_API_BASE}/${editingId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data),
      })
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then((updated) => {
          if (typeof window.updateItemInTable === "function") window.updateItemInTable(updated);
          showAlert("Gear updated!", "success");
          setTimeout(() => {
            bootstrap.Modal.getInstance(modalEl)?.hide();
          }, 3);
        })
        .catch((err) => {
          console.error(err);
          showAlert(err.message || "Update failed", "danger");
        })
        .finally(done);
    } else {
      // CREATE
      fetch(`${GEAR_API_BASE}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data),
      })
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then((created) => {
          if (typeof window.addItemToTable === "function") window.addItemToTable(created);
          showAlert("Gear created!", "success");
          setTimeout(() => {
            bootstrap.Modal.getInstance(modalEl)?.hide();
          }, 3);
        })
        .catch((err) => {
          console.error(err);
          showAlert(err.message || "Create failed", "danger");
        })
        .finally(done);
    }
  });
});
