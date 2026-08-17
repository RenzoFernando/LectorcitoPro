document.addEventListener('DOMContentLoaded', () => {
    const appMeta = window.APP_META || {};
    function setText(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined && value !== null) {
            element.textContent = value;
        }
    }
    function setHref(id, value) {
        const element = document.getElementById(id);
        if (element && value) {
            element.href = value;
        }
    }
    function normalizeRepositoryUrl(url) {
        if (!url) return '';
        return url.endsWith('.git') ? url.slice(0, -4) : url;
    }
    function buildReleaseAssetUrl(assetName) {
        const repositoryUrl = normalizeRepositoryUrl(appMeta.repositoryUrl || '');
        if (!repositoryUrl || !assetName) return '';
        return `${repositoryUrl}/releases/latest/download/${assetName}`;
    }
    function buildCreatorProfileUrl(repositoryUrl) {
        if (!repositoryUrl) return '';
        try {
            const url = new URL(repositoryUrl);
            const pathParts = url.pathname.split('/').filter(Boolean);
            if (pathParts.length >= 1) {
                return `${url.origin}/${pathParts[0]}`;
            }
        } catch (error) {
        }
        return '';
    }
    function applyAppMeta() {
        const displayName = appMeta.displayName || '';
        const versionText = appMeta.version ? `v${appMeta.version}` : '';
        const currentYear = appMeta.currentYear || new Date().getFullYear();
        const author = appMeta.author || '';
        const repositoryUrl = normalizeRepositoryUrl(appMeta.repositoryUrl || '');
        const creatorProfileUrl = buildCreatorProfileUrl(repositoryUrl);
        const installerDownloadUrl = appMeta.installerDownloadUrl || appMeta.downloadUrl || buildReleaseAssetUrl(appMeta.installerName || '');
        const portableDownloadUrl = appMeta.portableDownloadUrl || buildReleaseAssetUrl(appMeta.portableArtifactName || '');
        const linuxDownloadUrl = appMeta.linuxDownloadUrl || buildReleaseAssetUrl(appMeta.linuxArtifactName || '');
        if (displayName) {
            document.title = `Manual de Usuario - ${displayName}`;
        }
        setText('app-version-tag', versionText);
        setText('hero-app-name', displayName);
        setText('footer-app-name', displayName);
        setText('download-installer-title', `${displayName} Instalable`);
        setText('download-portable-title', `${displayName} Portable`);
        setText('download-linux-title', `${displayName} Portable`);
        if (author) {
            setText('footer-copyright', `© ${currentYear} — ${author}`);
        }
        setHref('hero-repo-link', repositoryUrl);
        setHref('download-repo-link', repositoryUrl);
        setHref('footer-app-link', repositoryUrl);
        setHref('download-installer-link', installerDownloadUrl);
        setHref('download-portable-link', portableDownloadUrl);
        setHref('download-linux-link', linuxDownloadUrl);
        setHref('creator-profile-link', creatorProfileUrl);
    }
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const appLogo = document.getElementById('app-logo');
    const githubIcon = document.getElementById('github-btn-icon');
    const downloadGithubIcon = document.getElementById('download-github-btn-icon');
    const navLinks = Array.from(document.querySelectorAll('.nav-link'));
    const trackedSections = Array.from(document.querySelectorAll('.section-anchor'));
    const downloadInfoButtons = Array.from(document.querySelectorAll('.download-info-btn'));
    function closeDownloadInfo(exceptButton = null) {
        downloadInfoButtons.forEach(button => {
            if (button === exceptButton) return;
            const panelId = button.getAttribute('aria-controls');
            const panel = panelId ? document.getElementById(panelId) : null;
            button.setAttribute('aria-expanded', 'false');
            if (panel) panel.hidden = true;
        });
    }
    downloadInfoButtons.forEach(button => {
        button.addEventListener('click', event => {
            event.stopPropagation();
            const panelId = button.getAttribute('aria-controls');
            const panel = panelId ? document.getElementById(panelId) : null;
            if (!panel) return;
            const willOpen = panel.hidden;
            closeDownloadInfo(button);
            panel.hidden = !willOpen;
            button.setAttribute('aria-expanded', String(willOpen));
        });
    });
    document.addEventListener('click', event => {
        if (!event.target.closest('.download-info-btn') && !event.target.closest('.download-info-panel')) {
            closeDownloadInfo();
        }
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            closeDownloadInfo();
        }
    });
    let isDarkMode = false;
    function updateThemeVisuals(isDark) {
        if (themeIcon) {
            themeIcon.src = isDark ? 'resources/icons/luna.png' : 'resources/icons/sol.png';
        }
        const logoSrc = isDark ? 'resources/branding/logo_claro.png' : 'resources/branding/logo_oscuro.png';
        if (appLogo) appLogo.src = logoSrc;
        const gitSrc = isDark ? 'resources/icons/github_claro.png' : 'resources/icons/github_oscuro.png';
        if (githubIcon) githubIcon.src = gitSrc;
        if (downloadGithubIcon) downloadGithubIcon.src = gitSrc;
    }
    function updateActiveNav() {
        const scrollPosition = window.scrollY + 120;
        let currentSectionId = 'intro';
        trackedSections.forEach(section => {
            if (section.offsetTop <= scrollPosition) {
                currentSectionId = section.id;
            }
        });
        navLinks.forEach(link => {
            const target = link.getAttribute('href');
            link.classList.toggle('active', target === `#${currentSectionId}`);
        });
    }
    applyAppMeta();
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            isDarkMode = document.body.classList.contains('dark-mode');
            updateThemeVisuals(isDarkMode);
        });
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-mode');
        isDarkMode = true;
    }
    updateThemeVisuals(isDarkMode);
    updateActiveNav();
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    const animatedElements = document.querySelectorAll('.fade-in-up');
    animatedElements.forEach(el => observer.observe(el));
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || !targetId.startsWith('#')) return;
            e.preventDefault();
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    window.addEventListener('scroll', updateActiveNav, { passive: true });
    window.addEventListener('resize', updateActiveNav);
});
