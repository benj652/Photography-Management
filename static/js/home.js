// Function to fetch items from the server
async function fetchItems() {
	try {
		console.log('Fetching items from /items/all');
		const response = await fetch('/items/all');
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const items = await response.json();
		console.log('Fetched items:', items);
		populateTable(items);
	} catch (error) {
		console.error("Failed to fetch items:", error);
		showEmptyState("Failed to load items. Please refresh the page.");
	}
}

// Function to populate the table
function populateTable(items) {
	const tableBody = document.getElementById("items-table-body");
	tableBody.innerHTML = ""; // Clear existing rows

	if (items && items.length > 0) {
		items.forEach(item => {
			const row = document.createElement("tr");
			
			// Handle tags display - could be array or string
			const tags = Array.isArray(item.tags) ? item.tags.join(', ') : (item.tags || '');
			
			// Format dates properly
			const expires = item.expires ? new Date(item.expires).toLocaleDateString() : '';
			const lastUpdated = item.last_updated ? new Date(item.last_updated).toLocaleString() : '';

			row.innerHTML = `
				<td>${item.id || ''}</td>
				<td>${item.name || ''}</td>
				<td>${item.quantity || ''}</td>
				<td>${tags}</td>
				<td>${item.location || ''}</td>
				<td>${expires}</td>
				<td>${lastUpdated}</td>
				<td>${item.updated_by || ''}</td>
			`;

			tableBody.appendChild(row);
		});
	} else {
		showEmptyState("No items found. Click 'Add Item' to get started.");
	}
}

// Function to show empty state
function showEmptyState(message) {
	const tableBody = document.getElementById("items-table-body");
	const row = document.createElement("tr");
	row.innerHTML = `
		<td colspan="8" class="text-center text-muted py-4">
			${message}
		</td>
	`;
	tableBody.appendChild(row);
}

// Function to add a new item to the table (called from modal) - MAKE IT GLOBAL
window.addItemToTable = function(item) {
	console.log('Adding item to table:', item);
	const tableBody = document.getElementById('items-table-body');
	
	if (!tableBody) {
		console.error('Table body not found!');
		return;
	}
	
	// Remove "no items" message if it exists
	const noItemsRow = tableBody.querySelector('td[colspan="8"]');
	if (noItemsRow) {
		noItemsRow.parentElement.remove();
	}
	
	// Create new row - handle both response formats
	const row = document.createElement('tr');
	const tags = Array.isArray(item.tags) ? item.tags.join(', ') : (item.tags || '');
	const expires = item.expires ? new Date(item.expires).toLocaleDateString() : '';
	const last_updated = item.last_updated ? new Date(item.last_updated).toLocaleString() : '';
	
	row.innerHTML = `
		<td>${item.id || ''}</td>
		<td>${item.name || ''}</td>
		<td>${item.quantity || ''}</td>
		<td>${tags}</td>
		<td>${item.location || item.location_id || ''}</td>
		<td>${expires}</td>
		<td>${last_updated}</td>
		<td>${item.updated_by || ''}</td>
	`;
	
	// Add to beginning of table
	tableBody.insertBefore(row, tableBody.firstChild);
	
	// Add highlight effect
	row.classList.add('table-success');
	setTimeout(() => {
		row.classList.remove('table-success');
	}, 2000);
	
	console.log('Item added to table successfully');
};

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
	console.log('Home.js loaded');
	fetchItems();
});