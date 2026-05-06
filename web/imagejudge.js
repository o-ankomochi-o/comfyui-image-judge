import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ImageJudge.OpenUI",
    async setup() {
        const btn = document.createElement("button");
        btn.textContent = "Image Judge";
        btn.title = "Open Image Judge UI in a new tab";
        btn.style.cssText = [
            "position: fixed",
            "right: 12px",
            "bottom: 12px",
            "z-index: 9999",
            "padding: 8px 14px",
            "background: #2d6e2d",
            "color: #fff",
            "border: 1px solid #4a9a4a",
            "border-radius: 4px",
            "cursor: pointer",
            "font-family: system-ui, sans-serif",
            "font-size: 13px",
            "box-shadow: 0 2px 6px rgba(0,0,0,0.4)",
        ].join(";");
        btn.addEventListener("mouseenter", () => { btn.style.filter = "brightness(1.15)"; });
        btn.addEventListener("mouseleave", () => { btn.style.filter = ""; });
        btn.addEventListener("click", () => {
            window.open("/imagejudge/ui", "_blank");
        });
        document.body.appendChild(btn);
    },
});
