

const fs = require('fs');
const jsyaml = require('js-yaml');

const yamlPath = 'demo_yaml.yaml';
let sceneCurrentNumber = 1;
let sceneCurrent;

// โหลดข้อมูลบทสนทนาจากไฟล์ YAML
// fs.readFile(yamlPath, 'utf8', (error, yamlString) => {
//     if (error) {
//         console.error('Error loading YAML file:', error);
//         return;
//     }

//     // แปลงข้อมูลจาก YAML ให้อยู่ในรูปของ Object
//     const scriptData = jsyaml.load(yamlString);
//     const sceneName = Object.keys(scriptData);
//     sceneCurrent = scriptData[sceneName[sceneCurrentNumber]]
//     print(sceneCurrent);
// });


fetch(yamlPath)
    .then(response => response.text())
    .then(yamlString => {
        const sceneData = jsyaml.load(yamlString);
    })







function print(sceneCurrent) {
    console.log(sceneCurrent);
}