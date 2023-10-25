//line

const ctx = document.getElementById('revenueChart').getContext('2d');

const monthlyData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  revenue: [1000, 1200, 1500, 1300, 1400, 1600, 1800, 1700, 1900, 2100, 2000, 2200],
};

const yearlyData = {
  labels: ['2020', '2021', '2022', '2023'],
  revenue: [25000, 28000, 32000, 30000],
};

const chartConfig = {
  type: 'line',
  data: {
    labels: monthlyData.labels, 
    datasets: [
      {
        label: 'Revenue',
        data: monthlyData.revenue, 
        fill: false,
        borderColor: '#0C144D', 
        borderWidth: 2, 
        backgroundColor: '#0C144D',

      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Sales Quantity', 
          },
        },
        yAxes: [{
          ticks: {
            beginAtZero: true,
            min: 0
          }
        }]
   
  
      },
  },
};

const myChart = new Chart(ctx, chartConfig);

const revenueFilter = document.getElementById('revenueFilter');
revenueFilter.value = 'monthly'; // Set the filter dropdown to 'monthly' by default

revenueFilter.addEventListener('change', () => {
  const selectedFilter = revenueFilter.value;
  const data = selectedFilter === 'monthly' ? monthlyData : yearlyData;

  myChart.data.labels = data.labels;
  myChart.data.datasets[0].data = data.revenue;
  myChart.update();
});

//horizontal bar


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

// Define a function to update the chart with data
function updateChart(labels, salesQuantities) {
    myChart1.data.labels = labels;
    myChart1.data.datasets[0].data = salesQuantities;
    myChart1.update();
  }
  
  // Example data (replace this with your actual data)
  const labels = ['Camping and Hiking Gear', 'Exercise and Fitness Gear', 'Sports Equipment','Outdoor Clothing'];
  const salesQuantities = [300, 200, 450, 600];
  
  // Call the function to update the chart with the data
  updateChart(labels, salesQuantities);
  


  //for dropdown icon
     $(document).ready(function () {
            $('.nav-link').on('click', function () {
                const icon = $(this).find('i');
                icon.toggleClass('fa-plus fa-minus');
            });
        });