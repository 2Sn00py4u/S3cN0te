document.getElementById("registerForm").addEventListener("submit", async function(e){
    e.preventDefault();

    const data = {
        username: document.getElementById("register_unameInput").value,
        password: document.getElementById("register_passwdInput").value
    };
    
    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (!response.ok) {throw new Error("Registration failed");}

        if (result.valid !== true){
            const lang = localStorage.getItem("language");
            if (lang == "en"){
                alert("Username couldn't be registered.");
            }
            else {
                alert("Benutzername konnte nicht registriert werden.");
            }
            return;
        }
        else if (result.valid === true){
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

