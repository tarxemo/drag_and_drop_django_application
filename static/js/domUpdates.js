// domUpdates.js

function highlightActiveTag(tagId) {
    document.querySelectorAll('.tag').forEach(tag => {
        tag.classList.remove('bg-yellow-100');
    });
    document.getElementById(tagId).classList.add('bg-yellow-100');
}

function highlightContent(tagId) {
    document.querySelectorAll('.content').forEach(content => {
        content.classList.remove('bg-blue-100');
    });
    document.querySelector(`#content-${tagId}`).classList.add('bg-blue-100');
}

function attachTagClickEvents() {
    document.querySelectorAll('.tag').forEach(tag => {
        tag.addEventListener('click', function() {
            highlightActiveTag(this.id);
            loadTagData(this.id);  // Function to load tag data into the form
        });
    });
}

function attachContentClickEvents() {
    document.querySelectorAll('.content').forEach(content => {
        content.addEventListener('click', function() {
            highlightContent(this.dataset.tagId);
            loadContentData(this.dataset.tagId);  // Function to load content data into the form
        });
    });
}

export { highlightActiveTag, highlightContent, attachTagClickEvents, attachContentClickEvents };
