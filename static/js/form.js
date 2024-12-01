// form.js

async function submitForm(url, method, data) {
    const response = await fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(data)
    });

    return response.json();
}

function handleFormSubmit(formId, url, method) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const response = await submitForm(url, method, data);
        
        if (response.status === 'success') {
            window.location.reload();
        } else {
            alert('An error occurred. Please try again.');
        }
    });
}

export { handleFormSubmit };
