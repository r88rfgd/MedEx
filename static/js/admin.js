document.addEventListener('DOMContentLoaded', function() {
    // Admin panel tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Show target tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${targetTab}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });

    // Project deletion
    const deleteButtons = document.querySelectorAll('.delete-project');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const projectId = button.getAttribute('data-id');
            
            if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
                // Send delete request
                fetch(`/api/delete_project/${projectId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // If on admin panel, remove row
                        const row = button.closest('tr');
                        if (row) {
                            row.remove();
                        } else {
                            // If on project detail page, redirect to home
                            window.location.href = '/';
                        }
                    } else {
                        alert('Failed to delete project.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while deleting the project.');
                });
            }
        });
    });
});