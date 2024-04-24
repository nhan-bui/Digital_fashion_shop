function changeActive(product_id) {
  event.preventDefault();

  // Get the button element
  const button = document.querySelector(`button[onclick="changeActive(${product_id})"]`);

  // Disable the button while waiting for the response
  button.disabled = true;

  fetch('/api/change_active', {
    method: 'post',
    body: JSON.stringify({
      'product_id': product_id,
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'oke') {
        // Update button text and background color based on the new active state

        button.innerText = data.active ? 'Ẩn' : 'Hiển thị';
        button.style.backgroundColor = data.active ? '#c75050' : '#3d85c6'; // Set appropriate colors for Active and Inactive states

        // Re-enable the button
        button.disabled = false;
      } else {
        // Handle error response
        alert('Có lỗi xảy ra. Vui lòng thử lại sau.');
        button.disabled = false; // Re-enable the button
      }
    })
    .catch(error => {
      // Handle network or other errors
      alert('Đã xảy ra lỗi');
      button.disabled = false; // Re-enable the button
    });
}
