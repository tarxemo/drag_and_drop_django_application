// modal.js

function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Close modal on background click
document.querySelectorAll('.modal-background').forEach(background => {
    background.addEventListener('click', function() {
        closeModal(this.parentElement.id);
    });
});

// Close modal on close button click
document.querySelectorAll('.modal-close').forEach(button => {
    button.addEventListener('click', function() {
        closeModal(this.closest('.modal').id);
    });
});

export { openModal, closeModal };
