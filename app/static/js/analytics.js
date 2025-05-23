const regionCtx = document.getElementById('regionChart');
new Chart(regionCtx, {
  type: 'bar',
  data: {
    labels: regionLabels,
    datasets: [{
      label: 'Predictions',
      data: regionCounts,
      backgroundColor: 'rgba(54, 162, 235, 0.6)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        ticks: { precision: 0 }
      }
    }
  }
});

const categoryCtx = document.getElementById('categoryChart');
new Chart(categoryCtx, {
  type: 'pie',
  data: {
    labels: categoryLabels,
    datasets: [{
      data: categoryCounts,
      backgroundColor: [
        '#36A2EB',
        '#FF6384',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40'
      ],
      hoverOffset: 6
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  }
});
