async function downloadComic(comicId) {
    const buttons = document.querySelectorAll("button");
    const original = [];

    buttons.forEach((button) => {
        original.push([button, button.textContent]);
        button.disabled = true;
        button.textContent = "Exporting...";
    });

    try {
        const response = await fetch(`/export/${encodeURIComponent(comicId)}`);

        if (!response.ok) {
            let message = "PDF export failed.";
            try {
                const data = await response.json();
                message = data.detail || message;
            } catch (_) {}
            throw new Error(message);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = `comiccraft-${comicId}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);
        window.location.href =
            `/export-success?comic_id=${encodeURIComponent(comicId)}`;
    } catch (error) {
        alert(error.message || "PDF export failed.");
        original.forEach(([button, text]) => {
            button.disabled = false;
            button.textContent = text;
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("comicForm");
    const button = document.getElementById("createButton");

    if (form && button) {
        form.addEventListener("submit", () => {
            button.disabled = true;
            button.textContent = "Creating Comic...";
        });
    }
});
