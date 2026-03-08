let pageContainer = document.getElementById("page-frame");
let pageTemplate = document.getElementById("page-template").innerHTML;
let pages_list = []; // [{"id": 0-n, "markdown": "...\n", "html": "</>"}]
let addButton = document.getElementById("add-page-btn");
let removeButton = document.getElementById("remove-page-btn");
let undoButton = document.getElementById("undo-btn");
let redoButton = document.getElementById("redo-btn");
let saveButton = document.getElementById("saveButton");
let fileNameInput = document.getElementById("fileNameInput");
let encKeyInput = document.getElementById("encKeyInput");
let convertImgBtn = document.getElementById("convert-img-btn");
let convertPDFbtn = document.getElementById("convert-pdf-btn");
let loader = document.getElementById("loader");
let undoStack = [];
let redoStack = [];

function saveSnapshot() {
    if (undoStack.length >= 20){
        undoStack.pop();
    }
    undoStack.push(JSON.parse(JSON.stringify(pages_list)));
}

async function getSecNote() {
    try {
        const response = await fetch(window.location.pathname, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ req: "edit?" })
        });

        if (!response.ok) {
            throw new Error("New File failed!");
        }

        const result = await response.json();
        return result;

    } catch (err) {
        console.error(err.message);
    }
}

function renderPages(page_list) {
    pageContainer.innerHTML = "";
    pages_list = [];
    for (let i = 0; i < page_list.length; i++){
        let page_data = {
            page_id: page_list[i].id,
        }
        pages_list.push({id: page_data.page_id, markdown: page_list[i].markdown, html: DOMPurify.sanitize(marked.parse(page_list[i].markdown))})
        pageContainer.insertAdjacentHTML('beforeend', Mustache.render(pageTemplate, page_data));
        let page = document.getElementById("page-" + page_data.page_id);
        page.innerHTML = pages_list[i].html;
        page.addEventListener("focusin", function(){
            page.style.backgroundColor = "#06030f";
            page.textContent = pages_list[i].markdown;
            document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
            page.classList.add('selected');
        });
        page.addEventListener("focusout", function(){
            page.style.backgroundColor = "#212529";
            pages_list[i].markdown = page.innerText.replace(/\r/g, '').replace(/\n{3,}/g, '\n');
            let html = DOMPurify.sanitize(marked.parse(pages_list[i].markdown));
            pages_list[i].html = html;
            page.innerHTML = html;
            saveSnapshot();
        });
    };
}

function sortListIDs(l, index) {
    let list = l
    list.splice(index, 1);
    for (let i = 0; i < list.length; i++){
        list[i].id = i.toString();
    }
    return list
} 

function initEditbuttons() {
    addButton.addEventListener("click", function() {
        let new_list = pages_list;
        let index = new_list.length;
        let id = index.toString();
        new_list.push({id: id, markdown: "", html: DOMPurify.sanitize(marked.parse(""))});
        renderPages(new_list);
    });

    removeButton.addEventListener("click", function() {
        let selected = document.getElementsByClassName("selected");
        let new_list = pages_list;
        let index = new_list.length - 1;
        for (let element of selected){
            index = Number(element.id.replace(/^page-/, "")); 
        }
        new_list = sortListIDs(new_list, index);
        renderPages(new_list);
    });

    undoButton.addEventListener("click", function() {
        if (undoStack.length > 1) {
            redoStack.push(undoStack.pop());
            let new_list = undoStack[undoStack.length -1];
            renderPages(new_list);
        }       
    });

    redoButton.addEventListener("click", function() {
        if (redoStack.length > 0) {
            let new_list = redoStack.pop();
            undoStack.push(new_list);
            renderPages(new_list);
        }      
    });
    convertImgBtn.addEventListener("click", async function (e){
        e.preventDefault();
        loader.innerHTML = '<div class="loader"></div>';
        let selected = document.getElementsByClassName("selected")[0];
        const data = {
            format: ".png",
            content: selected.innerHTML
        };
        try {
            const response = await fetch("/edit/convert", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (!response.ok) {throw new Error("Save failed");}
            if (result.valid !== true){
                loader.innerHTML = '';
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note couldn't be converted.");
                }
                else {
                    alert("Note konnte nicht konvertiert werden.")
                }
                return;
            }
            else if (result.valid === true){
                loader.innerHTML = '';
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note has successfully been saved at '" + result.path + "'.");
                }
                else {
                    alert("Note wurde erfolgreich gespeichert unter '" + result.path + "'.");
                }
                return
            }
            else {
                loader.innerHTML = '';
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("An unexpected error occurred.");
                }
                else {
                    alert("Ein Fehler ist aufgetreten.");
                }
                return;
            }
        } catch (err) {
            loader.innerHTML = '';
            console.error(err.message);
        }
    });

    convertPDFbtn.addEventListener("click", async function (e){
        loader.innerHTML = '<div class="loader"></div>';
        e.preventDefault();

        const data = {
            format: ".pdf",
            pages_list: pages_list
        };
        try {
            const response = await fetch("/edit/convert", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (!response.ok) {throw new Error("Save failed");}

            if (result.valid !== true){
                loader.innerHTML = '';
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note couldn't be converted.");
                }
                else {
                    alert("Note konnte nicht konvertiert werden.")
                }
                return;
            }
            else if (result.valid === true){
                loader.innerHTML = '';
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note has successfully been saved at '" + result.path + "'.");
                }
                else {
                    alert("Note wurde erfolgreich gespeichert unter '" + result.path + "'.");
                }
                return
            }
            else {
                loader.innerHTML = '';
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("An unexpected error occurred.");
                }
                else {
                    alert("Ein Fehler ist aufgetreten.");
                }
                return;
            }
        } catch (err) {
            loader.innerHTML = '';
            console.error(err.message);
        }
    });
}

