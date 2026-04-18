// JavaScript for ECHO

(function initializeTheme() {
    const savedTheme = localStorage.getItem("theme");
    document.addEventListener("DOMContentLoaded", function () {
        const body = document.body;
        const themeIcon = document.getElementById("theme-icon");
        const themeToggle = document.getElementById("theme-toggle");

        if (savedTheme === "dark") {
            body.classList.remove("light-theme");
            body.classList.add("dark-theme");
        } else {
            body.classList.remove("dark-theme");
            body.classList.add("light-theme");
        }

        if (themeIcon) {
            themeIcon.className = savedTheme === "dark" ? "fas fa-sun" : "fas fa-moon";
        }

        if (themeToggle) {
            themeToggle.addEventListener("click", function (event) {
                event.preventDefault();

                const darkModeEnabled = body.classList.contains("dark-theme");
                body.classList.toggle("dark-theme", !darkModeEnabled);
                body.classList.toggle("light-theme", darkModeEnabled);
                localStorage.setItem("theme", darkModeEnabled ? "light" : "dark");

                if (themeIcon) {
                    themeIcon.className = darkModeEnabled ? "fas fa-moon" : "fas fa-sun";
                }
            });
        }
    });
})();

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            alert.style.display = "none";
        }, 5000);
    });

    document.querySelectorAll("a[href^='#']").forEach(function (anchor) {
        anchor.addEventListener("click", function (event) {
            const target = document.querySelector(this.getAttribute("href"));
            if (!target) {
                return;
            }
            event.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });

    document.querySelectorAll("textarea[name='content']").forEach(function (textarea) {
        const readingTimeDisplay = document.createElement("small");
        readingTimeDisplay.className = "text-muted mt-1";
        readingTimeDisplay.style.display = "block";
        textarea.parentNode.appendChild(readingTimeDisplay);

        function updateReadingTime() {
            const trimmed = textarea.value.trim();
            const wordCount = trimmed ? trimmed.split(/\s+/).length : 0;
            const readingTime = Math.max(1, Math.ceil(wordCount / 200));
            readingTimeDisplay.textContent = "Estimated reading time: " + readingTime + " minute" + (readingTime !== 1 ? "s" : "") + " (" + wordCount + " words)";
        }

        textarea.addEventListener("input", updateReadingTime);
        updateReadingTime();
    });

    document.querySelectorAll("input[name='tags']").forEach(function (input) {
        input.addEventListener("blur", function () {
            const tags = this.value
                .split(",")
                .map(function (tag) { return tag.trim().toLowerCase(); })
                .filter(Boolean);
            this.value = Array.from(new Set(tags)).join(", ");
        });
    });

    document.addEventListener("keydown", function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === "k") {
            const searchInput = document.querySelector("input[name='query']");
            if (!searchInput) {
                return;
            }
            event.preventDefault();
            searchInput.focus();
        }
    });
});
