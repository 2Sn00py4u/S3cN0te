let userUsernameInput = document.getElementById("Username-Input-userp");
let userPasswordInput = document.getElementById("Password-Input-userp");
let userDeleteInput = document.getElementById("userDeleteInput");
let cancelUserdataButton = document.getElementById("cancelUserdataButton");
let editUserdataButton = document.getElementById("editUserdataButton");
let userDeleteButton = document.getElementById("userDeleteButton");

function toggleInputs(userdata){
    userPasswordInput.addEventListener("focusin", function(){
        userPasswordInput.type = "text";
    });
    userPasswordInput.addEventListener("focusout", function(){
        userPasswordInput.type = "password";
    });
    userUsernameInput.addEventListener("input", function(){
        if (userUsernameInput.value.trim() === userdata.username && userPasswordInput.value.trim() === userdata.password){
            cancelUserdataButton.classList.add("disabled");
            editUserdataButton.classList.add("disabled");
            cancelUserdataButton.style.boxShadow = "";
            editUserdataButton.style.boxShadow = "";
        }
        else {
            cancelUserdataButton.classList.remove("disabled");
            editUserdataButton.classList.remove("disabled");
            cancelUserdataButton.style.boxShadow = "0 0 3px #dcebff";
            editUserdataButton.style.boxShadow = "0 0 3px #4596ff";
        }
    });
    userPasswordInput.addEventListener("input", function(){
        if (userUsernameInput.value.trim() === userdata.username && userPasswordInput.value.trim() === userdata.password){
            cancelUserdataButton.classList.add("disabled");
            editUserdataButton.classList.add("disabled");
            cancelUserdataButton.style.boxShadow = "";
            editUserdataButton.style.boxShadow = "";
        }
        else {
            cancelUserdataButton.classList.remove("disabled");
            editUserdataButton.classList.remove("disabled");
            cancelUserdataButton.style.boxShadow = "0 0 3px #dcebff";
            editUserdataButton.style.boxShadow = "0 0 3px #4596ff";
        }
    });
    userDeleteInput.addEventListener("input", function(){
        if (userDeleteInput.value === "SecNote " + userdata.username){
            userDeleteButton.classList.remove("disabled");
        }
        else {
            userDeleteButton.classList.add("disabled");
        }
    });
}

function toggleEdit(userdata){
    editUserdataButton.addEventListener("click", async function(e){
        e.preventDefault();

        const data = {
            new_username: userUsernameInput.value,
            new_password: userPasswordInput.value
        };

        try {
            const response = await fetch("/user/edit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (!response.ok) {throw new Error("Login failed");}

            if (result.valid !== true){
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Username couldn't be registered.");
                }
                else {
                    alert("Benutzername konnte nicht registriert werden.");
                }
                userUsernameInput.value = userdata.username;
                userPasswordInput.value = userdata.password;
                cancelUserdataButton.classList.add("disabled");
                editUserdataButton.classList.add("disabled");
                cancelUserdataButton.style.boxShadow = "";
                editUserdataButton.style.boxShadow = "";
                return;
            }
            else if (result.valid === true){
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Edit successfull! Please login for the changes to have effect.");
                }
                else {
                    alert("Erfolg! Nach dem nächsten Login sind die Änderungen etabliert");
                }
                window.location.href = "/";
            }
            else {
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("An unexpected error occurred.");
                }
                else {
                    alert("Ein Fehler ist aufgetreten.")
                }
                return;
            }
        } catch (err) {
            console.error(err.message);
        }
    });

    cancelUserdataButton.addEventListener("click", function(){
        userUsernameInput.value = userdata.username;
        userPasswordInput.value = userdata.password;
        cancelUserdataButton.classList.add("disabled");
        editUserdataButton.classList.add("disabled");
        cancelUserdataButton.style.boxShadow = "";
        editUserdataButton.style.boxShadow = "";
    });
}

document.addEventListener("DOMContentLoaded", function(){
    let userdata = {
        username: userUsernameInput.value,
        password: userPasswordInput.value
    }
    toggleInputs(userdata);
    toggleEdit(userdata);
});
