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

// Password

function togglePassword(inputId) {
    const pwInput = document.getElementById(inputId);
    if (pwInput.type === "password") {
        pwInput.type = "text";
    } else {
        pwInput.type = "password";
    }
}


// Account

function togglePassword() {
    const pwInput = document.getElementById("new_password");
    pwInput.type = pwInput.type === "password" ? "text" : "password";
}

function enablePasswordEdit() {
    console.log("Edit button clicked!");
    const pwInput = document.getElementById("new_password");
    
    if (!pwInput) {
        console.error("Could not find the new_password input!");
        return;
    }

    pwInput.readOnly = false;
    pwInput.disabled = false;
    
    pwInput.value = ""; 
    pwInput.placeholder = "Type new password...";
    
    pwInput.style.backgroundColor = "#ffffff";
    pwInput.style.border = "2px solid #007bff";
    
    setTimeout(() => {
        pwInput.focus();
    }, 10);
    
    document.getElementById("update-btn").style.display = "inline-block";
    document.getElementById("edit-btn").style.display = "none";
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

function setMainImage(productId, imageUrl) {
    const mainImg = document.getElementById('main-img-' + productId);
    if (mainImg) {
        mainImg.src = imageUrl;
    }
}

function openLightbox(imgSrc) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    lightboxImg.src = imgSrc;
    lightbox.style.display = 'flex';
}

function closeLightbox() {
    document.getElementById('lightbox').style.display = 'none';
}

// Add product
function addVariant() {
    const container = document.getElementById('variants-container');
    const variantGroup = document.createElement('div');
    variantGroup.className = 'variant-group';
    variantGroup.innerHTML = `
        <label>Color:</label>
        <input type="text" name="variant_color[]" required>

        <label>Size:</label>
        <input type="text" name="variant_size[]" required>

        <label>Stock:</label>
        <input type="number" name="variant_stock[]" min="0" required>

        <button type="button" onclick="removeVariant(this)">Remove</button>
    `;
    container.appendChild(variantGroup);
}

function removeVariant(btn) {
    btn.parentElement.remove();
}

function addImage() {
    const container = document.getElementById('images-container');
    const imageGroup = document.createElement('div');
    imageGroup.className = 'image-group';
    imageGroup.innerHTML = `
        <br>
        <label for="image">Image URL:</label>
        <input type="text" id="image" name="image" required>
        <button type="button" onclick="removeImage(this)">Remove</button>
    `;

    container.appendChild(imageGroup);
}

function removeImage(btn) {
    btn.parentElement.remove();
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

// Chat

function toggleRecipients() {
    var reason = document.getElementById('reason').value;
    document.getElementById('vendor_select').style.display = reason === 'question' ? 'block' : 'none';
    document.getElementById('admin_select').style.display = reason === 'return' ? 'block' : 'none';
    document.getElementById('return_select').style.display = reason === 'return' ? 'block' : 'none';
}


// Returns
function filterVariantsByOrder() {
    const orderSelect = document.getElementById('order_id');
    const variantSelect = document.getElementById('variant_id');
    const selectedOrderId = orderSelect.value;
    const variantOptions = variantSelect.querySelectorAll('option');

    document.getElementById('variant-select-group').style.display = "inline";

    // Reset the product selection
    variantSelect.value = "";

    variantOptions.forEach(option => {
        // Skip the placeholder option
        if (!option.getAttribute('data-order-id')) return;

        if (option.getAttribute('data-order-id') === selectedOrderId) {
            option.style.display = "block";
            option.disabled = false;
        } else {
            option.style.display = "none";
            option.disabled = true;
        }
    });
}