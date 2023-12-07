document.addEventListener('DOMContentLoaded', function () {
  const ctx1 = document.getElementById('topSellingChart').getContext('2d');
  const chartConfig1 = {
      type: 'bar',
      data: {
          labels: [],
          datasets: [
              {
                  label: 'Best Selling Product Categories',
                  borderColor: '#0C144D',
                  data: [],
                  backgroundColor: '#0C144D',
                  borderWidth: 2,
              },
          ],
      },
      options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
              xAxes: [{
                  ticks: {
                      fontSize: 10,
                  },
              }],
              yAxes: [{
                  ticks: {
                      beginAtZero: true,
                      min: 0,
                  }
              }]
          },
      },
  };
  const myChart1 = new Chart(ctx1, chartConfig1);

  // Function to update the chart with data
  function updateChart(labels, salesQuantities) {
      myChart1.data.labels = labels;
      myChart1.data.datasets[0].data = salesQuantities;
      myChart1.update();
  }

  // Fetch the actual sales data from the server and update the chart
  fetch('/admin/admin-dashboard/data')
      .then(response => response.json())
      .then(data => {
          const labels = data.labels;
          const salesQuantities = data.salesQuantities;
          updateChart(labels, salesQuantities);
      })
      .catch(error => console.error('Error fetching data:', error));
});
