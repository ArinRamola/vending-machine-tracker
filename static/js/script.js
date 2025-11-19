// Smooth fade-in animation for every page
document.addEventListener("DOMContentLoaded", () => {
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.transition = "opacity 0.7s";
        document.body.style.opacity = 1;
    }, 50);
});

// Button ripple effect
document.querySelectorAll("button, .btn").forEach(btn => {
    btn.addEventListener("click", function (e) {
        let ripple = document.createElement("span");
        ripple.classList.add("ripple");
        this.appendChild(ripple);

        ripple.style.left = `${e.clientX - this.offsetLeft}px`;
        ripple.style.top = `${e.clientY - this.offsetTop}px`;

        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Auto-refresh for machine live-stock pages
if (window.location.pathname.includes("machine_view")) {
    setInterval(() => {
        window.location.reload();
    }, 5000);
}

// Auto-refresh QR page
if (window.location.pathname.includes("qr_access")) {
    setInterval(() => {
        const img = document.querySelector("img");
        if (img) {
            img.src = img.src.split("?")[0] + "?" + new Date().getTime();
        }
    }, 7000);
}


(function () {

    const root = document.documentElement;
    const toggleBtn = document.getElementById("themeToggle");

    const saved = localStorage.getItem("theme");

    if (saved === "light") {
        root.setAttribute("data-theme", "light");
    } else if (saved === "dark") {
        root.setAttribute("data-theme", "dark");
    } else {
        root.removeAttribute("data-theme");
    }

    if (toggleBtn) {
        if (saved === "light") toggleBtn.innerText = "☀️ Light";
        else if (saved === "dark") toggleBtn.innerText = "🌙 Dark";
        else toggleBtn.innerText = "🌓 Auto";
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {

            let current = root.getAttribute("data-theme");

            if (current === "dark") {
                root.setAttribute("data-theme", "light");
                localStorage.setItem("theme", "light");
                toggleBtn.innerText = "☀️ Light";

            } else if (current === "light") {
                root.removeAttribute("data-theme");
                localStorage.removeItem("theme");
                toggleBtn.innerText = "🌓 Auto";

            } else {
                root.setAttribute("data-theme", "dark");
                localStorage.setItem("theme", "dark");
                toggleBtn.innerText = "🌙 Dark";
            }
        });
    }

})();
