let filePathInput = document.getElementById("filePathInput");
let encKeyInput = document.getElementById("encKeyInput");
let openButton = document.getElementById("openButton");

function initOpenFunc() {
    filePathInput.addEventListener("input", function(){
        filePathInput.value = filePathInput.value.replace(/[^a-zA-Z0-9_\-.: \/\\]/g, "");
        if (filePathInput.value.trim() === "" && encKeyInput.value.trim() === "") {
            openButton.classList.add("disabled");
        }
        else {
            openButton.classList.remove("disabled");
        }
    });

    encKeyInput.addEventListener("input", function(){
        encKeyInput.value = encKeyInput.value.replace(/[^a-zA-Z0-9_]/g, "");
        if (filePathInput.value.trim() === "" && encKeyInput.value.trim() === "") {
            openButton.classList.add("disabled");
        }
        else {
            openButton.classList.remove("disabled");
        }
    });

    openButton.addEventListener("click", async function(e){
        e.preventDefault();
        let signed = document.getElementById("signedCheck").checked;
        console.log(signed);
        const data = {
            path: filePathInput.value,
            key: encKeyInput.value,
            signed: signed
        };

        try {
            const response = await fetch("/open", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (!response.ok) {throw new Error("Open failed");}
            if (result.valid !== true){
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note couldn't be read.");
                }
                else {
                    alert("Note konnte nicht gelesen werden.")
                }
                return;
            }
            else if (result.valid === true){
                window.location.href = "/edit/open"
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
}

const translations = {
    en: { 
            lang: "en",
            navUser: "User",
            sideHeaderNew: "New Note",
            sideBodyNew: "Create a new SecNote.",
            sideHeaderOpen: "Open Note",
            sideBodyOpen: "Open an existing SecNote.",
            sideHeaderHelp: "Need Help?",
            sideBodyHelp: "View documentation.",
            modalHeaderOpen: "Open Note",
            modalBodyPath: "Path",
            modalBodyKey: "Key",
            modalOpenSigned: "Signed",
            modalFooterClose: "Close",
            modalFooterOpen: "Open"
        }, 
    
    de: {
            lang: "de",
            navUser: "Profil",
            sideHeaderNew: "Neue Note",
            sideBodyNew: "Neue SecNote erstellen.",
            sideHeaderOpen: "Note öffnen",
            sideBodyOpen: "Existierende SecNote öffnen.",
            sideHeaderHelp: "Hilfe?",
            sideBodyHelp: "Zur Dokumentation.",
            modalHeaderOpen: "Note öffnen",
            modalBodyPath: "Pfad",
            modalBodyKey: "Schlüssel",
            modalOpenSigned: "Signiert",
            modalFooterClose: "Abbrechen",
            modalFooterOpen: "Öffnen"
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

async function main() {
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
    initOpenFunc();
}

document.addEventListener("DOMContentLoaded", function() {
    main();
});