function initSaveFunc() {
    fileNameInput.addEventListener("input", function(){
        fileNameInput.value = fileNameInput.value.replace(/[^a-zA-Z0-9_-]/g, "");
        if (fileNameInput.value.trim() === "" && encKeyInput.value.trim() === "") {
            saveButton.classList.add("disabled");
        }
        else {
            saveButton.classList.remove("disabled");
        }
    });

    encKeyInput.addEventListener("input", function(){
        encKeyInput.value = encKeyInput.value.replace(/[^a-zA-Z0-9_]/g, "");
        if (fileNameInput.value.trim() === "" && encKeyInput.value.trim() === "") {
            saveButton.classList.add("disabled");
        }
        else {
            saveButton.classList.remove("disabled");
        }
    });

    saveButton.addEventListener("click", async function(e){
        e.preventDefault();
        let signed = document.getElementById("signedCheck").checked;
        console.log(signed);
        const data = {
            name: fileNameInput.value,
            key: encKeyInput.value,
            pages_list: pages_list,
            signed: signed
        };

        try {
            const response = await fetch("/edit/save", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (!response.ok) {throw new Error("Save failed");}

            if (result.valid !== true){
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note couldn't be saved.");
                }
                else {
                    alert("Note konnte nicht gespeichert werden.")
                }
                return;
            }
            else if (result.valid === true){
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("Note has successfully been saved at '" + result.path + "'.");
                }
                else {
                    alert("Note wurde erfolgreich gespeichert unter '" + result.path + "'.");
                }
                return
            }
            else {
                const lang = localStorage.getItem("language");
                if (lang == "en"){
                    alert("An unexpected error occurred.");
                }
                else {
                    alert("Ein Fehler ist aufgetreten.");
                }
                return;
            }
        } catch (err) {
            console.error(err.message);
        }
    });
}

async function main() {
    const result = await getSecNote();
    renderPages(result.pages);
    saveSnapshot();
    initEditbuttons();
    initSaveFunc();
    document.getElementById("page-0").classList.add("selected");
}

const translations = {
    en: { 
            lang: "en",
            navUser: "User",
            sideSaveHeader: "Save Note",
            sideSaveBody: "Save this SecNote.",
            sidePDFHeader: "Save .PDF",
            sidePDFBody: "Save this SecNote as PDF.",
            sidePNGHeader: "Save .PNG",
            sidePNGBody: "Save selected page as PNG.",
            sideHelpHeader: "Need Help?",
            sideHelpBody: "View help documentation.",
            modalSaveHeader: "Save Note",
            modalSaveKey: "Key",
            modalSaveSigned: "Signed",
            modalSaveCancel: "Cancel",
            modalSaveSave: "Save"
        }, 
    
    de: {
            lang: "de",
            navUser: "Profil",
            sideSaveHeader: "Note speichern",
            sideSaveBody: "Diese SecNote speichern.",
            sidePDFHeader: "Speichern .PDF",
            sidePDFBody: "Diese SecNote als PDF speichern.",
            sidePNGHeader: "Speichern .PNG",
            sidePNGBody: "Ausgewählte Seite als PNG speichern.",
            sideHelpHeader: "Hilfe?",
            sideHelpBody: "Zur Dokumentation.",
            modalSaveHeader: "Note speichern",
            modalSaveKey: "Schlüssel",
            modalSaveSigned: "Signiert",
            modalSaveCancel: "Abbrechen",
            modalSaveSave: "Speichern"
            
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

document.addEventListener("DOMContentLoaded", function() {
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
    main();
    window.addEventListener("beforeunload", (event) => {
        event.preventDefault();
        event.returnValue = "";
    });
});