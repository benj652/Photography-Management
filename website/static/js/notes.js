const NOTES_API_BASE = "/api/v1/notes";

// Current note and item context
let currentNote = null;
let currentItemType = null;
let currentItemId = null;

// Cache for notes
let notesCache = {
  camera_gear: new Set(),
  lab_equipment: new Set(),
  consumable: new Set(),
};

/**
 * Open the notes modal for a specific item
 * @param {string} itemType - 'camera_gear', 'lab_equipment', or 'consumable'
 * @param {number} itemId - The ID of the item
 * @param {string} itemName - The name of the item
 */
async function openNotesModal(itemType, itemId, itemName) {
  currentItemType = itemType;
  currentItemId = itemId;

  // Update modal title with item name
  const itemNameEl = document.getElementById("notesItemName");
  const itemIdEl = document.getElementById("notesItemId");
  if (itemNameEl) itemNameEl.textContent = itemName || "Unknown";
  if (itemIdEl) itemIdEl.textContent = itemId;

  // Reset modal state
  resetNotesModal();

  // Show modal
  const modalEl = document.getElementById("notesModal");
  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  // Fetch existing note
  await loadNoteForItem(itemType, itemId);
}

/**
 * Load note for a specific item
 */
async function loadNoteForItem(itemType, itemId) {
  try {
    showNotesLoading(true);

    const response = await fetch(
      `${NOTES_API_BASE}/by-item/${itemType}/${itemId}`
    );

    if (response.status === 404 || response.status === 200) {
      const data = await response.json();

      if (data && data.id) {
        // Note exists
        currentNote = data;
        displayNote(data);
      } else {
        // No note exists
        showNoNoteState();
      }
    } else {
      throw new Error(`Failed to load note: ${response.status}`);
    }
  } catch (error) {
    console.error("Error loading note:", error);
    showNotesAlert("Failed to load note. Please try again.", "danger");
    showNoNoteState();
  } finally {
    showNotesLoading(false);
  }
}

/**
 * Display an existing note in the modal
 */
function displayNote(note) {
  const contentTextarea = document.getElementById("noteContent");
  const metadataDiv = document.getElementById("noteMetadata");
  const noNoteSection = document.getElementById("noNoteSection");
  const noteContentSection = document.getElementById("noteContentSection");
  const saveBtn = document.getElementById("saveNoteBtn");
  const saveBtnText = document.getElementById("saveNoteBtnText");
  const deleteBtn = document.getElementById("deleteNoteBtn");
  const saveNoteIcon = document.getElementById("saveNoteIcon");

  // Show note content section
  if (noteContentSection) noteContentSection.classList.remove("d-none");
  if (noNoteSection) noNoteSection.classList.add("d-none");

  // Populate content
  if (contentTextarea) {
    contentTextarea.value = note.content || "";
  }

  // Show metadata
  if (metadataDiv) {
    metadataDiv.classList.remove("d-none");
    const createdAtEl = document.getElementById("noteCreatedAt");
    const createdByEl = document.getElementById("noteCreatedBy");
    const updatedAtEl = document.getElementById("noteUpdatedAt");
    const updatedByEl = document.getElementById("noteUpdatedBy");

    if (createdAtEl && note.created_at) {
      createdAtEl.textContent = formatDateDisplay(note.created_at, true);
    }
    if (createdByEl) {
      createdByEl.textContent = note.created_by || "Unknown";
    }
    if (updatedAtEl && note.updated_at) {
      updatedAtEl.textContent = formatDateDisplay(note.updated_at, true);
    } else if (updatedAtEl) {
      updatedAtEl.textContent = "Never";
    }
    if (updatedByEl) {
      updatedByEl.textContent = note.updated_by || "N/A";
    }
  }

  // Update button text
  if (saveBtnText) saveBtnText.textContent = "Save Changes";

  // Show delete button if user has permission (TA or Admin)
  const canEdit = checkCanEditNote();
  if (deleteBtn) {
    if (canEdit) {
      deleteBtn.classList.remove("d-none");
    } else {
      deleteBtn.classList.add("d-none");
    }
  }

  // Make textarea read-only if user can't edit
  if (contentTextarea) {
    contentTextarea.readOnly = !canEdit;
    if (!canEdit) {
      contentTextarea.classList.add("bg-light");
    } else {
      contentTextarea.classList.remove("bg-light");
    }
  }

  // Hide "Add Note" text
  if (saveBtnText) saveBtnText.classList.add("d-none");
  if (saveNoteIcon) saveNoteIcon.classList.remove("d-none");
  if (saveBtn) {
    saveBtn.classList.remove("btn-primary");
    saveBtn.classList.add("btn-success");
  }
}

