class FilterManager {
    constructor(tableBodyId) {
        this.tableBodyId = tableBodyId;
        this.filters = {
            search: '',
            name: '',
            tags: [],
            location: ''
        };
    }

    applyFilters() {
        const rows = document.querySelectorAll(`#${this.tableBodyId} tr`);
        
        rows.forEach((row) => {
            if (row.querySelector('td[colspan]')) return;

            const cells = row.cells;
            const itemName = cells[1].textContent.toLowerCase();
            const itemTags = cells[3].textContent.toLowerCase();
            const itemLocation = cells[4].textContent.toLowerCase();

            const matchesSearch = !this.filters.search || 
                itemName.includes(this.filters.search) ||
                itemTags.includes(this.filters.search) ||
                itemLocation.includes(this.filters.search);

            const matchesName = !this.filters.name || itemName.includes(this.filters.name);
            const matchesLocation = !this.filters.location || itemLocation.includes(this.filters.location);
            
            const matchesTags = this.filters.tags.length === 0 || 
                this.filters.tags.some(tag => itemTags.includes(tag.toLowerCase()));

            const shouldShow = matchesSearch && matchesName && matchesLocation && matchesTags;
            row.style.display = shouldShow ? "" : "none";
        });
    }

    updateFilter(type, value) {
        if (type === 'tags') {
            this.filters.tags = Array.isArray(value) ? value : [value].filter(Boolean);
        } else {
            this.filters[type] = value.toLowerCase();
        }
        this.applyFilters();
    }

    clearFilters() {
        this.filters = { search: '', name: '', tags: [], location: '' };
        this.applyFilters();
        
        const searchInput = document.getElementById('search-input');
        const nameInput = document.getElementById('filter-name');
        const tagsDropdown = document.getElementById('filter-tags-dropdown');
        const locationDropdown = document.getElementById('filter-location-dropdown');
        
        if (searchInput) searchInput.value = '';
        if (nameInput) nameInput.value = '';
        if (tagsDropdown) tagsDropdown.selectedIndex = 0;
        if (locationDropdown) locationDropdown.selectedIndex = 0;
    }
}

window.FilterManager = FilterManager;


