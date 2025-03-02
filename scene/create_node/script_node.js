
let allNodeValue = {};

const canvas = document.getElementById("flowchartCanvas");
const ctx = canvas.getContext("2d");

const scale = window.devicePixelRatio;
canvas.width = (window.innerWidth - 20) * scale;
canvas.height = (window.innerHeight - 20) * scale;
canvas.style.width = `${window.innerWidth - 20}px`;
canvas.style.height = `${window.innerHeight - 20}px`;
ctx.scale(scale, scale);

let nodes = [
    { x: 100, y: 100, width: 80, height: 50, id: 1, title: "Node 1" },
    { x: 300, y: 200, width: 80, height: 50, id: 2, title: "Node 2" },
    { x: 500, y: 100, width: 80, height: 50, id: 3, title: "Node 3" }
];

let connections = [];
let selectedOutput = null;
let tempConnection = null;
let isDragging = false;
let selectedNode = null;

function drawRoundedRect(x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fillStyle = "white";
    ctx.fill();
    ctx.strokeStyle = "#ccc";
    ctx.lineWidth = 1;
    ctx.stroke();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    connections.forEach(({ from, to }) => {
        ctx.beginPath();
        ctx.moveTo(from.x + from.width + 10, from.y + from.height / 2);
        ctx.lineTo(to.x - 10, to.y + to.height / 2);
        ctx.strokeStyle = "black";
        ctx.lineWidth = 2;
        ctx.stroke();
    });

    if (tempConnection) {
        ctx.beginPath();
        ctx.moveTo(tempConnection.x, tempConnection.y);
        ctx.lineTo(tempConnection.endX, tempConnection.endY);
        ctx.strokeStyle = "gray";
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    nodes.forEach(node => {
        drawRoundedRect(node.x, node.y, node.width, node.height, 5);
        ctx.fillStyle = "black";
        ctx.font = "bold 14px Arial";
        ctx.fillText(node.title, node.x + 10, node.y + node.height / 2 + 5);

        ctx.beginPath();
        ctx.arc(node.x - 10, node.y + node.height / 2, 7, 0, Math.PI * 2);
        ctx.fillStyle = "red";
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x + node.width + 10, node.y + node.height / 2, 7, 0, Math.PI * 2);
        ctx.fillStyle = "green";
        ctx.fill();
    });
}

draw();

function getOutputAt(x, y) {
    return nodes.find(node => {
        const dx = x - (node.x + node.width + 10);
        const dy = y - (node.y + node.height / 2);
        return Math.sqrt(dx * dx + dy * dy) <= 7;
    });
}

function getInputAt(x, y) {
    return nodes.find(node => {
        const dx = x - (node.x - 10);
        const dy = y - (node.y + node.height / 2);
        return Math.sqrt(dx * dx + dy * dy) <= 7;
    });
}

canvas.addEventListener("mousedown", (event) => {
    const { offsetX, offsetY } = event;
    const outputNode = getOutputAt(offsetX, offsetY);
    if (outputNode) {
        selectedOutput = outputNode;
        tempConnection = { x: outputNode.x + outputNode.width + 10, y: outputNode.y + outputNode.height / 2, endX: offsetX, endY: offsetY };
    } else {
        selectedNode = nodes.find(node => offsetX > node.x && offsetX < node.x + node.width && offsetY > node.y && offsetY < node.y + node.height);
        if (selectedNode) {
            isDragging = true;
        }
    }
});

canvas.addEventListener("mousemove", (event) => {
    if (isDragging && selectedNode) {
        selectedNode.x = event.offsetX - selectedNode.width / 2;
        selectedNode.y = event.offsetY - selectedNode.height / 2;
        draw();
    } else if (tempConnection) {
        tempConnection.endX = event.offsetX;
        tempConnection.endY = event.offsetY;
        draw();
    }
});

canvas.addEventListener("mouseup", (event) => {
    if (isDragging) {
        isDragging = false;
        selectedNode = null;
    } else if (tempConnection) {
        const targetNode = getInputAt(event.offsetX, event.offsetY);
        if (targetNode && selectedOutput !== targetNode) {
            connections.push({ from: selectedOutput, to: targetNode });
        }
        tempConnection = null;
        selectedOutput = null;
        draw();
    }
});

function addNode() {
    document.getElementById("nodeForm").style.display = "block";
}

document.getElementById("addNodeButton").addEventListener("click", addNode);

