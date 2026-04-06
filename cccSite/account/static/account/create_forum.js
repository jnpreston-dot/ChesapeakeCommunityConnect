// Track the current tab
let currentTab = 0;

// Initialize the form when the page loads
document.addEventListener("DOMContentLoaded", function () {
    showTab(currentTab);
});

// Display the specified tab
function showTab(n) {
    const tabs = document.getElementsByClassName("tab");
    const steps = document.getElementsByClassName("step-indicator");

    // Show the current tab
    tabs[n].style.display = "block";

    // Handle Back button visibility
    document.getElementById("prevBtn").style.display = n === 0 ? "none" : "inline-block";

    // Handle Continue button visibility
    document.getElementById("nextBtn").style.display = n === (tabs.length - 1) ? "none" : "inline-block";

    // Handle Submit button visibility
    const submitBtn = document.getElementById("id_submit");
    submitBtn.style.display = n === (tabs.length - 1) ? "inline-block" : "none";

    // Update step indicators
    updateStepIndicator(n);
}

// Move between tabs
function nextPrev(direction) {
    const tabs = document.getElementsByClassName("tab");

    // Hide the current tab
    tabs[currentTab].style.display = "none";

    // Move to the next or previous tab
    currentTab += direction;

    // Prevent going out of bounds
    if (currentTab < 0) currentTab = 0;
    if (currentTab >= tabs.length) currentTab = tabs.length - 1;

    // Show the new tab
    showTab(currentTab);
}

// Update the step indicator circles
function updateStepIndicator(n) {
    const steps = document.getElementsByClassName("step-indicator");

    // Remove active class from all
    for (let i = 0; i < steps.length; i++) {
        steps[i].classList.remove("active-step");
    }

    // Add active class to the current step
    steps[n].classList.add("active-step");
}
