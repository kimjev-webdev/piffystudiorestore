document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('nav-toggle');
    const navbarCollapse = document.getElementById('navbarNav');
    const menu = document.querySelector('.navbar-nav');
    if (!toggle || !navbarCollapse || !menu) return;

    const ICON_OPEN_DEG = 405;
    const ICON_CLOSED_DEG = 0;
    const ROTATE_MS = 450;
    const CLOSE_BUFFER_MS = 30;
    const CLOSE_ANIM_MS = ROTATE_MS + CLOSE_BUFFER_MS;

    const bsCollapse = new bootstrap.Collapse(navbarCollapse, { toggle: false });

    const icon = toggle.querySelector('img.nav-icon') || toggle.querySelector('img[src*="crossicon"]');
    if (!icon) console.warn('nav.js: nav icon not found inside #nav-toggle.');

    let logicalRotation = 0;
    window.__navLogicalRotation = () => logicalRotation;

    function rotateIconTo(targetDeg, duration = ROTATE_MS) {
        if (!icon) return;
        const fromDeg = logicalRotation;
        const toDeg = targetDeg;
        const fromStr = `rotate(${fromDeg}deg)`;
        const toStr = `rotate(${toDeg}deg)`;

        icon.style.transform = fromStr;
        const anim = icon.animate(
            [{ transform: fromStr }, { transform: toStr }],
            { duration, easing: 'cubic-bezier(.2,.9,.3,1)', fill: 'forwards' }
        );

        anim.onfinish = () => {
            icon.style.transform = toStr;
            logicalRotation = toDeg;
        };
        return anim;
    }

    // Adjust breathing and stagger logic here:
    const items = [];
    let rafId = null, startTime = null, breathing = false;

    function collectItems() {
        items.length = 0;
        const lis = Array.from(menu.querySelectorAll('li'));
        const subLis = Array.from(document.querySelectorAll('.submenu li'));
        const allLis = Array.from(new Set([...lis, ...subLis]));
        allLis.forEach(li => {
            const el = li.querySelector('.nav-item') || li.querySelector('button') || li.querySelector('a');
            if (!el) return;
            items.push({
                el,
                phase: Math.random() * Math.PI * 2,
                freq: 0.10 + Math.random() * 0.18,
                ampX: 1 + Math.random() * 3.0,
                ampY: 0.8 + Math.random() * 2.0,
                baseScale: 1
            });
            el.style.transformOrigin = 'center center';
            el.style.willChange = 'transform';
        });
    }

    function tick(now) {
        if (!startTime) startTime = now;
        const t = (now - startTime) / 1000;
        items.forEach(item => {
            const el = item.el;
            const hovered = el.matches(':hover') || el.classList.contains('active');
            const freq = item.freq * (hovered ? 1.4 : 1);
            const phase = item.phase;
            const sx = Math.sin((t * freq * Math.PI * 2) + phase);
            const sy = Math.cos((t * freq * Math.PI * 2) + phase * 1.07);
            const x = sx * item.ampX;
            const y = sy * item.ampY;
            const scale = item.baseScale * (hovered ? 1.045 : 1.0);
            const rot = (sx * item.ampX) * 0.6;
            el.style.transform = `translate(${x}px, ${y}px) rotate(${rot}deg) scale(${scale})`;
        });
        rafId = breathing ? requestAnimationFrame(tick) : null;
    }

    function startBreathing() {
        if (breathing) return;
        collectItems();
        if (items.length === 0) return;
        breathing = true;
        startTime = null;
        rafId = requestAnimationFrame(tick);
    }
    function stopBreathing() {
        breathing = false;
        if (rafId) cancelAnimationFrame(rafId);
        rafId = null;
        items.forEach(i => { i.el.style.transform = ''; i.el.style.willChange = ''; });
    }

    // Add staggered entrance after opening the navbar
    navbarCollapse.addEventListener('show.bs.collapse', () => {
        const target = (logicalRotation % 360) + ICON_OPEN_DEG + Math.floor(logicalRotation / 360) * 360;
        rotateIconTo(target);
        toggle.classList.add('active');
        menu.classList.add('open-active', 'open-hover', 'alive');
        document.querySelectorAll('.submenu').forEach(s => s.classList.add('open-active', 'alive'));
        startBreathing();

        setTimeout(() => {
            document.querySelectorAll('.navbar-nav > li').forEach((li, index) => {
                li.classList.add('staggered-entrance');
                li.style.animationDelay = `${index * 0.1}s`; // Adjust delay for staggered effect
            });
        }, 100);
    });

    // Adjust submenu item behavior
    document.querySelectorAll('.submenu li').forEach((submenuItem) => {
        submenuItem.style.animationDuration = "0.3s"; // reduce animation duration
        submenuItem.style.animationTimingFunction = "ease-out"; // more subtle ease
    });

    // Event listener to trigger staggered entrance class after animation
    document.querySelectorAll('.navbar-nav > li').forEach(item => {
        item.addEventListener('animationend', () => {
            item.classList.add('staggered-entered'); // Add class after animation ends
        });
    });

    navbarCollapse.addEventListener('hide.bs.collapse', () => {
        const target = logicalRotation - ICON_OPEN_DEG;
        rotateIconTo(target);
        toggle.classList.remove('active');
        menu.classList.remove('open-active', 'open-hover');
        document.querySelectorAll('.submenu').forEach(s => s.classList.remove('open-active'));
    });

    navbarCollapse.addEventListener('hidden.bs.collapse', () => {
        menu.classList.remove('alive', 'open-hover', 'open-active');
        document.querySelectorAll('.submenu').forEach(s => s.classList.remove('alive'));
        stopBreathing();
    });

    toggle.addEventListener('click', ev => {
        ev.stopPropagation();
        bsCollapse.toggle();
    });

    // Handle clicks outside the navbar
    document.addEventListener('click', ev => {
        const isOpen = navbarCollapse.classList.contains('show');
        if (!isOpen) return;
        if (!ev.target.closest('#navbar') && !ev.target.closest('#nav-toggle') && !ev.target.closest('#navbarNav')) {
            bsCollapse.hide();
        }
    });
});