/**
 * Show no note state
 */
function showNoNoteState() {
  const noteContentSection = document.getElementById("noteContentSection");
  const noNoteSection = document.getElementById("noNoteSection");
  const metadataDiv = document.getElementById("noteMetadata");
  const saveBtn = document.getElementById("saveNoteBtn");
  const saveBtnText = document.getElementById("saveNoteBtnText");
  const saveNoteIcon = document.getElementById("saveNoteIcon");
  const deleteBtn = document.getElementById("deleteNoteBtn");
  const contentTextarea = document.getElementById("noteContent");

  // Hide textarea section
  if (noteContentSection) noteContentSection.classList.add("d-none");
  if (noNoteSection) noNoteSection.classList.remove("d-none");

  // Hide metadata
  if (metadataDiv) metadataDiv.classList.add("d-none");

  if (saveBtnText) {
    saveBtnText.textContent = "Add Note";
    saveBtnText.classList.remove("d-none");
  }
  if (saveNoteIcon) saveNoteIcon.classList.add("d-none");
  if (saveBtn) {
    saveBtn.classList.remove("btn-success");
    saveBtn.classList.add("btn-primary");
  }

  // Hide delete button
  if (deleteBtn) deleteBtn.classList.add("d-none");

  // Clear textarea
  if (contentTextarea) {
    contentTextarea.value = "";
    contentTextarea.readOnly = false;
    contentTextarea.classList.remove("bg-light");
    contentTextarea.placeholder = "Enter note content...";
  }

  currentNote = null;
}

/**
 * Show textarea for adding a new note
 */
function showTextareaForNewNote() {
  const noteContentSection = document.getElementById("noteContentSection");
  const noNoteSection = document.getElementById("noNoteSection");
  const saveBtnText = document.getElementById("saveNoteBtnText");
  const saveNoteIcon = document.getElementById("saveNoteIcon");
  const saveBtn = document.getElementById("saveNoteBtn");
  const contentTextarea = document.getElementById("noteContent");

  // Show textarea section, hide "no note" message
  if (noteContentSection) noteContentSection.classList.remove("d-none");
  if (noNoteSection) noNoteSection.classList.add("d-none");

  if (saveBtnText) saveBtnText.classList.add("d-none");
  if (saveNoteIcon) saveNoteIcon.classList.remove("d-none");
  if (saveBtn) {
    saveBtn.classList.remove("btn-primary");
    saveBtn.classList.add("btn-success");
  }

  // Focus on textarea
  if (contentTextarea) {
    contentTextarea.focus();
  }
}

/**
 * Reset modal to initial state
 */
function resetNotesModal() {
  const alertEl = document.getElementById("notesModalAlert");
  if (alertEl) {
    alertEl.classList.add("d-none");
    alertEl.textContent = "";
  }
  showNotesLoading(false);
}

/**
 * Show/hide loading state
 */
function showNotesLoading(loading) {
  const spinner = document.getElementById("saveNoteSpinner");
  const saveBtn = document.getElementById("saveNoteBtn");
  if (spinner) {
    if (loading) {
      spinner.classList.remove("d-none");
    } else {
      spinner.classList.add("d-none");
    }
  }
  if (saveBtn) {
    saveBtn.disabled = loading;
  }
}

/**
 * Show alert message
 */
function showNotesAlert(message, type = "info") {
  const alertEl = document.getElementById("notesModalAlert");
  if (alertEl) {
    alertEl.textContent = message;
    alertEl.className = `alert alert-${type}`;
    alertEl.classList.remove("d-none");
  }
}

/**
 * Check if current user can edit/delete notes (TA or Admin)
 */
function checkCanEditNote() {
  return (
    window.userData &&
    (window.userData.role === "Ta" ||
      window.userData.role === "Admin" ||
      window.userData.role === "TA")
  );
}

/**
 * Save note (create or update)
 */
