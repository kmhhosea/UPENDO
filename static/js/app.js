const labels = JSON.parse(document.getElementById('trend-labels')?.textContent || '[]');
const income = JSON.parse(document.getElementById('trend-income')?.textContent || '[]');
const expense = JSON.parse(document.getElementById('trend-expense')?.textContent || '[]');

const ctx = document.getElementById('trendChart');
if (ctx && labels.length) {
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Income', data: income, borderColor: '#16a34a', tension: 0.35 },
        { label: 'Expense', data: expense, borderColor: '#dc2626', tension: 0.35 },
      ],
    },
  });
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/static/sw.js'));
}
