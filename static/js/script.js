/* dark mode toggle script */

// Get theme toggle button
function toggleTheme() {
    document.body.classList.toggle("dark-mode");

    // Save theme to localStorage
    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.removeItem("theme");
    }
}

// Load saved theme on page load
window.onload = function() {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    }
};
