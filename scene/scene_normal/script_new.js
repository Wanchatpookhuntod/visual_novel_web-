const yamlPath = 'scripts/scene_scripts.yaml';
let scenes;
let currentSceneIndex = 0;
let keyCurrentScene;
let currentDialogIndex = 0;
let isInstantDisplay = false; 
let currentScene;


fetch(yamlPath)
    .then(response => response.text())
    .then(yamlString => {
    scenes = jsyaml.load(yamlString);
    keyCurrentScene = Object.keys(scenes)[currentSceneIndex];
    const firstScene = scenes[keyCurrentScene];
    const dialog = firstScene["dialog"];

    typeWriter(dialog[currentDialogIndex].text);
    changeSpeakerImage(dialog[currentDialogIndex].speaker);

    });

function changeDialog() {
    currentScene = scenes[keyCurrentScene]
    const dialog = currentScene["dialog"];
    
    if (currentDialogIndex < dialog.length - 1) {
        currentDialogIndex++;
        isInstantDisplay = !isInstantDisplay;
        typeWriter(dialog[currentDialogIndex].text);
        changeSpeakerImage(dialog[currentDialogIndex].speaker);
        
    } else {
        console.log('End of the scene');
        
        if (scenes[keyCurrentScene].hasOwnProperty('next_scene')) {
            const nextSceneKey = scenes[keyCurrentScene].next_scene;
            if (scenes.hasOwnProperty(nextSceneKey)) {
                keyCurrentScene = nextSceneKey;
                currentDialogIndex = 0;
                currentScene = scenes[keyCurrentScene];
                console.log(currentScene);
                
                const firstScene = scenes[keyCurrentScene];
                const dialog = firstScene["dialog"];
                typeWriter(dialog[currentDialogIndex].text);
                changeSpeakerImage(dialog[currentDialogIndex].speaker);
                
            return;
            }
        }
    }
}

function typeWriter(text,elementId = 'description', speed = 50, ) {
    console.log(text);
    console.log(isInstantDisplay);
    let i = 0;
    const element = document.getElementById(elementId);
    element.textContent = ''; // ล้างข้อความเก่า
    // ฟังก์ชันภายในสำหรับพิมพ์ทีละตัวอักษร
    function type() {
        if (!isInstantDisplay) {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                // เมื่อพิมพ์ครบทุกตัวแล้ว ให้สลับสถานะ
                isInstantDisplay = !isInstantDisplay;
            }
        } else {
            // ถ้าสถานะเป็นแสดงทันที ให้แสดงข้อความทั้งหมดทันที
            element.textContent = text;
        }
    }
    type();
}

function changeSpeakerImage(newSrc) {
    const imagePath = `images/${newSrc}.png`;
    const speakerElement = document.getElementById('speaker');
    speakerElement.src = imagePath;

    // ฟังก์ชันสำหรับพลิกภาพ (flip image) ของตัวละคร
    function filpImage(speakerElement) {
        // ถ้าตำแหน่งข้อความเป็นเลขคี่ ให้พลิกภาพไปทางซ้าย
        if (currentDialogIndex % 2 == 1) {
            speakerElement.style.transform = "scaleX(-1)";
            speakerElement.style.left = "3%";
        } else {
            // ถ้าตำแหน่งข้อความเป็นเลขคู่ ให้พลิกภาพไปทางขวา
            speakerElement.style.transform = "scaleX(1)";
            speakerElement.style.left = "auto";
            speakerElement.style.right = "3%";
        }
    }

    // ฟังก์ชันสำหรับทำให้ภาพค่อยๆ ปรากฏขึ้น (fade in)
    function fadeInImage(element, duration = 1500) {
        element.style.opacity = 0;
        element.style.display = 'block';

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

    filpImage(speakerElement);
    fadeInImage(speakerElement);
}