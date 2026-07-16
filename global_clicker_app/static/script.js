const clicker = document.getElementById("clicker");
const clickCount = document.getElementById("clickCount");

function getCsrfToken() {
    const input = document.querySelector("input[name='csrfmiddlewaretoken']");
    return input ? input.value : "";
}

async function handleClick(event) {
    try {
        const response = await fetch(clicker.dataset.clickUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();
        clickCount.textContent = data.clicks;
    } catch (error) {
        console.error("click failed", error);
    }
}
