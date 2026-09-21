document.addEventListener("DOMContentLoaded", () => {
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
        if (!url) return "";
        return url.endsWith(".git") ? url.slice(0, -4) : url;
    }

    function buildReleaseAssetUrl(assetName) {
        const repositoryUrl = normalizeRepositoryUrl(appMeta.repositoryUrl || "");
        if (!repositoryUrl || !assetName) return "";
        return `${repositoryUrl}/releases/latest/download/${assetName}`;
    }

    function buildCreatorProfileUrl(repositoryUrl) {
        if (!repositoryUrl) return "";

        try {
            const url = new URL(repositoryUrl);
            const pathParts = url.pathname.split("/").filter(Boolean);
            if (pathParts.length >= 1) {
                return `${url.origin}/${pathParts[0]}`;
            }
        } catch {
            return "";
        }

        return "";
    }

    function applyAppMeta() {
        const displayName = appMeta.displayName || "Lectorcito Pro";
        const versionText = appMeta.version ? `v${appMeta.version}` : "";
        const currentYear = new Date().getFullYear();
        const author = appMeta.author || "";
        const repositoryUrl = normalizeRepositoryUrl(appMeta.repositoryUrl || "");
        const creatorProfileUrl = buildCreatorProfileUrl(repositoryUrl);
        const installerDownloadUrl =
            appMeta.installerDownloadUrl ||
            appMeta.downloadUrl ||
            buildReleaseAssetUrl(appMeta.installerName || "");
        const portableDownloadUrl =
            appMeta.portableDownloadUrl || buildReleaseAssetUrl(appMeta.portableArtifactName || "");
        const linuxDownloadUrl =
            appMeta.linuxDownloadUrl || buildReleaseAssetUrl(appMeta.linuxArtifactName || "");

        if (appMeta.documentTitle) {
            document.title = appMeta.documentTitle;
        }

        setText("app-version-tag", versionText);
        setText("hero-app-name", displayName);
        setText("footer-app-name", displayName);
        setText("download-installer-title", `${displayName} Instalable`);
        setText("download-portable-title", `${displayName} Portable`);
        setText("download-linux-title", `${displayName} Portable`);

        if (author) {
            setText("footer-copyright", `© ${currentYear} — ${author}`);
        }

        setHref("hero-repo-link", repositoryUrl);
        setHref("download-repo-link", repositoryUrl);
        setHref("footer-app-link", repositoryUrl);
        setHref("download-installer-link", installerDownloadUrl);
        setHref("download-portable-link", portableDownloadUrl);
        setHref("download-linux-link", linuxDownloadUrl);
        setHref("creator-profile-link", creatorProfileUrl);
    }

    const themeToggleBtn = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    const appLogo = document.getElementById("app-logo");
    const navLinks = Array.from(document.querySelectorAll(".nav-link"));
    const trackedSections = Array.from(document.querySelectorAll(".section-anchor"));
    const downloadInfoButtons = Array.from(document.querySelectorAll(".download-info-btn"));
    const shareButtons = Array.from(document.querySelectorAll("[data-share]"));
    const shareStatus = document.getElementById("share-status");

    function closeDownloadInfo(exceptButton = null) {
        downloadInfoButtons.forEach((button) => {
            if (button === exceptButton) return;

            const panelId = button.getAttribute("aria-controls");
            const panel = panelId ? document.getElementById(panelId) : null;
            button.setAttribute("aria-expanded", "false");
            if (panel) panel.hidden = true;
        });
    }

    downloadInfoButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.stopPropagation();

            const panelId = button.getAttribute("aria-controls");
            const panel = panelId ? document.getElementById(panelId) : null;
            if (!panel) return;

            const willOpen = panel.hidden;
            closeDownloadInfo(button);
            panel.hidden = !willOpen;
            button.setAttribute("aria-expanded", String(willOpen));
        });
    });

    document.addEventListener("click", (event) => {
        if (
            !event.target.closest(".download-info-btn") &&
            !event.target.closest(".download-info-panel")
        ) {
            closeDownloadInfo();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeDownloadInfo();
        }
    });

    let isDarkMode = false;

    function updateThemeVisuals(isDark) {
        if (themeIcon) {
            themeIcon.classList.toggle("icon-sun", !isDark);
            themeIcon.classList.toggle("icon-moon", isDark);
        }

        if (themeToggleBtn) {
            themeToggleBtn.setAttribute("aria-pressed", String(isDark));
            themeToggleBtn.setAttribute(
                "aria-label",
                isDark ? "Cambiar a tema claro" : "Cambiar a tema oscuro"
            );
        }

        const logoSrc = isDark
            ? "resources/branding/logo_dark_theme.png"
            : "resources/branding/logo_light_theme.png";
        if (appLogo) appLogo.src = logoSrc;
    }

    function updateActiveNav() {
        const scrollPosition = window.scrollY + 120;
        let currentSectionId = "intro";

        trackedSections.forEach((section) => {
            if (section.offsetTop <= scrollPosition) {
                currentSectionId = section.id;
            }
        });

        navLinks.forEach((link) => {
            const target = link.getAttribute("href");
            link.classList.toggle("active", target === `#${currentSectionId}`);
        });
    }

    async function copyShareUrl(url) {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(url);
            return;
        }

        const textarea = document.createElement("textarea");
        textarea.value = url;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
    }

    function announceShare(message) {
        if (shareStatus) shareStatus.textContent = message;
    }

    async function sharePage(button) {
        const shareData = {
            title: appMeta.documentTitle || document.title,
            text:
                appMeta.fileDescription ||
                "Lectorcito Pro: auditoría de código, documentación técnica y contexto para IA.",
            url: appMeta.websiteUrl || window.location.href
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
                announceShare("Contenido compartido.");
                return;
            }

            await copyShareUrl(shareData.url);
            const originalText = button.textContent;
            button.textContent = "Enlace copiado";
            announceShare("Enlace copiado al portapapeles.");
            window.setTimeout(() => {
                button.textContent = originalText;
            }, 1800);
        } catch (error) {
            if (error && error.name === "AbortError") return;
            announceShare("No se pudo compartir ni copiar el enlace.");
        }
    }

    shareButtons.forEach((button) => {
        button.addEventListener("click", () => sharePage(button));
    });

    applyAppMeta();

    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        document.body.classList.add("dark-mode");
        isDarkMode = true;
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            isDarkMode = document.body.classList.contains("dark-mode");
            updateThemeVisuals(isDarkMode);
        });
    }

    updateThemeVisuals(isDarkMode);
    updateActiveNav();

    const reduceMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if ("IntersectionObserver" in window && !reduceMotion) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.1,
                rootMargin: "0px 0px -50px 0px"
            }
        );

        document.querySelectorAll(".fade-in-up").forEach((element) => observer.observe(element));
    } else {
        document.querySelectorAll(".fade-in-up").forEach((element) => {
            element.classList.add("visible");
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (event) {
            const targetId = this.getAttribute("href");
            if (targetId === "#" || !targetId.startsWith("#")) return;

            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;

            event.preventDefault();
            const headerOffset = 80;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: reduceMotion ? "auto" : "smooth"
            });
        });
    });

    window.addEventListener("scroll", updateActiveNav, { passive: true });
    window.addEventListener("resize", updateActiveNav);
});
