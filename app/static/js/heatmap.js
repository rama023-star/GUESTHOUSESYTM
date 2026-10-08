document.querySelectorAll('#heatmap [data-cell]').forEach((button) => {
  button.addEventListener('click', () => {
    const cell = JSON.parse(button.dataset.cell);
    const label = new Date(`${cell.date}T00:00:00`).toLocaleDateString(undefined, {weekday:'long', year:'numeric', month:'long', day:'numeric'});
    document.getElementById('heat-detail').textContent = `${label} · ${window.GUESTFLOW_CURRENCY} ${Number(cell.revenue).toLocaleString()} · ${cell.bookings} bookings`;
  });
});
