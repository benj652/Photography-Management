
cat > static/js/edit_item_modal.js << 'EOF'
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('editItemModal');
    const form = modal.querySelector('form');

    document.querySelectorAll('.edit-item-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const item = this.dataset;

            // Set form action with item ID and preserve current URL params 
            const baseUrl = `/items/update/${item.id}`;
            const currentParams = window.location.search;
            form.action = baseUrl + currentParams;

            // Fill out the form fields
            form.querySelector('[name="name"]').value = item.name || '';
            form.querySelector('[name="quantity"]').value = item.quantity || 1;
            form.querySelector('[name="tags"]').value = item.tags || '';
            form.querySelector('[name="location_id"]').value = item.locationId || '';
            form.querySelector('[name="expires"]').value = item.expires || '';
        });
    });

    // Reset form when the modal closes
    modal.addEventListener('hidden.bs.modal', () => {
        form.reset();
        form.action = '';
    });
});
EOF