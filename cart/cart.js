document.addEventListener("DOMContentLoaded", function () {
    function getCSRFToken() {
      return document.querySelector('meta[name="csrf-token"]').getAttribute("content");
    }
  
    document.querySelectorAll(".add-to-cart-btn").forEach(button => {
      button.addEventListener("click", function (event) {
        event.preventDefault();
  
        const productId = this.dataset.productId;
        const size = this.dataset.productSize || "M";
        const url = `/cart/add/${productId}/`;
  
        const formData = new FormData();
        formData.append("size", size);
        formData.append("quantity", 1);
  
        fetch(url, {
          method: "POST",
          body: formData,
          headers: {
            "X-CSRFToken": getCSRFToken()
          }
        })
          .then(res => res.json())
          .then(data => {
            if (data.cart_count !== undefined) {
              const cartCount = document.getElementById("cartCount")?.querySelector("span");
              if (cartCount) cartCount.textContent = data.cart_count;
              showSuccessToast(data.message);
              setTimeout(() => location.reload(), 1000);
            } else {
              alert("Error: " + data.error);
            }
          })
          .catch(err => {
            console.error("Add to cart failed:", err);
            alert("Failed to add to cart.");
          });
      });
    });
  
    function showSuccessToast(message) {
      const toast = document.createElement("div");
      toast.textContent = message;
      toast.style.position = "fixed";
      toast.style.bottom = "20px";
      toast.style.right = "20px";
      toast.style.background = "#28a745";
      toast.style.color = "white";
      toast.style.padding = "10px 20px";
      toast.style.borderRadius = "5px";
      toast.style.zIndex = "9999";
      toast.style.boxShadow = "0 0 10px rgba(0,0,0,0.3)";
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }
  });
  fetch(`/add-to-cart/${productId}/`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
        quantity: 1,
        size: 'M',
    })
})
.then(res => res.json())
.then(data => {
    console.log(data.message);
});

