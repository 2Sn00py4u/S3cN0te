
const translations = {
    en: {   
            navRegister: "Register",
            navUser: "User",
            lang: "en",
            registerHeader: "Create an account",
            UsernameLabel: "Username",
            PasswordLabel: "Password",
            loginRegisterSwitch: "You don't have an account yet?",
            registerLoginSwitch: "You already have an account?",
            userWelcomeHeader: "Welcome back!",
            userSecondHeader: "Keep control of your data 🔒",
            userUserdataHeader: "Userdata",
            userUsernameLabel: "Username",
            userPasswordLabel: "Password",
            userUserdataCancel: "Cancel",
            userUserdataSave: "Save",
            userDangerzoneHeader: "Dangerzone",
            userDangerzoneDelete: "Delete"
        }, 
    
    de: {
            navRegister: "Registrieren",
            navUser: "Profil",
            lang: "de",
            registerHeader: "Account erstellen",
            UsernameLabel: "Benutzername",
            PasswordLabel: "Passwort",
            loginRegisterSwitch: "Sie haben noch keinen Account?",
            registerLoginSwitch: "Sie haben bereits einen Account?",
            userWelcomeHeader: "Willkommen zurück!",
            userSecondHeader: "Behalten Sie die Kontrolle über Ihre Daten 🔒",
            userUserdataHeader: "Benutzerdaten",
            userUsernameLabel: "Benutzername",
            userPasswordLabel: "Passwort",
            userUserdataCancel: "Abbrechen",
            userUserdataSave: "Speichern",
            userDangerzoneHeader: "Gefahrenzone",
            userDangerzoneDelete: "Löschen"
        }
}

let langSwitch = document.getElementById("langSwitch")

function setLanguage(lang) { 
    document.querySelectorAll("[data-i18n]").forEach(el => { 
        const key = el.getAttribute("data-i18n"); 
        el.textContent = translations[lang][key]; 
    }); 
    localStorage.setItem("language", lang); 
} 

function main() {
    const savedLang = localStorage.getItem("language") || "de"; 
    setLanguage(savedLang);
    langSwitch.addEventListener("click", function() {
        const savedLang = localStorage.getItem("language");
        if (savedLang == "de") {
            setLanguage("en");
        }
        else {
            setLanguage("de");
        }
    });
}

document.addEventListener("DOMContentLoaded", function() { 
    main();
});