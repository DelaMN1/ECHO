// JavaScript for ECHO

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.display = 'none';
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation feedback
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Reading time calculation for textareas
    const contentTextareas = document.querySelectorAll('textarea[name="content"]');
    contentTextareas.forEach(function(textarea) {
        const readingTimeDisplay = document.createElement('small');
        readingTimeDisplay.className = 'text-muted mt-1';
        readingTimeDisplay.style.display = 'block';
        textarea.parentNode.appendChild(readingTimeDisplay);

        function updateReadingTime() {
            const wordCount = textarea.value.trim().split(/\s+/).length;
            const readingTime = Math.max(1, Math.ceil(wordCount / 200));
            readingTimeDisplay.textContent = `Estimated reading time: ${readingTime} minute${readingTime !== 1 ? 's' : ''} (${wordCount} words)`;
        }

        textarea.addEventListener('input', updateReadingTime);
        updateReadingTime(); // Initial calculation
    });

    // Tag input enhancement
    const tagInputs = document.querySelectorAll('input[name="tags"]');
    tagInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            // Clean up tags (remove extra spaces, convert to lowercase)
            const tags = this.value.split(',').map(tag => tag.trim().toLowerCase()).filter(tag => tag);
            this.value = tags.join(', ');
        });
    });

    // Search form enhancement
    const searchForms = document.querySelectorAll('form[action*="search"]');
    searchForms.forEach(function(form) {
        const searchInput = form.querySelector('input[name="query"]');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    form.submit();
                }
            });
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="query"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    // Theme persistence - client-side only
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeToggle && themeIcon) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle theme immediately
            const body = document.body;
            const isDark = body.classList.contains('dark-theme');
            
            if (isDark) {
                body.classList.remove('dark-theme');
                body.classList.add('light-theme');
                themeIcon.className = 'fas fa-moon';
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light-theme');
                body.classList.add('dark-theme');
                themeIcon.className = 'fas fa-sun';
                localStorage.setItem('theme', 'dark');
            }
        });
    }

    // Load saved theme preference on page load
    const savedTheme = localStorage.getItem('theme');
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        if (themeIcon) {
            themeIcon.className = 'fas fa-sun';
        }
    } else {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        if (themeIcon) {
            themeIcon.className = 'fas fa-moon';
        }
    }
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions for use in templates
window.BlogApp = {
    formatDate: formatDate,
    formatDateTime: formatDateTime
};