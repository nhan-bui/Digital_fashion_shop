function addToCart(category, user_id, pr_id){
     event.preventDefault()
     var size = "";
     if (category ==  1 || category == 3) {
        // Sản phẩm là loại quần áo
        size = document.getElementById("size_clothes").value; // Lấy giá trị size từ select size quần áo
      }
      else {
        // Sản phẩm là loại giày
        size = document.getElementById("size_shoe").value; // Lấy giá trị size từ select size giày
      }

     var quantity = document.getElementById("quantity").value; // Lấy giá trị số lượng từ input số lượng

      fetch('/api/add_item', {
        method: 'post',
        body: JSON.stringify({
          'pr_id': pr_id,
          'user_id': user_id,
          'quantity': quantity,
          'size': size,
        }),
        headers: {
          'Content-Type': 'application/json'
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'oke') {
            // Thông báo khi trạng thái là "oke"
            alert('Thêm vào giỏ hàng thành công!');
          } else {
            // Xử lý khi trạng thái không phải là "oke"
            alert('Có lỗi xảy ra. Vui lòng thử lại sau.');
          }
        })
        .catch(error => {
          // Xử lý lỗi (nếu có)
          alert('Có lỗi xảy ra. Vui lòng thử lại sau.');
        });



}