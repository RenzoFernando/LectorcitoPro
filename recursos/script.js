document.addEventListener('DOMContentLoaded', () => {

    // --- ELEMENTOS DOM ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const appLogo = document.getElementById('app-logo');
    const downloadLogo = document.getElementById('download-logo');
    const githubIcon = document.getElementById('github-btn-icon');

    // Estado inicial
    let isDarkMode = false;

    // --- FUNCIÓN DE ACTUALIZACIÓN VISUAL ---
    function updateThemeVisuals(isDark) {
        // 1. Icono del botón Tema (Sol/Luna)
        // Si es oscuro, mostramos sol para cambiar a claro.
        themeIcon.src = isDark ? 'recursos/sol.png' : 'recursos/luna.png';

        // 2. Logos de la Aplicación (Invertidos al fondo)
        // Fondo web oscuro -> Logo Claro | Fondo web claro -> Logo Oscuro
        const logoSrc = isDark ? 'recursos/logo_claro.png' : 'recursos/logo_oscuro.png';
        if(appLogo) appLogo.src = logoSrc;
        if(downloadLogo) downloadLogo.src = logoSrc;

        // 3. Icono de Github en botón (Invertido)
        const gitSrc = isDark ? 'recursos/github_claro.png' : 'recursos/github_oscuro.png';
        if(githubIcon) githubIcon.src = gitSrc;

        // Nota: Los iconos de la "Barra de Herramientas" (tool-item) NO cambian.
        // Tienen la clase .bg-dark y siempre usan iconos _claro.png (blancos)
        // para mantener consistencia visual con la app real.
    }

    // --- MANEJADOR DE EVENTOS ---
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        isDarkMode = document.body.classList.contains('dark-mode');
        updateThemeVisuals(isDarkMode);
    });

    // --- DETECCIÓN AUTOMÁTICA DEL SISTEMA ---
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-mode');
        isDarkMode = true;
    }

    // Aplicar estado inicial
    updateThemeVisuals(isDarkMode);

    // --- ANIMACIONES AL HACER SCROLL (Intersection Observer) ---
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Solo animar una vez
            }
        });
    }, observerOptions);

    // Elementos a animar
    const animatedElements = document.querySelectorAll('.fade-in-up');
    animatedElements.forEach(el => observer.observe(el));

    // --- SCROLL SUAVE PARA LINKS ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if(targetElement){
                // Compensar la altura del navbar sticky
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            }
        });
    });
});