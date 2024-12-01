// Add an alert for admin actions
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".action").forEach(function (actionButton) {
        actionButton.addEventListener("click", function () {
            alert("Are you sure you want to perform this action?");
        });
    });
});
