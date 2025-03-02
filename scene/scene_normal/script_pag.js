let currentIndex = 0;
let dialogData = [];
let scenes;
let dialogs;
let idx = 0;
let skip = false;
let idx_scene = 0;
let sceneCurrent;


document.addEventListener("DOMContentLoaded", async function () {
    await fetch("scripts/scene_scripts.yaml")
        .then((response) => response.text())
        .then((yamlString) => {
            scenes = jsyaml.load(yamlString);
            const keys = Object.keys(scenes);
            sceneCurrent = scenes[keys[idx_scene]];
        });
    checkTypeScene();
});


function checkTypeScene() {
    const keys = Object.keys(scenes);
    sceneCurrent = scenes[keys[idx_scene]];

    if (sceneCurrent.hasOwnProperty("type")) {
        if (sceneCurrent.type === "game") {
            console.log("ahead to game");
        } else if (sceneCurrent.type === "dialog") {
            console.log("ahead to dialog");
            createDialogPage();
        } else if (sceneCurrent.type === "choice") {
            console.log("ahead to choice");
            createChoicePage();
        }
    }
}

function createDialogPage() {
    document.body.innerHTML = '';

    const background = document.createElement("div");
    background.className = "background";
    document.body.appendChild(background);

    const speaker = document.createElement("img");
    speaker.className = "speaker";
    speaker.id = "speaker";
    document.body.appendChild(speaker);

    const panel = document.createElement("div");
    panel.className = "panel";
    document.body.appendChild(panel);

    const description = document.createElement("p");
    description.id = "description";
    panel.appendChild(description);

    const buttonNext = document.createElement("button");
    buttonNext.id = "buttonNext";
    buttonNext.className = "button";
    buttonNext.style.display = "none";
    buttonNext.textContent = "ต่อไป >>";
    panel.appendChild(buttonNext);

    const buttonSkip = document.createElement("button");
    buttonSkip.id = "buttonSkip";
    buttonSkip.className = "button";
    buttonSkip.style.display = "none";
    buttonSkip.textContent = "ข้าม >>";
    panel.appendChild(buttonSkip);

    const buttonChoice = document.createElement("button");
    buttonChoice.id = "buttonChoice";
    buttonChoice.className = "button";
    buttonChoice.textContent = "เลือก >>";
    buttonChoice.onclick = function () {
        idx_scene++;
        seneTrasition();
    }; // ต้องเปลี่ยนเป็นเรียกฟังก์ชันที่สร้างหน้าเลือก
    document.body.appendChild(buttonChoice);

    fadeOut();
}

function createChoicePage() {
    document.body.innerHTML = '';

    const background = document.createElement("div");
    background.className = "background";
    document.body.insertBefore(background, document.body.firstChild);

    const buttonChoice = document.createElement("div");
    buttonChoice.id = "button_choice";
    document.body.appendChild(buttonChoice);

    for (let i = 1; i <= 5; i++) {
        const button = document.createElement("button");
        button.textContent = `Choice ${i}`;
        button.id = `choice${i}`;
        buttonChoice.appendChild(button);
    }

    const panel = document.createElement("div");
    panel.className = "panel";
    document.body.appendChild(panel);

    const description = document.createElement("p");
    description.id = "description";
    panel.appendChild(description);

    fadeOut();

    console.log("createChoicePage");

}

function fadeInImage(duration = 1000) {
    const transition = document.createElement("div");
    transition.className = "transition";
    document.body.appendChild(transition);
    transition.style.opacity = 0;
    transition.style.display = "block";

    let opacity = 0;
    const interval = 50;
    const increment = interval / duration;

    function fade() {
        opacity += increment;
        if (opacity <= 1) {
            transition.style.opacity = opacity;
            setTimeout(fade, interval);
        } else {
            transition.style.opacity = 1;
        }

    }
    fade();
    console.log("fadeInImage");

}

function seneTrasition(duration = 1000) {
    fadeInImage(duration);
    setTimeout(checkTypeScene, duration);
}

function fadeOut() {
    const fadeOut = document.createElement("div");
    fadeOut.className = "fadeOut";
    document.body.appendChild(fadeOut);

}
