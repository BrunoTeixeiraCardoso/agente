// Animação de fade-in ao carregar a página
window.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    const nav = document.querySelector('nav');
    const sections = document.querySelectorAll('section');
    const footer = document.querySelector('footer');

    // Adicionar classe de fade-in
    header.classList.add('fade-in');
    nav.classList.add('fade-in');
    sections.forEach((section, index) => {
        section.classList.add('fade-in');
        section.style.animationDelay = `${index * 0.2}s`;
    });
    footer.classList.add('fade-in');
});

// Animação ao rolar a página (Intersection Observer)
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('slide-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observar todas as seções
document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
});

// Animação nos links de navegação
const navLinks = document.querySelectorAll('nav a');
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        navLinks.forEach(l => l.style.color = '');
        link.style.color = '#3498db';
        
        setTimeout(() => {
            link.style.color = '';
        }, 500);
    });
});

// Animação nos itens de serviço
const serviceItems = document.querySelectorAll('#servicos ul li');
serviceItems.forEach((item, index) => {
    item.addEventListener('mouseenter', () => {
        item.style.transform = 'translateX(10px)';
        item.style.transition = 'transform 0.3s ease';
    });

    item.addEventListener('mouseleave', () => {
        item.style.transform = 'translateX(0)';
    });
});

// Efeito de scroll smooth
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Animação ao passar mouse nas seções
const sections = document.querySelectorAll('section');
sections.forEach(section => {
    section.addEventListener('mouseenter', () => {
        section.style.transform = 'translateY(-5px)';
        section.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.2)';
        section.style.transition = 'all 0.3s ease';
    });

    section.addEventListener('mouseleave', () => {
        section.style.transform = 'translateY(0)';
        section.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
    });
});

// Animação de contadores (opcional para números)
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.textContent = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Log para confirmar que o arquivo foi carregado
console.log('✓ Animações carregadas com sucesso!');
