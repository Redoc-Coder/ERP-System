function redirectTo(url) {
    window.location.href = url;
  }

  const itemsPerPage = 10; // Number of items to show per page
  let currentPage = 1;

  // Function to show/hide rows based on the current page
  function showPage(pageNumber) {
    const rows = document.querySelectorAll("tbody tr");
    const startIndex = (pageNumber - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;

    rows.forEach((row, index) => {
      if (index >= startIndex && index < endIndex) {
        row.classList.remove("hidden");
      } else {
        row.classList.add("hidden");
      }
    });
  }

  // Initially, show the first page
  showPage(currentPage);

  // Handle "Next" and "Previous" button clicks
  document.getElementById("prevPage").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      showPage(currentPage);
    }
  });

  document.getElementById("nextPage").addEventListener("click", () => {
    const totalRows = document.querySelectorAll("tbody tr").length;
    const totalPages = Math.ceil(totalRows / itemsPerPage);

    if (currentPage < totalPages) {
      currentPage++;
      showPage(currentPage);
    }
  });

  // Handle page number clicks
  document.getElementById("page1").addEventListener("click", () => {
    currentPage = 1;
    showPage(currentPage);
  });

  document.getElementById("page2").addEventListener("click", () => {
    currentPage = 2;
    showPage(currentPage);
  });   