const tableNameSelect = document.querySelector("#tableName");
const sqlCommandField = document.querySelector("#sqlCommand");
const formInput = document.querySelector("#formInput");
const dummyframe = document.querySelector("#dummyframe");
const footer = document.querySelector("footer");
const form = document.querySelector("#form");


function request(url, extra, get_json = false) {
    return new Promise((response, _reject) => {
        return fetch(url, (extra) ? extra : {}).catch(error => alert(error)).then(data => response((get_json) ? data.json() : data.text()));
    });
}


function run(_button) {
    tableNameSelect.value = "null";
    formInput.value = sqlCommandField.value;
    formInput.parentElement.submit();
    window.setTimeout(() => {
        var result = dummyframe.contentWindow.document.body.innerHTML;
        if (!result) window.setTimeout(() => {
            footer.innerHTML = dummyframe.contentWindow.document.body.innerHTML;
        }, 250);
        else footer.innerHTML = result;
    }, 100);
}

function tableSelected() {
    if (tableNameSelect.value === "null") {
        document.querySelector("#onlyWhenTable").style.setProperty("display", "none");
        footer.innerHTML = "";
    } else {
        document.querySelector("#onlyWhenTable").style.removeProperty("display");
        request(`/api/fetch_table/${tableNameSelect.value}`).then(data => footer.innerHTML = data);
    }
}

function appendRow() {
    let row = document.querySelector("tbody").appendChild(document.createElement("tr"));
    let column = row.parentElement.parentElement.firstElementChild.firstElementChild.firstElementChild.innerText;
    if (!column.includes("_")) return alert("Unable to append row unless id is present as the first column.")
    let table = column.split("_")[0].replace(/^\w/, c => c.toUpperCase());
    form.querySelector("#table").value = table;
    form.querySelectorAll(".formTitle").forEach(title => title.innerText = "Append row");

    request(`/api/info/${table}`).then(data => {
        form.querySelector("section").innerHTML = data;
        form.style.removeProperty("display");
    });
}

function editRow(row) {
    let column = row.parentElement.parentElement.parentElement.parentElement.firstElementChild.firstElementChild.firstElementChild.innerText;
    if (!column.includes("_")) return alert("Unable to edit row unless id is present as the first column.")
    let table = column.split("_")[0].replace(/^\w/, c => c.toUpperCase());
    let id = row.parentElement.parentElement.firstElementChild.innerText;
    form.querySelector("#id").value = id;
    form.querySelector("#table").value = table;
    form.querySelectorAll(".formTitle").forEach(title => title.innerText = "Edit row");

    request(`/api/info/${table}`).then(data => {
        form.querySelector("section").innerHTML = data;
        window.setTimeout(() => {
            row.parentElement.parentElement.querySelectorAll(".column").forEach(column => {
                let match = form.querySelector(`#${column.dataset?.column}`);
                if (match) { 
                    if (column.dataset?.column == `${table}_id`.toLocaleLowerCase()) match.disabled = true;
                    match.value = (column.innerText === "[NULL]") ? "" : column.innerText;
                    if (column.dataset?.column === "password") {
                        match.value = "[encrypted]";
                        match.onfocus = function (_) {
                            if (match.value == "[encrypted]") match.value = "";
                        }
                        match.onblur = function (_) {
                            if (match.value == "") match.value = "[encrypted]";
                        }
                    }
                }
            });

            form.style.removeProperty("display");
        }, 100);
    })
}

function deleteRow(row) {
    let column = row.parentElement.parentElement.parentElement.parentElement.firstElementChild.firstElementChild.firstElementChild.innerText;
    if (!column.includes("_")) return alert("Unable to delete row unless id is present as the first column.")
    let table = column.split("_")[0].replace(/^\w/, c => c.toUpperCase());
    let id = row.parentElement.parentElement.firstElementChild.innerText;
    request(`/api/delete/${table}/${column}/${id}`).then(_data => row.parentElement.parentElement.remove());
}

function leaveForm() {
    document.querySelectorAll("temporary").forEach(i => i.remove());
    form.style.setProperty("display", "none");
}

if (location.href.includes("#")) {
    tableNameSelect.value = location.href.split("#")[1];
    tableSelected();
}
