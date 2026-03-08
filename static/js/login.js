document.getElementById("loginForm").addEventListener("submit", async function(e){
    e.preventDefault();

    const data = {
        username: document.getElementById("login_unameInput").value,
        password: document.getElementById("login_passwdInput").value
    };

    try {
        const response = await fetch("/login", {
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
                alert("Invalid credentials.");
            }
            else {
                alert("Falsche Benutzerdaten.")
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

