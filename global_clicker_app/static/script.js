(() => {
    const clicker = document.getElementById("clicker");
    const clickCount = document.getElementById("clickCount");

    let clickToken = clicker.dataset.clickToken;
    clicker.removeAttribute("data-click-token");

    function getCsrfToken() {
        const input = document.querySelector("input[name='csrfmiddlewaretoken']");
        return input ? input.value : "";
    }

    async function handleClick(event) {
        if (!event.isTrusted) {
            return;
        }

        try {
            const response = await fetch(clicker.dataset.clickUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Click-Token": clickToken,
                },
            });

            if (response.status === 403) {
                window.location.reload();
                return;
            }

            const data = await response.json();
            if (data.token) {
                clickToken = data.token;
            }
            if (data.clicks !== undefined) {
                clickCount.textContent = data.clicks;
            }
        } catch (error) {
            console.error("click failed", error);
        }
    }

    clicker.addEventListener("click", handleClick);
})();
