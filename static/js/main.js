// main.js

import { openModal, closeModal } from './modal.js';
import { handleFormSubmit } from './form.js';
import { highlightActiveTag, highlightContent, attachTagClickEvents, attachContentClickEvents } from './domUpdates.js';

// Attach event listeners
document.addEventListener('DOMContentLoaded', () => {
    attachTagClickEvents();
    attachContentClickEvents();

    // Handle form submissions
    handleFormSubmit('tagForm', '/save-tag/', 'POST');
    handleFormSubmit('attributeForm', '/save-attribute/', 'POST');
    handleFormSubmit('classForm', '/save-class/', 'POST');

    // Open modal buttons
    document.getElementById('openTagModal').addEventListener('click', () => openModal('tagModal'));
    document.getElementById('openAttributeModal').addEventListener('click', () => openModal('attributeModal'));
    document.getElementById('openClassModal').addEventListener('click', () => openModal('classModal'));
});
