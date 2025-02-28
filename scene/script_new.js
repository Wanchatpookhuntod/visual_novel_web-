
// const yamlPath = 'scripts/demo_yaml.yaml';
let sceneData;

async function loadYAML(yamlPath) {
    try {
        const response = await fetch(yamlPath);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const yamlString = await response.text();
        const sceneData = jsyaml.load(yamlString); // แปลง YAML เป็น JSON

        console.log(" Loaded YAML data:", sceneData);
        return sceneData; // ส่งค่ากลับเพื่อใช้ต่อ
    } catch (error) {
        console.error(" Failed to load YAML:", error);
        return null; // กรณีโหลดไม่สำเร็จ ให้คืนค่า null
    }
}

(async () => {
    const yamlPath = "scripts/scene_scripts.yaml";
    sceneData = await loadYAML(yamlPath);
    manageSceneData(sceneData);
})();




function print(text){
    console.log(text);
}


let currentSceneIndex = 0;
let sceneStart;
let scenes;
let dialogIndex = 0
function manageSceneData(sceneData){
    sceneStart = sceneData[createSceneStart(sceneData)];
    scenes = sceneData;
    
}

let currentScene;
let sceneIndex = 0;
function changeDialog() {

    console.log(scenes);
    if (sceneIndex == 0){
        currentScene = sceneStart;
    }
    
    if ( dialogIndex< currentScene.dialog.length){
        console.log(currentScene.dialog[dialogIndex].text);
        dialogIndex ++;
    } else {
        dialogIndex = 0;
    }
    
        
    // if (sceneIndex < Object.keys(scenes).length){
        
    //     sceneIndex += 1;
    //     console.log(scenes[currentScene.next_scene])
    //     currentScene = scenes[currentScene.next_scene];
        

    // }
    

    // console.log(dialogIndex, sceneIndex, currentScene.dialog.length, Object.keys(scenes).length)

    // console.log(currentScene.dialog[dialogIndex].text);
    // 
    // 
    // 
    // else {
        
    //     sceneIndex += 1
        
    //     if (sceneIndex < Object.keys(scenes).length){
    //         currentScene = scenes[currentScene.next_scene];
    //         dialogIndex = 0;
    //         console.log("next scene");
            
    //     } else {
    //         print("not scene")
    //     }
    // }
    // console.log(Object.keys(currentScene.dialog[0].text).length);}
  
    
}




function pullBackground(scene){
    const pathBg = "backgrounds/"; 
    return pathBg + scene.bg + ".png";
}

function pullAudioBackground(scene){
    const pathAudio = "audio/";
    return pathBg + scene.audio + ".mp3";
}



function dialog(scene, indexText){
    const dialog = scene.dialog;
    print(dialog[indexText].text);
}
    
function createSceneStart(sceneData){
    let sceneStart;
    Object.keys(sceneData).forEach((scene, index) => {
        if (index == 0){
            sceneStart = scene;
        }
    });
    return sceneStart
}

function imageBackground(scene){
    const sceneStart = sceneData[createSceneStart(scene)];
    const background = sceneStart.background;
    print(background);

}


// let textIndex = 0
// function changeDialog() {
//     textIndex += 1;
//     dialog(sceneStart, textIndex);
 
    
// }



