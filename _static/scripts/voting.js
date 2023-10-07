function request(url, extra, get_json = false) {
    return new Promise((response, _reject) => {
        return fetch(url, (extra) ? extra : {}).catch(error => alert(error)).then(data => response((get_json) ? data.json() : data.text()));
    });
}

function vote(button) {
    request(`/api/vote/${button.dataset.target}`).then(data => {
        location.reload();
    });
}

function printQuestion() {
    let screen = window.open("");
    screen.document.open();
    screen.document.write(`<html><body>${document.querySelector(".printable").innerHTML}</body></html>`);
    screen.window.print();
    screen.close();
}
