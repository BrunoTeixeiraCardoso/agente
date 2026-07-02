async function loadSidebar() {
    const sidebarContainer = document.getElementById('sidebar');
    if (!sidebarContainer) return;

    try {
        const response = await fetch('./sidebar.html');
        if (!response.ok) throw new Error('Falha ao carregar sidebar');

        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        const content = doc.body ? doc.body.innerHTML : text;
        sidebarContainer.innerHTML = content;
        markActiveSidebarLink();
    } catch (error) {
        console.error(error);
        sidebarContainer.innerHTML = '<aside class="sidebar"><p class="sidebar-error">Não foi possível carregar a sidebar.</p></aside>';
    }
}

function markActiveSidebarLink() {
    const currentPage = window.location.pathname.split('/').pop();
    const links = document.querySelectorAll('#sidebar nav a');

    links.forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === currentPage);
    });
}

async function fetchTableData(path) {
    const response = await fetch(path);
    if (!response.ok) {
        throw new Error(`Erro ao carregar JSON: ${response.status}`);
    }

    const data = await response.json();
    return data.entries || [];
}

function calculateLayout(totalItems) {
    let numColumns = 1;

    if (totalItems > 50) {
        numColumns = 4;
    } else if (totalItems > 25) {
        numColumns = 2;
    }

    const itemsPerColumn = Math.ceil(totalItems / numColumns);
    return { numColumns, itemsPerColumn };
}

document.addEventListener('DOMContentLoaded', () => {
    loadSidebar();
});
