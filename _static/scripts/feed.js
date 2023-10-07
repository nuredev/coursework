function fetchAPI(url) {
    return new Promise((response, reject) => {
        return fetch(url).catch(error => alert(error)).then(data => response(data.text()));
    });
}

function addNewCategoryCall() {
    fetchAPI("/api/fetch_format/category").then(data => addNewCategory(data));
}

function addNewCategory(data) {
    document.body.innerHTML += `
    <section id="dialogForm">
        <form action="/api/append/category" method="post">
            ${data}
            <div>
                <span class="space"></span>
                <a class="button red single" href="/">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="eyecons">
                        <path d="m12.293 13.707c0.39174 0.39174 1.0223 0.39174 1.4141 0s0.39174-1.0223 0-1.4141l-4.293-4.293 4.293-4.293c0.39174-0.39174 0.39174-1.0223 0-1.4141-0.39174-0.39174-1.0223-0.39174-1.4141 0l-4.293 4.293-4.293-4.293c-0.39174-0.39174-1.0223-0.39174-1.4141 0s-0.39174 1.0223 0 1.4141l4.293 4.293-4.293 4.293c-0.39174 0.39174-0.39174 1.0223 0 1.4141 0.39174 0.39174 1.0223 0.39174 1.4141 0l4.293-4.293z" />
                    </svg>
                </a>
                <button class="button green" type="submit">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor" class="eyecons">
                        <path d="m13 3.5a1 1 0 0 0-0.70703 0.29297l-6.293 6.293-2.293-2.293a1 1 0 0 0-1.4141 0 1 1 0 0 0 0 1.4141l3.707 3.707 7.707-7.707a1 1 0 0 0 0-1.4141 1 1 0 0 0-0.70703-0.29297z" />
                    </svg>
                    <span>Save</span>
                </button>
            </div>
        </form>
    </section>
    `;
}
