// Constants
const EMPTY_PLACEHOLDER = "&mdash;";

// Date formatting functions
function formatDateOnly(dateString) {
    if (!dateString) return "";
    // For date-only strings (YYYY-MM-DD), parse without timezone conversion
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
        const [year, month, day] = dateString.split("-").map(Number);
        const date = new Date(year, month - 1, day); // month is 0-indexed
        return date.toLocaleDateString();
    }
    // For ISO datetime strings, extract date components
    const parsed = new Date(dateString);
    if (Number.isNaN(parsed.getTime())) return "";
    const year = parsed.getFullYear();
    const month = parsed.getMonth();
    const day = parsed.getDate();
    const localDate = new Date(year, month, day);
    return localDate.toLocaleDateString();
}

function formatDateDisplay(value, includeTime = false) {
    if (!value) return EMPTY_PLACEHOLDER;
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return EMPTY_PLACEHOLDER;
    return includeTime ? parsed.toLocaleString() : parsed.toLocaleDateString();
}

// General value formatting functions
function formatDisplayValue(value) {
    if (value === null || value === undefined) {
        return EMPTY_PLACEHOLDER;
    }
    if (typeof value === "string") {
        const trimmed = value.trim();
        return trimmed.length ? trimmed : EMPTY_PLACEHOLDER;
    }
    if (typeof value === "number") {
        return Number.isNaN(value) ? EMPTY_PLACEHOLDER : value;
    }
    return value || EMPTY_PLACEHOLDER;
}

// Tags formatting functions
function formatTagsDisplay(tags) {
    if (Array.isArray(tags)) {
        if (!tags.length) return EMPTY_PLACEHOLDER;
        const normalized = tags
            .map((tag) => {
                if (typeof tag === "string") return tag;
                if (tag && typeof tag.name === "string") return tag.name;
                return "";
            })
            .filter((tag) => tag && tag.trim().length);
        return normalized.length ? normalized.join(", ") : EMPTY_PLACEHOLDER;
    }
    if (typeof tags === "string") {
        return formatDisplayValue(tags);
    }
    return EMPTY_PLACEHOLDER;
}

// Location formatting functions
function getLocationDisplay(item) {
    if (!item) return EMPTY_PLACEHOLDER;
    const locationName =
        typeof item.location === "object" && item.location !== null
            ? item.location.name
            : item.location;
    const fallback = item.location_name || item.location_id || "";
    return formatDisplayValue(locationName || fallback);
}

// Make functions available globally
window.formatDateOnly = formatDateOnly;
window.formatDateDisplay = formatDateDisplay;
window.formatDisplayValue = formatDisplayValue;
window.formatTagsDisplay = formatTagsDisplay;
window.getLocationDisplay = getLocationDisplay;
window.EMPTY_PLACEHOLDER = EMPTY_PLACEHOLDER;

console.log("Utils loaded - formatting functions available globally");