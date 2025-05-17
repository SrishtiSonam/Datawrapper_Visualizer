 // Initialize the application when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            // Check if user is already logged in
            const token = localStorage.getItem('token');
            if (token) {
                // Validate token and load user data
                checkAuthStatus();
            }

            // Setup event listeners for auth forms
            setupAuthListeners();

            // Setup navigation event listeners
            document.getElementById('nav-home').addEventListener('click', showHomeSection);
            document.getElementById('nav-journals').addEventListener('click', showJournalsSection);
            document.getElementById('nav-create-journal').addEventListener('click', showCreateJournalSection);
            document.getElementById('create-journal-btn').addEventListener('click', showCreateJournalSection);
        });