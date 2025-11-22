const toggle = document.getElementById("nav-toggle");
const menu = document.querySelector(".nav-menu");
const isTouch = matchMedia("(pointer: coarse)").matches;

document.body.dataset.input = isTouch ? "touch" : "mouse";

function updateIconState() {
    if (menu.classList.contains("open-active") || menu.classList.contains("open-hover")) {
        toggle.classList.add("active");
    } else {
        toggle.classList.remove("active");
    }
}

// CLICK → lock open / close
toggle.addEventListener("click", () => {
    menu.classList.toggle("open-active");
    updateIconState();
});

// HOVER BEHAVIOR (desktop)
if (!isTouch) {

    toggle.addEventListener("mouseenter", () => {
        menu.classList.add("open-hover");
        updateIconState();
    });

    menu.addEventListener("mouseenter", () => {
        menu.classList.add("open-hover");
        updateIconState();
    });

    function closeHoverIfOut() {
        if (!toggle.matches(":hover") && !menu.matches(":hover") && !menu.classList.contains("open-active")) {
            menu.classList.remove("open-hover");
            updateIconState();
        }
    }

    toggle.addEventListener("mouseleave", closeHoverIfOut);
    menu.addEventListener("mouseleave", closeHoverIfOut);
}
