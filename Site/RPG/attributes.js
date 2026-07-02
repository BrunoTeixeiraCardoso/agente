function d6() {
    return Math.floor(Math.random() * 6) + 1;
}

function roll3d6() {
    return d6() + d6() + d6();
}

function getCurrentModifier(score) {
    const modValue = Math.floor((score - 10) / 2);
    return modValue >= 0 ? `+${modValue}` : `${modValue}`;
}

function generateAttributes() {
    const attributes = ['for', 'des', 'con', 'int', 'sab', 'car'];

    attributes.forEach(attr => {
        const score = roll3d6();
        const mod = getCurrentModifier(score);

        const scoreEl = document.getElementById(`${attr}-score`);
        const modEl = document.getElementById(`${attr}-mod`);

        if (scoreEl) scoreEl.textContent = score;
        if (modEl) modEl.textContent = mod;
    });
}

function setupAttributePage() {
    const generateButton = document.getElementById('generate-btn');
    if (!generateButton) return;

    generateButton.addEventListener('click', generateAttributes);
}

document.addEventListener('DOMContentLoaded', setupAttributePage);
