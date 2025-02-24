
const yamlPath = 'scripts/demo_yaml.yaml';
let sceneData;

fetch(yamlPath)
    .then(response => response.text())
    .then(yamlString => {
    sceneData = jsyaml.load(yamlString);
    print(sceneData)

    });

function print(text){
    console.log(text);
}

let currentScene;
let currentSceneIndex = 0;
function manageSceneData(){
    print(currentSceneIndex);
    if (currentSceneIndex+1 < Object.keys(sceneData).length){
        currentSceneIndex += 1;
    } else {
        currentSceneIndex = 0;
    }
    
    
}



function changeDescription(text) {
    manageSceneData();
}



