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

document.addEventListener('DOMContentLoaded', function() {
    console.log('Modal script loaded');
    
    const form = document.getElementById('addItemForm');
    const submitBtn = document.getElementById('createItemBtn');
    const spinner = submitBtn.querySelector('.spinner-border');
    const modalAlert = document.getElementById('modalAlert');
    
    if (!form) {
        console.error('Form not found!');
        return;
    }
    
    form.addEventListener('submit', function(e) {
        console.log('Form submitted - preventing default');
        e.preventDefault();
        e.stopPropagation();
        
        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        hideAlert();
        
        // Get form data
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            quantity: parseInt(formData.get('quantity')) || 1,
            tags: formData.get('tags') ? formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag) : [],
            location_id: formData.get('location_id') ? parseInt(formData.get('location_id')) : null,
            expires: formData.get('expires') || null
        };
        
        console.log('Sending data:', data);
        
        // Send request
        fetch('/items/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Success response:', data);
            showAlert('Item created successfully!', 'success');
            
            // Try to add to table
            if (typeof window.addItemToTable === 'function') {
                console.log('Adding item to table');
                window.addItemToTable(data);
            } else {
                console.log('addItemToTable function not found, reloading page');
                setTimeout(() => window.location.reload(), 100);
            }
            
            // Close modal after delay
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addItemModal'));
                if (modal) {
                    modal.hide();
                }
                form.reset();
                hideAlert();
            }, 1500);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error: ' + error.message, 'danger');
        })
        .finally(() => {
            // Reset button state
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
        });
        
        return false; // Extra prevention of form submission
    });
    
    function showAlert(message, type) {
        modalAlert.textContent = message;
        modalAlert.className = `alert alert-${type}`;
        modalAlert.classList.remove('d-none');
    }
    
    function hideAlert() {
        modalAlert.classList.add('d-none');
    }
    
    // Reset form when modal is closed
    document.getElementById('addItemModal').addEventListener('hidden.bs.modal', function() {
        form.reset();
        hideAlert();
    });
});