async function saveNote() {
  const contentTextarea = document.getElementById("noteContent");
  const noteContentSection = document.getElementById("noteContentSection");
  const saveBtnText = document.getElementById("saveNoteBtnText");
  const saveNoteIcon = document.getElementById("saveNoteIcon");
  const saveBtn = document.getElementById("saveNoteBtn");

  if (!contentTextarea || !saveBtnText) return;

  if (noteContentSection && noteContentSection.classList.contains("d-none")) {
    if (saveBtnText.textContent.trim() === "Add Note") {
      showTextareaForNewNote();
      return;
    }
  }

  const content = contentTextarea.value.trim();

  if (!content) {
    showNotesAlert("Note content cannot be empty.", "warning");
    return;
  }

  if (!checkCanEditNote()) {
    showNotesAlert("You don't have permission to edit notes.", "danger");
    return;
  }

  try {
    showNotesLoading(true);
    hideNotesAlert();

    let response;
    if (currentNote) {
      // Update existing note
      response = await fetch(`${NOTES_API_BASE}/${currentNote.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: content,
        }),
      });
    } else {
      // Create new note
      response = await fetch(`${NOTES_API_BASE}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: content,
          item_type: currentItemType,
          item_id: currentItemId,
        }),
      });
    }

    if (response.ok) {
      const data = await response.json();
      currentNote = data;
      showNotesAlert(
        currentNote
          ? "Note updated successfully!"
          : "Note created successfully!",
        "success"
      );

      // Refresh notes cache
      if (typeof refreshNotesCache === "function") {
        await refreshNotesCache();
      }
      setTimeout(() => {
        const modalEl = document.getElementById("notesModal");
        if (modalEl) {
          const modal = bootstrap.Modal.getInstance(modalEl);
          if (modal) {
            modal.hide();
          }
        }
      }, 1000);
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to save note");
    }
  } catch (error) {
    console.error("Error saving note:", error);
    showNotesAlert("Failed to save note: " + error.message, "danger");
  } finally {
    showNotesLoading(false);
  }
}

/**
 * Delete note
 */
async function deleteNote() {
  if (!currentNote) return;

  if (!checkCanEditNote()) {
    showNotesAlert("You don't have permission to delete notes.", "danger");
    return;
  }

  if (
    !confirm(
      "Are you sure you want to delete this note? This action cannot be undone."
    )
  ) {
    return;
  }

  try {
    showNotesLoading(true);
    hideNotesAlert();

    const response = await fetch(`${NOTES_API_BASE}/${currentNote.id}`, {
      method: "DELETE",
    });

    if (response.ok) {
      showNotesAlert("Note deleted successfully!", "success");
      currentNote = null;

      // Refresh notes cache
      if (typeof refreshNotesCache === "function") {
        await refreshNotesCache();
      }

      setTimeout(() => {
        const modalEl = document.getElementById("notesModal");
        if (modalEl) {
          const modal = bootstrap.Modal.getInstance(modalEl);
          if (modal) {
            modal.hide();
          }
        }
      }, 1000);
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to delete note");
    }
  } catch (error) {
    console.error("Error deleting note:", error);
    showNotesAlert("Failed to delete note: " + error.message, "danger");
  } finally {
    showNotesLoading(false);
  }
}

/**
 * Hide alert
 */
function hideNotesAlert() {
  const alertEl = document.getElementById("notesModalAlert");
  if (alertEl) {
    alertEl.classList.add("d-none");
  }
}

/**
 * Load all notes and cache which items have notes
 */
async function loadNotesCache() {
  try {
    const response = await fetch(`${NOTES_API_BASE}/all`);
    if (response.ok) {
      const data = await response.json();
      const notes = data.notes || [];

      // Reset cache
      notesCache = {
        camera_gear: new Set(),
        lab_equipment: new Set(),
        consumable: new Set(),
      };

      // Populate cache
      notes.forEach((note) => {
        if (note.item_type && note.item_id) {
          if (notesCache[note.item_type]) {
            notesCache[note.item_type].add(note.item_id);
          }
        }
      });
    }
  } catch (error) {
    console.error("Error loading notes cache:", error);
  }
}

/**
 * Check if an item has a note
 */
function itemHasNote(itemType, itemId) {
  return notesCache[itemType] && notesCache[itemType].has(parseInt(itemId));
}

// Global function to refresh tables after notes cache update
window.refreshTablesWithNotes = null;

/**
 * Refresh notes cache (call after create/update/delete)
 */
async function refreshNotesCache() {
  await loadNotesCache();
  // Trigger a re-render of tables
  if (typeof window.refreshTablesWithNotes === "function") {
    window.refreshTablesWithNotes();
  }
}

// Initialize event listeners when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  const saveBtn = document.getElementById("saveNoteBtn");
  const deleteBtn = document.getElementById("deleteNoteBtn");
  const modalEl = document.getElementById("notesModal");

  if (saveBtn) {
    saveBtn.addEventListener("click", saveNote);
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", deleteNote);
  }

  // Reset modal when closed
  if (modalEl) {
    modalEl.addEventListener("hidden.bs.modal", function () {
      resetNotesModal();
      currentNote = null;
      currentItemType = null;
      currentItemId = null;
    });
  }
});

// Make function globally available
window.openNotesModal = openNotesModal;
window.loadNotesCache = loadNotesCache;
window.itemHasNote = itemHasNote;
