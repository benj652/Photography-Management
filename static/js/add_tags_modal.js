document.getElementById('add-tags-btn')?.addEventListener('click', () => {
    const ids = Array.from(document.querySelectorAll('.item-checkbox:checked'))
                     .map(cb => cb.value);
    document.getElementById('selected-item-ids').value = ids.join(',');
  });

  