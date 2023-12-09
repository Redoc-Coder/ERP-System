function logoutAndRedirect() {
    // Add any necessary logic for logging out (e.g., clearing session, making an AJAX request)
    
    // Clear the user session
    fetch('/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      // Redirect to the LandingPage after clearing the session
      window.location.href = '/login';
    })
    .catch(error => {
      console.error('Error:', error);
      // Handle errors if needed
    });
  }