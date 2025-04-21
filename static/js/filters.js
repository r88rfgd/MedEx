document.addEventListener('DOMContentLoaded', function() {
    const categoryFilter = document.getElementById('category-filter');
    const searchInput = document.getElementById('search-input');
    const projectsContainer = document.getElementById('projects-container');
    const projectCards = document.querySelectorAll('.project-card');

    // Filter projects by category and search term
    function filterProjects() {
        const category = categoryFilter.value;
        const searchTerm = searchInput.value.toLowerCase();

        projectCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category');
            const cardTitle = card.querySelector('h4').textContent.toLowerCase();
            const cardDescription = card.querySelector('.project-description').textContent.toLowerCase();
            
            const matchesCategory = category === 'all' || cardCategory === category;
            const matchesSearch = cardTitle.includes(searchTerm) || cardDescription.includes(searchTerm);
            
            if (matchesCategory && matchesSearch) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });

        // Show "no projects" message if no results
        const visibleProjects = [...projectCards].filter(card => card.style.display !== 'none');
        const noProjectsMessage = document.querySelector('.no-projects');
        
        if (visibleProjects.length === 0 && !noProjectsMessage) {
            const message = document.createElement('p');
            message.className = 'no-projects';
            message.textContent = 'No projects match your filters.';
            projectsContainer.appendChild(message);
        } else if (visibleProjects.length > 0 && noProjectsMessage) {
            noProjectsMessage.remove();
        }
    }

    // Add event listeners
    categoryFilter.addEventListener('change', filterProjects);
    searchInput.addEventListener('input', filterProjects);
});