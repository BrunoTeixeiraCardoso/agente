// Dispara o carregamento assim que a árvore do documento estiver pronta
document.addEventListener('DOMContentLoaded', carregarCurriculo);

async function carregarCurriculo() {
  try {
    // Faz a requisição assíncrona do arquivo JSON unificado
    const resposta = await fetch('data.json');
    
    if (!resposta.ok) {
      throw new Error(`Impossível ler o arquivo JSON: ${resposta.statusText}`);
    }
    
    const data = await resposta.json();

    // Limpa os seletores nativos para evitar sobreposições
    document.querySelector('.left-column').innerHTML = '';
    document.querySelector('.right-column').innerHTML = '';
    
    // Injeção modular mapeando exatamente a estrutura do seu JSON em inglês
    aplicarTema(data.theme);
    renderizarCabecalho(data.personal);
    renderizarResumo(data.summary);
    renderizarExperiencia(data.experience);
    renderizarEducacao(data.education);
    renderizarCompetencias(data.skills);
    renderizarCursos(data.courses);
    renderizarIdiomas(data.languages);

  } catch (error) {
    console.error('Falha crítica na compilação dos dados do QA:', error);
  }
}

// Injeta as chaves mapeadas diretamente na raiz do CSS (:root) aplicando camelCase para kebab-case
function aplicarTema(theme) {
  if (!theme) return;
  const root = document.documentElement;
  Object.entries(theme).forEach(([key, value]) => {
    // Converte chaves como containerBg para --container-bg, bgColor para --bg-color, etc.
    const kebabKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    root.style.setProperty(`--${kebabKey}`, value);
  });
}

function renderizarCabecalho(personal) {
  if (!personal) return;
  const header = document.querySelector('header');
  
  header.innerHTML = `
    <h1>${personal.name || ''}</h1>
    ${personal.age ? `<p class="age">Age: ${personal.age}</p>` : ''}
    <h2>${personal.profession || ''}</h2>
    
    <div class="contact-info">
      <span>📍 ${personal.location || ''}</span>
      <span>📧 <a href="mailto:${personal.email || ''}">${personal.email || ''}</a></span>
      <span>🔗 <a href="${personal.linkedin || ''}" target="_blank" rel="noopener noreferrer">${personal.linkedin ? personal.linkedin.replace('https://', '') : ''}</a></span>
    </div>
  `;
}

function renderizarResumo(summary) {
  if (!summary) return;
  const section = document.createElement('section');
  section.innerHTML = `
    <h3 class="section-title">Summary</h3>
    <p class="summary-text">${summary}</p>
  `;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarExperiencia(experience) {
  if (!experience || experience.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Professional Experience</h3>';
  
  experience.forEach(exp => {
    const activities = exp.activities || [];
    conteudo += `
      <div class="experience-item">
        <div class="job-title">${exp.role || ''}</div>
        <div class="company-time">
          <strong>${exp.company || ''}</strong>
          <span>${exp.period || ''} ${exp.duration ? `(${exp.duration})` : ''}</span>
        </div>
        <ul class="activities-list">
          ${activities.map(ativ => `<li>${ativ}</li>`).join('')}
        </ul>
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarEducacao(education) {
  if (!education || education.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Education</h3>';
  
  education.forEach(edu => {
    conteudo += `
      <div class="experience-item">
        <div class="job-title">${edu.course || ''}</div>
        <div class="company-time">
          <strong>${edu.institution || ''}</strong>
          <span>${edu.period || ''}</span>
        </div>
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarCompetencias(skills) {
  if (!skills || skills.length === 0) return;
  const section = document.createElement('section');
  
  section.innerHTML = `
    <h3 class="section-title">Skills</h3>
    <div class="tags-container">
      ${skills.map(skill => `<span class="tag">${skill}</span>`).join('')}
    </div>
  `;
  document.querySelector('.right-column').appendChild(section);
}

function renderizarCursos(courses) {
  if (!courses || courses.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Courses & Certifications</h3>';
  
  courses.forEach(cur => {
    conteudo += `
      <div class="cert-item">
        <strong>${cur.title || ''}</strong>
        ${cur.description ? `<p>${cur.description}</p>` : ''}
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.right-column').appendChild(section);
}

function renderizarIdiomas(languages) {
  if (!languages || languages.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Languages</h3>';
  
  languages.forEach(lang => {
    conteudo += `
      <div class="lang-item">
        <strong>${lang.language || ''}</strong>
        <span class="lang-level">${lang.level || ''}</span>
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.right-column').appendChild(section);
}
