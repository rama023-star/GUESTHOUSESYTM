document.querySelectorAll('form').forEach((form) => {
  if (!form.querySelector('input[name="room_id"]')) return;
  form.addEventListener('submit', () => {
    const button = form.querySelector('button[type="submit"],button:not([type])');
    if (button) { button.disabled = true; button.classList.add('tap-success'); }
  });
});
