// modal.js
// Function to open a modal
function openModal(listingId) {
    // Get the modal by its id
    var modal = document.getElementById('modal-' + listingId);
    // Show the modal
    modal.style.display = "block";
}

// Function to close a modal
function closeModal(listingId) {
    // Get the modal by its id
    var modal = document.getElementById('modal-' + listingId);
    // Hide the modal
    modal.style.display = "none";
}

// Close modal when clicking anywhere outside of the modal-content
window.onclick = function (event) {
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function (modal) {
        if (event.target == modal) {
            closeModal(modal.id.split('-')[1]); // Get the listing ID from modal's id and close it
        }
    });
}