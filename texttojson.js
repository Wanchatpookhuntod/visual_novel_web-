const yaml = require('js-yaml');
const fs = require('fs');

const path = 'conversations.yaml';

const yamlString = fs.readFileSync(path, 'utf8');

try{
    const parsedData = yaml.load(yamlString);
    const scene_1 = parsedData.converstions;

    console.log(scene_1.scene_1.dialog[0].text);
}

catch (e){
  console.error(e);
}


