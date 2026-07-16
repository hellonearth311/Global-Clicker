const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
clickForm = document.getElementById("clickForm");

function handleClick(event) {
    console.log("clicked");
    clickForm.requestSubmit();
    sleep(100);
}