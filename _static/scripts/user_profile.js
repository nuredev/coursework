function showTab(tab = null) {
    document.querySelector("#questions").checked = false;
    document.querySelector("#answers").checked = false;
    document.querySelector("#view_questions").style.setProperty("display", "none");
    document.querySelector("#view_answers").style.setProperty("display", "none");
    if (tab) {
        document.querySelector(`#view_${tab.id}`).style.removeProperty("display");
        tab.checked = true;
    }
}

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

showTab(document.querySelector("#questions"));


function printUser() {
    let screen = window.open("");
    screen.document.open();
    screen.document.write(`<html><body>${document.querySelector(".printable").innerHTML}</body></html>`);
    screen.window.print();
    screen.close();
}
