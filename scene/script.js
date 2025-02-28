// ตัวแปรสำหรับ path ของไฟล์ YAML
const yamlPath = 'scripts/conversations.yaml';

// ตัวแปรสำหรับจัดการสถานะของบทสนทนา
let currentTextIndex = 0;    // ตำแหน่งข้อความในบทสนทนาปัจจุบัน
let sceneData;               // เก็บข้อมูลบทสนทนาที่โหลดมาจากไฟล์ YAML
let currentSceneIndex = 0;   // ตำแหน่งฉากปัจจุบัน
let currentScene;            // คีย์ของฉากปัจจุบันใน sceneData
let isInstantDisplay = false; // สลับระหว่างการแสดงผลแบบเอฟเฟกต์พิมพ์และแสดงทันที

// โหลดไฟล์เสียงพื้นหลังและตั้งค่าให้เล่นวน
const backgroundAudio = new Audio('sounds/game-music-loop.mp3');

// เมื่อหน้าเว็บโหลดเสร็จ ให้เริ่มต้นการเล่นเสียงและตั้งค่าเริ่มต้น
window.onload = function() {
    currentTextIndex = 0;
    backgroundAudio.loop = true;
    // backgroundAudio.play(); // ยกเลิกคอมเมนต์หากต้องการเล่นเสียง
};

// โหลดข้อมูลบทสนทนาจากไฟล์ YAML
fetch(yamlPath)
    .then(response => response.text())
    .then(yamlString => {
        // แปลงข้อมูลจาก YAML ให้อยู่ในรูปของ Object
        sceneData = jsyaml.load(yamlString)["conversations"];
        console.log(Object.keys(sceneData)[0]);

        // เลือกฉากแรกและแสดงข้อความแรก
        currentScene = Object.keys(sceneData)[currentSceneIndex];
        const firstSceneDialog = sceneData[currentScene].dialog;
        const firstText = firstSceneDialog[currentTextIndex].text;
        const firstSpeaker = firstSceneDialog[currentTextIndex].speaker;
        
        typeWriter(firstText, 'description', 50);
        changeSpeakerImage(firstSpeaker);

    })
    .catch(error => console.error('Error loading YAML file:', error));

// ฟังก์ชันสำหรับเปลี่ยนข้อความในบทสนทนาเมื่อมีการคลิกปุ่ม
function changeDialog() {
    // ตรวจสอบว่ามีข้อความถัดไปในบทสนทนาของฉากปัจจุบันหรือไม่
    if (sceneData[currentScene].dialog.length !== (currentTextIndex + 1)) {
        currentTextIndex++;
        isInstantDisplay = !isInstantDisplay; // สลับสถานะการแสดงผล

        const currentSceneDialog = sceneData[currentScene].dialog[currentTextIndex];
        const nextText = currentSceneDialog.text;
        const nextSpeaker = currentSceneDialog.speaker;

        if (isInstantDisplay) {
            displayTextImmediately(nextText);
            if (nextSpeaker) {
                changeSpeakerImage(nextSpeaker);
            }
        } else {
            typeWriter(nextText, 'description', 50);
            if (nextSpeaker){
                changeSpeakerImage(nextSpeaker);
            }
        }
    } else {
        console.log('End of the scene');
        // ถ้ามีฉากถัดไป ให้เปลี่ยนไปฉากใหม่
        if (Object.keys(sceneData).length !== (currentSceneIndex + 1)) {
            isInstantDisplay = !isInstantDisplay;
            currentSceneIndex++;
            currentScene = Object.keys(sceneData)[currentSceneIndex];
            currentTextIndex = 0;

            const currentSceneDialog = sceneData[currentScene].dialog[currentTextIndex];
            const firstText = currentSceneDialog.text;
            const firstSpeaker = currentSceneDialog.speaker;
            typeWriter(firstText, 'description', 50);

            if (firstSpeaker){
                changeSpeakerImage(firstSpeaker);
            }
            
        }
    }
}

// ฟังก์ชันสำหรับแสดงข้อความทันที (ไม่ใช้เอฟเฟกต์พิมพ์)
function displayTextImmediately(newText) {
    document.getElementById('description').textContent = newText;
}

// ฟังก์ชันสำหรับแสดงข้อความแบบเอฟเฟกต์พิมพ์ (typewriter effect)
function typeWriter(text, elementId, speed = 50) {
    console.log(text);
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
    
    filpImage(speakerElement);
    fadeInImage(speakerElement, 1500);

}

// ฟังก์ชันสำหรับพลิกภาพ (flip image) ของตัวละคร
function filpImage(speakerElement) {
    // ถ้าตำแหน่งข้อความเป็นเลขคี่ ให้พลิกภาพไปทางซ้าย
    if (currentTextIndex % 2 == 1) {
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
function fadeInImage(element, duration = 1000) {
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