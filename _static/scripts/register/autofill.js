const userIdField = document.querySelector("#user_id");

function usernameInput(field) {
    let autofill = String(field.value.toLowerCase().replaceAll(" ", "_"));

    if (autofill.length > 16) {
        let arr = autofill.split("_");
        let output = [];

        output = [...output, arr[0][0] + arr[0][arr[0].length - 1]];
        
        for (let i = 1; i < arr.length; i++) {
            output = [...output, arr[i]];
        }

        autofill = output.join("_");
    }
    userIdField.value = autofill.substring(0, 15);
}
