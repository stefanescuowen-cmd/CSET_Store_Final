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