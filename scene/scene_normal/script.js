let currentIndex = 0;
let dialogData = [];
let scenes;
let dialogs;
let idx = 0;
let skip = false;
let idx_scene = 0;
let sceneCurrent;

window.onload = function () {
    fetch("scripts/scene_scripts.yaml")
        .then((response) => response.text())
        .then((yamlString) => {
            scenes = jsyaml.load(yamlString);

            const keys = Object.keys(scenes);
            sceneCurrent = scenes[keys[idx_scene]];
            dialogs = sceneCurrent.dialog;
            start();
        });
};

function start() {
    function textDialog() {
        const element_disc = document.getElementById("description");
        const textSart = dialogs[idx].text;
        let textNumber = 0;


        if (element_disc){
            element_disc.textContent = "";
            function typingtext() {
                if (textNumber < textSart.length) {
                    element_disc.textContent += textSart.charAt(textNumber);
                    textNumber++;
                    setTimeout(typingtext, 50);
                }
            }
            typingtext();
        } else {
            console.log("ไม่พบ element ที่มี id 'description'");
        }
    }

    function updateSpeaker(image) {
        if (dialogs[idx].hasOwnProperty("speaker")) {
            const imagePath = `images/${image}.png`;
            const speakerElement = document.getElementById("speaker");
            if (speakerElement) {
                speakerElement.src = imagePath;
            } else {
                console.log("ไม่พบ element ที่มี id 'speaker'");
            }

            moveSpeaker(speakerElement, 0, 0.8, 63);
        } else {
            const speakerElement = document.getElementById("speaker");
            speakerElement.src = "";
            speakerElement.style.display = "none";
        }
    }

    setTimeout(() => {
        const buttonNext = document.getElementById("buttonNext");
        if (buttonNext) {
            buttonNext.style.display = "block";
        } else {
            console.log("ไม่พบ element ที่มี id 'buttonNext'");
        }
    }, 5000);
    checkTypeScene();
    textDialog();
    updateSpeaker(dialogs[idx].speaker);
}

const buttonSkip = document.getElementById("buttonSkip");
const buttonNext = document.getElementById("buttonNext");

if (buttonSkip && buttonNext) {
    buttonSkip.addEventListener("click", btnSkip);
    buttonNext.addEventListener("click", btnNext);
} else {
    console.log("ไม่พบปุ่มที่มี id 'buttonSkip' หรือ 'buttonNext'");
}

function btnSkip() {
    toggleButtonDisplay("buttonSkip", "buttonNext");
    console.log(skip);
    skip = !skip;
}

function btnNext() {
    toggleButtonDisplay("buttonNext", "buttonSkip");
    manageScene();
    changeText(dialogs[idx].text, "description");
    updateSpeakerImage(dialogs[idx].speaker);
}

function manageScene() {
    if (idx < dialogs.length - 1) {
        idx++;
    } else {
        if (sceneCurrent.hasOwnProperty("next_scene")) {
            sceneCurrent = scenes[sceneCurrent.next_scene];
            idx = 0;
            dialogs = sceneCurrent.dialog;
        }
    }
}

function checkTypeScene() {
    if (sceneCurrent.hasOwnProperty("type")) {
        if (sceneCurrent.type === "game") {
            console.log("game");
        } else if (sceneCurrent.type === "dialog") {
            console.log("dialog");
        } else if (sceneCurrent.type === "choice"){
            console.log("choice");
        }
    }
}






function toggleButtonDisplay(buttonId1, buttonId2) {
    const button1 = document.getElementById(buttonId1);
    const button2 = document.getElementById(buttonId2);

    button1.style.visibility = "hidden";
    button2.style.visibility = "hidden";

    setTimeout(() => {
        button1.style.visibility = "visible";
        button2.style.visibility = "visible";
    }, 500);

    if (button1.style.display === "none") {
        button1.style.display = "block";
        button2.style.display = "none";
    } else {
        button1.style.display = "none";
        button2.style.display = "block";
    }
}

function changeText(text, id) {
    let textNumber = 0;
    const element = document.getElementById(id);
    element.textContent = "";

    function typingtext() {
        if (skip) {
            element.textContent = text;
            skip = !skip;
            return;
        } else {
            if (textNumber < text.length) {
                element.textContent += text.charAt(textNumber);
                textNumber++;
                setTimeout(typingtext, 50);
            } else {
                console.log("end fade ......");
                resetText();
            }
        }
    }
    typingtext();
}

function resetText() {
    function toggleButtonDisplay() {
        const button1 = document.getElementById("buttonNext");
        const button2 = document.getElementById("buttonSkip");

        if (button1.style.display === "none") {
            button1.style.display = "block";
            button2.style.display = "none";
        } else {
            button1.style.display = "none";
            button2.style.display = "block";
        }
    }
    toggleButtonDisplay();
    changeText(dialogs[idx].text, "description");
    skip = !skip;
}

function updateSpeakerImage(newSrc) {
    const imagePath = `images/${newSrc}.png`;
    const speakerElement = document.getElementById("speaker");
    filpImage(speakerElement, idx);
    speakerElement.src = imagePath;
    fadeInImage(speakerElement);
}

function moveSpeaker(id, start = 10, speed = 0.5, limit = 63) {
    const speakerImg = id;
    if (!speakerImg) {
        console.log("ไม่พบ element ที่มี id 'speaker'");
        return;
    }

    let left = start;
    speakerImg.style.left = left + "%";
    fadeInImage(speakerImg);

    // หน่วงเวลา 3 วินาทีก่อนเริ่มแอนิเมชัน
    setTimeout(() => {
        function animate() {
            if (left < limit) { // ตรวจสอบให้แน่ใจว่า left ไม่เกิน 3%
                left += speed; // เพิ่มค่า left ทีละ 0.5%
                speakerImg.style.left = left + "%";
                requestAnimationFrame(animate); // เรียก animate ใน frame ถัดไป
            }
        }
        animate();
    }, 3000);
}

function fadeInImage(element, duration = 1000) {
    element.style.opacity = 0;
    element.style.display = "block";

    let opacity = 0;
    const interval = 50;
    const increment = interval / duration;

    function fade() {
        opacity += increment;
        if (opacity <= 1) {
            element.style.opacity = opacity;
            setTimeout(fade, interval);
        } else {
            element.style.opacity = 1;
        }
    }
    fade();
}

function filpImage(speakerElement, idx) {
    // ถ้าตำแหน่งข้อความเป็นเลขคี่ ให้พลิกภาพไปทางซ้าย
    if (idx % 2 == 1) {
        speakerElement.style.transform = "scaleX(-1)";
        speakerElement.style.left = "3%";
        console.log("flip left");
    } else {
        // ถ้าตำแหน่งข้อความเป็นเลขคู่ ให้พลิกภาพไปทางขวา
        speakerElement.style.transform = "scaleX(1)";
        speakerElement.style.left = "auto";
        speakerElement.style.right = "3%";
        console.log("flip right");
    }
}

function choicePage(){
    const buttonChoice = document.getElementById("button_choice");
    for (let i = 1; i <= 5; i++) {
        const button = document.createElement("button");
        button.textContent = `Choice ${i}`;
        button.id = `choice${i}`;
        buttonChoice.appendChild(button);
    }
}