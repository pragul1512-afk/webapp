let cart = [];

function addToCart(id, name, price) {
    // Convert ID to match types cleanly
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id: id, name: name, price: parseFloat(price), quantity: 1 });
    }
    console.log("Cart Updated:", cart);
    alert(`${name} added to cart!`);
}

async function checkout() {
    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    try {
        const response = await fetch('/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN // Uses global variable declared in index.html
            },
            body: JSON.stringify({ cart: cart })
        });
        
        if (response.ok) {
            alert("Order completed successfully!");
            cart = [];
            window.location.reload(); // Refresh to clean state
        } else {
            const errData = await response.json();
            alert("Checkout failed: " + errData.error);
        }
    } catch (error) {
        console.error("Error during checkout:", error);
        alert("An error occurred during checkout.");
    }
}
