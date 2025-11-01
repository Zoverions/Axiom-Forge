document.addEventListener('DOMContentLoaded', () => {
    const welcomeScreen = document.getElementById('welcome-screen');
    const modeSelectionScreen = document.getElementById('mode-selection-screen');
    const beginButton = document.getElementById('begin-button');
    const redTeamConsent = document.getElementById('red-team-consent');
    const redTeamSelectButton = document.querySelector('[data-mode="red-team"]');

    // Show welcome screen initially
    welcomeScreen.style.display = 'flex';

    beginButton.addEventListener('click', () => {
        welcomeScreen.style.display = 'none';
        modeSelectionScreen.style.display = 'flex';
    });

    redTeamConsent.addEventListener('change', () => {
        redTeamSelectButton.disabled = !redTeamConsent.checked;
    });
});
