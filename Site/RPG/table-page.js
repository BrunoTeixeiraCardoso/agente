let tableData = [];
let currentTableConfig = {
    jsonPath: './d100-table.json',
    indexHeader: 'd100',
    valueHeaderMale: 'Palavra-Chave',
    valueKeyMale: 'keyword',
    valueHeaderFemale: null,
    valueKeyFemale: null
};

async function loadTableData(config) {
    try {
        tableData = await fetchTableData(config.jsonPath);
        currentTableConfig = config;
        generateTableHeader(config);
        renderTable(config);
    } catch (error) {
        console.error('Erro:', error);
        const tbody = document.getElementById('table-body');
        if (tbody) {
            const { numColumns } = calculateLayout(tableData.length);
            const colspan = numColumns * (config.valueKeyFemale ? 3 : 2);
            tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading">Erro ao carregar tabela</td></tr>`;
        }
    }
}

function generateTableHeader(config) {
    const thead = document.querySelector('thead tr');
    const { numColumns } = calculateLayout(tableData.length);

    if (!thead) return;
    thead.innerHTML = '';

    for (let col = 0; col < numColumns; col++) {
        const thIndex = document.createElement('th');
        thIndex.textContent = config.indexHeader;
        thIndex.className = col > 0 ? 'separator center' : 'center';
        thead.appendChild(thIndex);

        const thMale = document.createElement('th');
        thMale.textContent = config.valueHeaderMale;
        thead.appendChild(thMale);

        if (config.valueKeyFemale) {
            const thFemale = document.createElement('th');
            thFemale.textContent = config.valueHeaderFemale;
            thead.appendChild(thFemale);
        }
    }
}

function renderTable(config) {
    const tbody = document.getElementById('table-body');
    if (!tbody) return;

    const { numColumns, itemsPerColumn } = calculateLayout(tableData.length);
    tbody.innerHTML = '';

    for (let row = 0; row < itemsPerColumn; row++) {
        const trElement = document.createElement('tr');

        for (let col = 0; col < numColumns; col++) {
            const itemIndex = col * itemsPerColumn + row;
            const entry = tableData[itemIndex];

            const cellIndex = document.createElement('td');
            cellIndex.className = 'dice-col';
            if (col > 0) cellIndex.classList.add('separator');
            cellIndex.textContent = entry ? String(entry.id).padStart(2, '0') : '';
            trElement.appendChild(cellIndex);

            const cellMale = document.createElement('td');
            cellMale.textContent = entry ? entry[config.valueKeyMale] : '';
            trElement.appendChild(cellMale);

            if (config.valueKeyFemale) {
                const cellFemale = document.createElement('td');
                cellFemale.textContent = entry ? entry[config.valueKeyFemale] : '';
                trElement.appendChild(cellFemale);
            }
        }

        tbody.appendChild(trElement);
    }
}

function rollTableItem(config) {
    const result = Math.floor(Math.random() * tableData.length) + 1;
    const resultEl = document.getElementById('roll-result');
    const keywordEl = document.getElementById('roll-keyword');
    const entry = tableData.find(item => item.id === result);

    if (resultEl) {
        resultEl.textContent = String(result).padStart(2, '0');
    }

    if (keywordEl) {
        if (entry) {
            keywordEl.textContent = config.valueKeyFemale
                ? `${entry[config.valueKeyMale]} / ${entry[config.valueKeyFemale]}`
                : entry[config.valueKeyMale];
        } else {
            keywordEl.textContent = 'Nenhum valor';
        }
    }
}

function parseTableConfig() {
    const tableElement = document.querySelector('[data-json]') || document.getElementById('table-d100') || document.getElementById('table-nomes');
    if (!tableElement) return null;

    return {
        jsonPath: tableElement.dataset.json || './d100-table.json',
        indexHeader: tableElement.dataset.indexHeader || 'd100',
        valueHeaderMale: tableElement.dataset.valueHeaderMale || tableElement.dataset.valueHeader || 'Palavra-Chave',
        valueKeyMale: tableElement.dataset.valueKeyMale || tableElement.dataset.valueKey || 'keyword',
        valueHeaderFemale: tableElement.dataset.valueHeaderFemale || null,
        valueKeyFemale: tableElement.dataset.valueKeyFemale || null
    };
}

function setupTablePage() {
    const tableBody = document.getElementById('table-body');
    if (!tableBody) return;

    const config = parseTableConfig();
    if (!config) return;

    const rollButton = document.getElementById('roll-btn');
    if (rollButton) {
        rollButton.addEventListener('click', () => rollTableItem(config));
    }

    loadTableData(config);
}

document.addEventListener('DOMContentLoaded', setupTablePage);
