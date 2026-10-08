(() => {
  const canvas = document.getElementById('revenue-chart');
  if (!canvas || !window.GUESTFLOW_CHART || typeof Chart === 'undefined') return;
  const points = window.GUESTFLOW_CHART;
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: points.map((point) => point.date.slice(5)),
      datasets: [{
        label: `Revenue (${window.GUESTFLOW_CURRENCY})`,
        data: points.map((point) => point.revenue),
        backgroundColor: '#f97316',
        borderRadius: 4,
        maxBarThickness: 22
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (item) => `${window.GUESTFLOW_CURRENCY} ${Number(item.raw).toLocaleString()} · ${points[item.dataIndex].bookings} bookings` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 7 } },
        y: { beginAtZero: true, ticks: { callback: (value) => Number(value).toLocaleString() } }
      },
      onClick: (_event, elements) => {
        const element = elements[0];
        if (!element) return;
        const point = points[element.index];
        document.getElementById('heat-detail').textContent = `${point.date}: ${window.GUESTFLOW_CURRENCY} ${Number(point.revenue).toLocaleString()} · ${point.bookings} bookings`;
      }
    }
  });
})();
