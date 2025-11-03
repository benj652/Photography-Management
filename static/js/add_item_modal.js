// Small script to open the Add Item modal when the button is clicked.
document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('openAddItemBtn');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
        try {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                var modalEl = document.getElementById('addItemModal');
                if (modalEl) {
                    var m = bootstrap.Modal.getOrCreateInstance(modalEl);
                    m.show();
                }
            } else {
                console.warn('Bootstrap JS not found; modal may not work.');
            }
        } catch (err) {
            console.error('Error showing modal:', err);
        }
    });
});
