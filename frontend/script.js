document.addEventListener('DOMContentLoaded', () => {
    const screens = {
        welcome: document.getElementById('welcome-screen'),
        modeSelection: document.getElementById('mode-selection-screen'),
        axiom: document.getElementById('axiom-screen'),
    };

    const beginButton = document.getElementById('begin-button');
    const redTeamConsent = document.getElementById('red-team-consent');
    const redTeamSelectButton = document.querySelector('[data-mode="red-team"]');
    const selectModeButtons = document.querySelectorAll('.select-mode-button');
    const backToModeSelectionButton = document.getElementById('back-to-mode-selection');

    const axiomHeader = document.getElementById('axiom-header');
    const axiomInput = document.getElementById('axiom-input');
    const addAxiomButton = document.getElementById('add-axiom-button');
    const axiomList = document.getElementById('axiom-list');

    const dilemmaContainer = document.getElementById('dilemma-container');
    const dilemmaText = document.getElementById('dilemma-text');
    const dilemmaOptions = document.getElementById('dilemma-options');
    const closeDilemmaButton = document.getElementById('close-dilemma-button');
    const redTeamDilemmaButton = document.getElementById('generate-red-team-dilemma-button');

    let currentMode = 'collaborative'; // Default mode

    const switchScreen = (screenName) => {
        Object.values(screens).forEach(screen => screen.style.display = 'none');
        screens[screenName].style.display = 'flex';
    };

    const fetchAxioms = async () => {
        try {
            const response = await fetch('/api/axioms');
            const axioms = await response.json();
            axiomList.innerHTML = '';
            axioms.forEach(axiom => {
                const li = document.createElement('li');

                const textSpan = document.createElement('span');
                textSpan.textContent = axiom.text;

                if (currentMode === 'red-team') {
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.dataset.axiomText = axiom.text;
                    checkbox.onchange = updateRedTeamButtonVisibility;
                    li.appendChild(checkbox);
                }

                li.appendChild(textSpan);
                li.dataset.id = axiom.id;

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.className = 'delete-axiom-button';
                deleteButton.onclick = () => deleteAxiom(axiom.id);

                const buttonGroup = document.createElement('div');
                if (currentMode === 'collaborative') {
                    const dilemmaButton = document.createElement('button');
                    dilemmaButton.textContent = 'Generate Dilemma';
                    dilemmaButton.className = 'generate-dilemma-button';
                    dilemmaButton.onclick = () => generateDilemma([axiom.text]);
                    buttonGroup.appendChild(dilemmaButton);
                }

                buttonGroup.appendChild(deleteButton);

                li.appendChild(buttonGroup);
                axiomList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching axioms:', error);
        }
    };

    const addAxiom = async () => {
        const text = axiomInput.value.trim();
        if (!text) return;

        try {
            const response = await fetch('/api/axioms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });
            if (response.ok) {
                axiomInput.value = '';
                fetchAxioms();
            }
        } catch (error) {
            console.error('Error adding axiom:', error);
        }
    };

    const deleteAxiom = async (id) => {
        try {
            const response = await fetch(`/api/axioms/${id}`, { method: 'DELETE' });
            if (response.ok) {
                fetchAxioms();
            }
        } catch (error) {
            console.error('Error deleting axiom:', error);
        }
    };

    const updateRedTeamButtonVisibility = () => {
        const selectedAxioms = axiomList.querySelectorAll('input[type="checkbox"]:checked');
        redTeamDilemmaButton.style.display = selectedAxioms.length === 2 ? 'block' : 'none';
    };

    const generateDilemma = async (axioms) => {
        try {
            const response = await fetch('/api/dilemma', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: currentMode, axioms: axioms }),
            });
            const dilemma = await response.json();

            dilemmaText.textContent = dilemma.dilemma_text;
            dilemmaOptions.innerHTML = '';
            dilemma.options.forEach(option => {
                const button = document.createElement('button');
                button.textContent = option;
                dilemmaOptions.appendChild(button);
            });

            dilemmaContainer.style.display = 'block';
        } catch (error) {
            console.error('Error generating dilemma:', error);
        }
    };

    closeDilemmaButton.addEventListener('click', () => {
        dilemmaContainer.style.display = 'none';
    });

    beginButton.addEventListener('click', () => switchScreen('modeSelection'));

    redTeamConsent.addEventListener('change', () => {
        redTeamSelectButton.disabled = !redTeamConsent.checked;
    });

    selectModeButtons.forEach(button => {
        button.addEventListener('click', () => {
            currentMode = button.dataset.mode;
            axiomHeader.textContent = `Axiom Management (${currentMode === 'collaborative' ? 'Collaborative Clarifier' : 'Personal Red-Team'})`;
            redTeamDilemmaButton.style.display = 'none';
            fetchAxioms();
            switchScreen('axiom');
        });
    });

    redTeamDilemmaButton.addEventListener('click', () => {
        const selectedAxioms = Array.from(axiomList.querySelectorAll('input[type="checkbox"]:checked'))
            .map(checkbox => checkbox.dataset.axiomText);
        generateDilemma(selectedAxioms);
    });

    backToModeSelectionButton.addEventListener('click', () => switchScreen('modeSelection'));
    addAxiomButton.addEventListener('click', addAxiom);
    axiomInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addAxiom();
    });

    // Start on the welcome screen
    switchScreen('welcome');
});
