// Dispara o carregamento assim que a árvore do documento estiver pronta
document.addEventListener('DOMContentLoaded', carregarCurriculo);

async function carregarCurriculo() {
  try {
    // Faz a requisição assíncrona do arquivo JSON unificado
    const resposta = await fetch('dados.json');
    
    if (!resposta.ok) {
      throw new Error(`Impossível ler o arquivo JSON: ${resposta.statusText}`);
    }
    
    const dados = await resposta.json();

    // Limpa os seletores nativos para evitar sobreposições
    document.querySelector('.left-column').innerHTML = '';
    document.querySelector('.right-column').innerHTML = '';
    
    // Injeção modular mapeando exatamente a estrutura do seu JSON
    aplicarTema(dados.tema);
    renderizarCabecalho(dados.pessoal);
    renderizarResumo(dados.resumo);
    renderizarExperiencia(dados.experiencia);
    renderizarEducacao(dados.educacao);
    renderizarCompetencias(dados.competencias);
    renderizarCursos(dados.cursos);
    renderizarIdiomas(dados.idiomas);

  } catch (error) {
    console.error('Falha crítica na compilação dos dados do QA:', error);
  }
}

// Injeta as chaves mapeadas diretamente na raiz do CSS (:root)
function aplicarTema(tema) {
  if (!tema) return;
  const root = document.documentElement;
  Object.entries(tema).forEach(([key, value]) => {
    root.style.setProperty(`--${key}`, value);
  });
}

function renderizarCabecalho(pessoal) {
  if (!pessoal) return;
  const header = document.querySelector('header');
  
  header.innerHTML = `
    <h1>${pessoal.nome || ''}</h1>
    ${pessoal.idade ? `<p class="age">Idade: ${pessoal.idade}</p>` : ''}
    <h2>${pessoal.profissao || ''}</h2>
    
    <div class="contact-info">
      <span>📍 ${pessoal.localizacao || ''}</span>
      <span>📧 <a href="mailto:${pessoal.email || ''}">${pessoal.email || ''}</a></span>
      <span>🔗 <a href="${pessoal.linkedin || ''}" target="_blank">linkedin.com/in/brunotcdesign</a></span>
    </div>
  `;
}

function renderizarResumo(resumo) {
  if (!resumo) return;
  const section = document.createElement('section');
  section.innerHTML = `
    <h3 class="section-title">Resumo Profissional</h3>
    <p class="summary-text">${resumo}</p>
  `;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarExperiencia(experiencias) {
  if (!experiencias || experiencias.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Experiência Profissional</h3>';
  
  experiencias.forEach(exp => {
    const atividades = exp.atividades || [];
    conteudo += `
      <div class="experience-item">
        <div class="job-title">${exp.cargo || ''}</div>
        <div class="company-time">
          <strong>${exp.empresa || ''}</strong>
          <span>${exp.periodo || ''} ${exp.duracao ? `(${exp.duracao})` : ''}</span>
        </div>
        <ul class="activities-list">
          ${atividades.map(ativ => `<li>${ativ}</li>`).join('')}
        </ul>
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.left-column').appendChild(section);
}

function renderizarEducacao(educacao) {
  if (!educacao || educacao.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Formação Acadêmica</h3>';
  
  educacao.forEach(edu => {
    conteudo += `
      <div class="experience-item">
        <div class="job-title">${edu.curso || ''}</div>
        <div class="company-time">
          <strong>${edu.instituicao || ''}</strong>
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
    <h3 class="section-title">Competências Técnicas</h3>
    <div class="tags-container">
      ${competencias.map(comp => `<span class="tag">${comp}</span>`).join('')}
    </div>
  `;
  document.querySelector('.right-column').appendChild(section);
}

function renderizarCursos(cursos) {
  if (!cursos || cursos.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Cursos e Especializações</h3>';
  
  cursos.forEach(cur => {
    conteudo += `
      <div class="cert-item">
        <strong>${cur.titulo || ''}</strong>
        ${cur.descricao ? `<p>${cur.descricao}</p>` : ''}
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.right-column').appendChild(section);
}

function renderizarIdiomas(idiomas) {
  if (!idiomas || idiomas.length === 0) return;
  const section = document.createElement('section');
  let conteudo = '<h3 class="section-title">Idiomas</h3>';
  
  idiomas.forEach(lang => {
    conteudo += `
      <div class="lang-item">
        <strong>${lang.idioma || ''}</strong>
        <span class="lang-level">${lang.nivel || ''}</span>
      </div>
    `;
  });
  
  section.innerHTML = conteudo;
  document.querySelector('.right-column').appendChild(section);
}
