// JavaScript for ECHO

// Theme management - run immediately to prevent flash
(function() {
    const savedTheme = localStorage.getItem('theme');
    const body = document.body;
    
    if (savedTheme === 'dark') {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
    } else {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
    }
    
    // Set theme icon after DOM is ready
    setTimeout(function() {
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            if (savedTheme === 'dark') {
                themeIcon.className = 'fas fa-sun';
            } else {
                themeIcon.className = 'fas fa-moon';
            }
        }
    }, 100);
})();

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
    let themeToggle = document.getElementById('theme-toggle');
    let themeIcon = document.getElementById('theme-icon');
    
    // Fallback selectors in case IDs don't work
    if (!themeToggle) {
        themeToggle = document.querySelector('a[href="#"]');
    }
    if (!themeIcon) {
        themeIcon = document.querySelector('.fas.fa-moon, .fas.fa-sun');
    }
    
    console.log('Theme toggle element:', themeToggle);
    console.log('Theme icon element:', themeIcon);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Theme toggle clicked');
            
            // Toggle theme immediately
            const body = document.body;
            const isDark = body.classList.contains('dark-theme');
            
            console.log('Current theme is dark:', isDark);
            
            if (isDark) {
                body.classList.remove('dark-theme');
                body.classList.add('light-theme');
                if (themeIcon) {
                    themeIcon.className = 'fas fa-moon';
                }
                localStorage.setItem('theme', 'light');
                console.log('Switched to light theme');
            } else {
                body.classList.remove('light-theme');
                body.classList.add('dark-theme');
                if (themeIcon) {
                    themeIcon.className = 'fas fa-sun';
                }
                localStorage.setItem('theme', 'dark');
                console.log('Switched to dark theme');
            }
        });
    } else {
        console.error('Theme toggle button not found!');
    }

    // Theme icon initialization (theme class already set by immediate function)
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeIcon) {
        if (savedTheme === 'dark') {
            themeIcon.className = 'fas fa-sun';
        } else {
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