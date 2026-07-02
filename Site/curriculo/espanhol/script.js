// Dispara o carregamento assim que a árvore do documento estiver pronta
document.addEventListener('DOMContentLoaded', carregarCurriculo);

async function carregarCurriculo() {
  try {
    // Faz a requisição assíncrona do arquivo JSON unificado
    const resposta = await fetch('dadosesp.json');
    
    if (!resposta.ok) {
      throw new Error(`Impossível ler o arquivo JSON: ${resposta.statusText}`);
    }
    
    const dadosesp = await resposta.json();

    // Limpa os seletores nativos para evitar sobreposições
    document.querySelector('.left-column').innerHTML = '';
    document.querySelector('.right-column').innerHTML = '';
    
    // Injeção modular mapeando exatamente a estrutura do seu JSON em espanhol
    aplicarTema(dadosesp.tema);
    renderizarCabecalho(dadosesp.personales);
    renderizarResumo(dadosesp.resumen);
    renderizarExperiencia(dadosesp.experiencia);
    renderizarEducacao(dadosesp.educacion);
    renderizarCompetencias(dadosesp.competencias);
    renderizarCursos(dadosesp.cursos);
    renderizarIdiomas(dadosesp.idiomas);

  } catch (error) {
    console.error('Falha crítica na compilação dos dados do QA:', error);
  }
}

// Injeta as chaves mapeadas diretamente na raiz do CSS (:root) aplicando camelCase para kebab-case
function aplicarTema(tema) {
  if (!tema) return;
  const root = document.documentElement;
  Object.entries(tema).forEach(([key, value]) => {
    // Converte chaves como containerBg para --container-bg, bgColor para --bg-color, etc.
    const kebabKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    root.style.setProperty(`--${kebabKey}`, value);
  });
}

function renderizarCabecalho(personales) {
  if (!personales) return;
  const header = document.querySelector('header');
  
  header.innerHTML = `
    <h1>${personales.nombre || ''}</h1>
    ${personales.edad ? `<p class="age">Age: ${personales.edad}</p>` : ''}
    <h2>${personales.profesion || ''}</h2>
    
    <div class="contact-info">
      <span>📍 ${personales.localizacion || ''}</span>
      <span>📧 <a href="mailto:${personales.email || ''}">${personales.email || ''}</a></span>
      <span>🔗 <a href="${personales.linkedin || ''}" target="_blank" rel="noopener noreferrer">${personales.linkedin ? personales.linkedin.replace('https://', '') : ''}</a></span>
    </div>
  `;
}

function renderizarResumo(resumen) {
  if (!resumen) return;
  const section = document.createElement('section');
  section.innerHTML = `
    <h3 class="section-title">Summary</h3>
    <p class="summary-text">${resumen}</p>
  `;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarExperiencia(experiencia) {
  if (!experiencia || experiencia.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Professional Experience</h3>';
  
  experiencia.forEach(exp => {
    const activities = exp.activities || [];
    conteudo += `
      <div class="experience-item">
        <div class="job-title">${exp.role || ''}</div>
        <div class="company-time">
          <strong>${exp.empresa || ''}</strong>
          <span>${exp.periodo || ''} ${exp.duracion ? `(${exp.duracion})` : ''}</span>
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

function renderizarEducacao(educacion) {
  if (!educacion || educacion.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Education</h3>';
  
  educacion.forEach(edu => {
    conteudo += `
      <div class="experience-item">
        <div class="job-title">${edu.curso || ''}</div>
        <div class="company-time">
          <strong>${edu.instituição || ''}</strong>
          <span>${edu.periodo || ''}</span>
        </div>
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarCompetencias(competencias) {
  if (!competencias || competencias.length === 0) return;
  const section = document.createElement('section');
  
  section.innerHTML = `
    <h3 class="section-title">Skills</h3>
    <div class="tags-container">
      ${competencias.map(competencias => `<span class="tag">${competencias}</span>`).join('')}
    </div>
  `;
  document.querySelector('.right-column').appendChild(section);
}

function renderizarCursos(cursos) {
  if (!cursos || cursos.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Courses & Certifications</h3>';
  
  cursos.forEach(cur => {
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

function renderizarIdiomas(idiomas) {
  if (!idiomas || idiomas.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Languages</h3>';
  
  idiomas.forEach(lang => {
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