document.getElementById("saveNodeButton").addEventListener("click", () => {
    const title = document.getElementById("nodeTitle").value;
    const newNode = {
        x: Math.random() * (canvas.width / scale - 100),
        y: Math.random() * (canvas.height / scale - 100),
        width: 80,
        height: 50,
        id: nodes.length + 1,
        title: title
    };

    const adTextForms = document.querySelectorAll(".container");
    const texts = [];
    adTextForms.forEach(form => {
        const speaker = form.querySelector("input").value;
        const text = form.querySelector("textarea").value;
        texts.push({ speaker, text });
        form.remove();
    });

    newNode.texts = texts


    const nodeValue = {
        title: title,
        texts: texts
    };


    allNodeValue[nodeValue.title] = nodeValue;

    console.log(allNodeValue);


    nodes.push(newNode);

    document.getElementById("nodeForm").style.display = "none";
    document.getElementById("nodeTitle").value = "";

    draw();
});

let formCount = 0;
document.getElementById("addTextButton").addEventListener("click", () => {
    // const adTextForm = document.createElement("div");
    // adTextForm.className = "container";
    // adTextForm.style.marginTop = "5px";

    // const speakerDiv = document.createElement("div");
    // const speakerInput = document.createElement("input");
    // speakerInput.type = "text";
    // speakerInput.placeholder = "speaker";
    // speakerDiv.appendChild(speakerInput);

    // const textDiv = document.createElement("div");
    // const textarea = document.createElement("textarea");
    // textarea.type = "text";
    // textarea.placeholder = "Text dialog";
    // textDiv.appendChild(textarea);

    // const removeDiv = document.createElement("div");
    // const removeButton = document.createElement("button");
    // removeDiv.appendChild(removeButton);
    // removeButton.className = "removeButton";
    // removeButton.innerHTML = "remove";

    // removeButton.addEventListener("click", () => {
    //     adTextForm.remove();
    // });


    // adTextForm.appendChild(speakerDiv);
    // adTextForm.appendChild(textDiv);
    // adTextForm.appendChild(removeDiv);

    // document.getElementById("nodeForm").insertBefore(adTextForm, document.getElementById("btnForm"));



    formCount++;
    const form = document.createElement('form');

    const table = document.createElement('table');
    table.style.borderSpacing = '10px';
    table.style.width = '100%';
    table.style.border = '1px solid #e3e3e3';
    table.style.marginTop = '1px';
    table.style.backgroundColor = '#f9f9f9';

    const row = document.createElement('tr');

    const labelCell = document.createElement('td');
    labelCell.style.width = '5%';
    labelCell.style.height = '100%';
    const label = document.createElement('label');
    label.style.width = '100%';
    label.style.height = '50%';
    label.style.margin = 'auto';
    label.style.fontSize = '1em';
    label.textContent = `script ${formCount}`;
    labelCell.appendChild(label);
    row.appendChild(labelCell);

    const inputCell1 = document.createElement('td');
    inputCell1.style.width = '25%';
    inputCell1.style.height = '100%';
    const input1 = document.createElement('input');
    input1.style.width = '100%';
    input1.style.height = '50%';
    input1.style.margin = 'auto';
    input1.type = 'text';
    input1.id = 'field2';
    input1.name = 'field2';
    inputCell1.appendChild(input1);
    row.appendChild(inputCell1);

    const inputCell2 = document.createElement('td');
    inputCell2.style.width = '65%';
    inputCell2.style.height = '100%';
    const input2 = document.createElement('input');
    input2.type = 'text';
    input2.style.margin = 'auto';
    input2.style.width = '100%';
    inputCell2.appendChild(input2);
    row.appendChild(inputCell2);

    const buttonCell = document.createElement('td');
    buttonCell.style.width = '5%';
    buttonCell.style.height = '100%';
    const buttonRemove = document.createElement('button');
    buttonRemove.className = 'buttonRemove';
    buttonRemove.style.width = '30px';
    buttonRemove.style.height = '30px';
    buttonRemove.style.backgroundColor = "#ff1f53";
    buttonRemove.style.display = 'block';
    buttonRemove.textContent = 'X';
    buttonRemove.style.margin = 'auto';
    
    buttonCell.appendChild(buttonRemove);
    row.appendChild(buttonCell);
    buttonRemove.addEventListener('click', function () {
        form.remove();
    });

    table.appendChild(row);
    form.appendChild(table);

    document.getElementById("nodeForm").insertBefore(form, document.getElementById("btnForm"));
});