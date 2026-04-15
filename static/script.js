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