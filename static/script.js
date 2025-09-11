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

    // Theme persistence
    const themeToggle = document.querySelector('a[href*="toggle-theme"]');
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            // Add a small delay to allow the theme change to take effect
            setTimeout(function() {
                localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
            }, 100);
        });
    }

    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme && savedTheme !== (document.body.classList.contains('dark-theme') ? 'dark' : 'light')) {
        // Theme doesn't match saved preference, redirect to toggle
        if (savedTheme === 'dark' && !document.body.classList.contains('dark-theme')) {
            window.location.href = '/toggle-theme';
        } else if (savedTheme === 'light' && document.body.classList.contains('dark-theme')) {
            window.location.href = '/toggle-theme';
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