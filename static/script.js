// Admin

function toggleEdit(id) {
    var displayDiv = document.getElementById('display-' + id);
    var editForm = document.getElementById('edit-form-' + id);

    if (displayDiv.style.display === "none") {
        displayDiv.style.display = "block";
        editForm.style.display = "none";
    } else {
        displayDiv.style.display = "none";
        editForm.style.display = "block";
    }
}

// Product

function updateVariant(selectElement) {
    const productId = selectElement.getAttribute('data-product-id');

    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const variantId = selectElement.value;
    const stock = selectedOption.getAttribute('data-stock');

    const stockEl = document.getElementById('stock-' + productId);
    if (stockEl) {
        stockEl.innerText = stock;
    }

    const vidEl = document.getElementById('vid-' + productId);
    if (vidEl) {
        vidEl.value = variantId;
    }

    const wvidEl = document.getElementById('wvid-' + productId);
    if (wvidEl) {
        wvidEl.value = variantId;
    }

    const qtyInput = document.getElementById('qty-' + productId);
    if (qtyInput) {
        qtyInput.max = stock;

        if (parseInt(qtyInput.value) > parseInt(stock)) {
            qtyInput.value = stock;
        }
    }
}

// Checkout

function showPayment(method) {
    document.getElementById("card-form").style.display = "none";
    document.getElementById("paypal-form").style.display = "none";
    document.getElementById("cod-form").style.display = "none";

    if (method === "card") {
        document.getElementById("card-form").style.display = "block";
    }
    else if (method === "paypal") {
        document.getElementById("paypal-form").style.display = "block";
    }
    else if (method === "cod") {
        document.getElementById("cod-form").style.display = "block";
    }
}