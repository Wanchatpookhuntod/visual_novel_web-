let allNodeValue = {};

const canvas = document.getElementById("flowchartCanvas");
const ctx = canvas.getContext("2d");

const scale = window.devicePixelRatio;
canvas.width = (window.innerWidth - 20) * scale;
canvas.height = (window.innerHeight - 20) * scale;
canvas.style.width = `${window.innerWidth - 20}px`;
canvas.style.height = `${window.innerHeight - 20}px`;
ctx.scale(scale, scale);

let nodes = [];
let connections = [];
let selectedOutput = null;
let tempConnection = null;
let isDragging = false;
let selectedNode = null;
let maxX = 0;
let maxY = 0;

function drawRoundedRect(x, y, width, height, radius, title, isSelected) {
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
    ctx.strokeStyle = isSelected ? "#007bff" : "#ccc";
    ctx.lineWidth = 1.2;
    ctx.stroke();

    // วาดตัวอักษรให้อยู่กึ่งกลาง
    ctx.fillStyle = "black";
    ctx.font = "bold 14px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(title, x + width / 2, y + height / 2);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    connections.forEach(({ from, to }) => {
        ctx.beginPath();
        ctx.moveTo(from.x + from.width + 5, from.y + from.height / 2);
        const cp1x = from.x + from.width + 50;
        const cp1y = from.y + from.height / 2;
        const cp2x = to.x - 50;
        const cp2y = to.y + to.height / 2;
        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, to.x - 5, to.y + to.height / 2);
        ctx.strokeStyle = "black";
        ctx.lineWidth = 2;
        ctx.stroke();

        // วาดวงกลมที่ปลายเส้นเชื่อมต่อ
        ctx.beginPath();
        ctx.arc(to.x - 5, to.y + to.height / 2, 5, 0, Math.PI * 2);
        ctx.fillStyle = "black";
        ctx.fill();
    });

    if (tempConnection) {
        ctx.beginPath();
        ctx.moveTo(tempConnection.x, tempConnection.y);
        const cp1x = tempConnection.x + 50;
        const cp1y = tempConnection.y;
        const cp2x = tempConnection.endX - 50;
        const cp2y = tempConnection.endY;
        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, tempConnection.endX, tempConnection.endY);
        ctx.strokeStyle = "gray";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // วาดวงกลมที่ปลายเส้นเชื่อมต่อชั่วคราว
        ctx.beginPath();
        ctx.arc(tempConnection.endX, tempConnection.endY, 5, 0, Math.PI * 2);
        ctx.fillStyle = "black";
        ctx.fill();
    }

    nodes.forEach(node => {
        drawRoundedRect(node.x, node.y, node.width, node.height, 5, node.title, node === selectedNode);

        ctx.beginPath();
        ctx.arc(node.x - 5, node.y + node.height / 2, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#ccc";
        ctx.fill();
        ctx.strokeStyle = node === selectedNode ? "#007bff" : "gray";
        ctx.lineWidth = 1.2;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(node.x + node.width + 5, node.y + node.height / 2, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#ccc";
        ctx.fill();
        ctx.strokeStyle = node === selectedNode ? "#007bff" : "gray";
        ctx.lineWidth = 1.2;
        ctx.stroke();
    });
}

draw();

function getOutputAt(x, y) {
    return nodes.find(node => {
        const dx = x - (node.x + node.width + 5);
        const dy = y - (node.y + node.height / 2);
        return Math.sqrt(dx * dx + dy * dy) <= 5;
    });
}

function getInputAt(x, y) {
    return nodes.find(node => {
        const dx = x - (node.x - 5);
        const dy = y - (node.y + node.height / 2);
        return Math.sqrt(dx * dx + dy * dy) <= 5;
    });
}

function getNodeAt(x, y) {
    return nodes.find(node => x > node.x && x < node.x + node.width && y > node.y && y < node.y + node.height);
}

function isConnected(node, type) {
    return connections.some(connection => {
        if (type === 'input') {
            return connection.to === node;
        } else if (type === 'output') {
            return connection.from === node;
        }
        return false;
    });
}

canvas.addEventListener("mousedown", (event) => {
    const { offsetX, offsetY } = event;
    const outputNode = getOutputAt(offsetX, offsetY);
    if (outputNode) {
        selectedOutput = outputNode;
        tempConnection = { x: outputNode.x + outputNode.width + 10, y: outputNode.y + outputNode.height / 2, endX: offsetX, endY: offsetY };
    } else {
        selectedNode = getNodeAt(offsetX, offsetY);
        if (selectedNode) {
            isDragging = true;
        }
    }
});

canvas.addEventListener("mousemove", (event) => {
    if (isDragging && selectedNode) {
        selectedNode.x = event.offsetX - selectedNode.width / 2;
        selectedNode.y = event.offsetY - selectedNode.height / 2;
        getMaxXAndYValues();
        expandCanvasIfNeeded();
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

            // เพิ่มข้อมูลการเชื่อมต่อไปยังโหนด
            if (!selectedOutput.connections) {
                selectedOutput.connections = [];
            }
            if (!targetNode.connections) {
                targetNode.connections = [];
            }
            selectedOutput.connections.push({ next: targetNode.title });
            targetNode.connections.push({ previous: selectedOutput.title });
        }
        tempConnection = null;
        selectedOutput = null;
        draw();
    }
});

canvas.addEventListener("dblclick", (event) => {
    const { offsetX, offsetY } = event;
    const targetNode = getInputAt(offsetX, offsetY);
    if (targetNode) {
        // ลบการเชื่อมต่อที่เกี่ยวข้องกับ targetNode
        const connectionsToRemove = connections.filter(connection => connection.to === targetNode);
        connectionsToRemove.forEach(connection => {
            const fromNode = connection.from;
            fromNode.connections = fromNode.connections.filter(conn => conn.next !== targetNode.title);
        });
        connections = connections.filter(connection => connection.to !== targetNode);

        // ลบข้อมูลการเชื่อมต่อในโหนด
        targetNode.connections = targetNode.connections.filter(connection => connection.previous !== targetNode.title);

        // ตรวจสอบและลบข้อมูล input และ output ถ้าไม่มีการเชื่อมต่ออยู่
        nodes.forEach(node => {
            if (!isConnected(node, 'input') && !isConnected(node, 'output')) {
                node.connections = [];
            } else {
                node.connections = node.connections.filter(connection => connection.next !== targetNode.title && connection.previous !== targetNode.title);
            }
        });

        draw();
    }
});

canvas.addEventListener("click", (event) => {
    const { offsetX, offsetY } = event;
    const clickedNode = getNodeAt(offsetX, offsetY);
    if (clickedNode) {
        selectedNode = clickedNode;
        displayNodeInfo(clickedNode); // แสดงข้อมูลของโหนดที่เลือก
    } else {
        selectedNode = null;
        clearNodeInfo(); // ล้างข้อมูลเมื่อไม่มีโหนดถูกเลือก
    }
    draw();
    
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Delete" && selectedNode) {
        // ลบโหนดที่เลือก
        nodes = nodes.filter(node => node !== selectedNode);
        connections = connections.filter(connection => connection.from !== selectedNode && connection.to !== selectedNode);
        delete allNodeValue[selectedNode.title]; // ลบข้อมูลของโหนดจาก allNodeValue
        selectedNode = null;
        clearNodeInfo();
        draw();
    }
});

function displayNodeInfo(node) {
    const nodeInfo = document.getElementById("nodeInfo");
    nodeInfo.style.display = "block";
    nodeInfo.innerHTML = `
        <p><strong>Scene:</strong> ${node.title}</p>
        <p><strong>Dialog: sp/text</strong></p>
        <ul>
            ${node.texts.map(text => `<li>${text.speaker} >> ${text.text}</li>`).join('')}
        </ul>
        <p><strong>Prev/Next:</strong></p>
        <ul>
            ${node.connections.map(conn => `<li>${conn.previous ? 'Previous: ' + conn.previous : 'Next: ' + conn.next}</li>`).join('')}
        </ul>
    `;
}

function clearNodeInfo() {
    const nodeInfo = document.getElementById("nodeInfo");
    nodeInfo.innerHTML = '';
    nodeInfo.style.display = "none";
}

function addNode() {
    document.getElementById("nodeForm").style.display = "block";
}

document.getElementById("addNodeButton").addEventListener("click", addNode);

document.getElementById("saveNodeButton").addEventListener("click", () => {
    const title = document.getElementById("nodeTitle").value;
    const newNode = {
        x: (canvas.width / scale - 100) / 2,
        y: (canvas.height / scale - 100) / 2,
        width: 100,
        height: 50,
        id: nodes.length + 1,
        title: title,
        texts: [],
        connections: [] // เพิ่มฟิลด์ connections เพื่อเก็บข้อมูลการเชื่อมต่อ
    };

    const adTextForms = document.querySelectorAll("form");
    adTextForms.forEach(form => {
        const speaker = form.querySelector("input[type='speaker']").value;
        const text = form.querySelector("input[type='text']").value;
        newNode.texts.push({ speaker, text });
        form.remove();
    });

    allNodeValue[newNode.title] = newNode;

    console.log(allNodeValue);

    nodes.push(newNode);

    document.getElementById("nodeForm").style.display = "none";
    document.getElementById("nodeTitle").value = "";

    draw();
});

let formCount = 0;

function createForm() {
    formCount++;
    const form = document.createElement('form');

    const table = document.createElement('table');
    table.style.borderSpacing = '10px';
    table.style.width = '100%';
    table.style.border = '1px solid #e3e3e3';
    table.style.marginTop = '1px';
    table.style.backgroundColor = '#f9f9f9';

    const row = document.createElement('tr');

    const labelCell = createCell('td', '5%', '100%');
    const label = createLabel(`script ${formCount}`, '100%', '50%');
    labelCell.appendChild(label);
    row.appendChild(labelCell);

    const inputCell1 = createCell('td', '25%', '100%');
    const input1 = createInput('speaker', '100%', '50%', 'speaker', 'speaker');
    inputCell1.appendChild(input1);
    row.appendChild(inputCell1);

    const inputCell2 = createCell('td', '65%', '100%');
    const input2 = createInput('text', '100%', 'auto', 'text', 'text');
    inputCell2.appendChild(input2);
    row.appendChild(inputCell2);

    const buttonCell = createCell('td', '5%', '100%');
    const buttonRemove = createButton('X', '30px', '30px', '#ff1f53');
    buttonRemove.addEventListener('click', () => form.remove());
    buttonCell.appendChild(buttonRemove);
    row.appendChild(buttonCell);

    table.appendChild(row);
    form.appendChild(table);

    document.getElementById("nodeForm").insertBefore(form, document.getElementById("btnForm"));
}

function createCell(tag, width, height) {
    const cell = document.createElement(tag);
    cell.style.width = width;
    cell.style.height = height;
    return cell;
}

function createLabel(text, width, height) {
    const label = document.createElement('label');
    label.style.width = width;
    label.style.height = height;
    label.style.margin = 'auto';
    label.style.fontSize = '1em';
    label.textContent = text;
    return label;
}

function createInput(type, width, height, id = '', name = '') {
    const input = document.createElement('input');
    input.type = type;
    input.style.width = width;
    input.style.height = height;
    input.style.margin = 'auto';
    if (id) input.id = id;
    if (name) input.name = name;
    return input;
}

function createButton(text, width, height, backgroundColor) {
    const button = document.createElement('button');
    button.className = 'buttonRemove';
    button.style.width = width;
    button.style.height = height;
    button.style.backgroundColor = backgroundColor;
    button.style.display = 'block';
    button.style.margin = 'auto';
    button.textContent = text;
    return button;
}

document.getElementById("addTextButton").addEventListener("click", createForm);

function getMaxXAndYValues() {
    maxX = 0;
    maxY = 0;
    for (const key in allNodeValue) {
        if (allNodeValue[key].x + allNodeValue[key].width > maxX) {
            maxX = allNodeValue[key].x + allNodeValue[key].width;
        }
        if (allNodeValue[key].y + allNodeValue[key].height > maxY) {
            maxY = allNodeValue[key].y + allNodeValue[key].height;
        }
    }
    console.log({ maxX, maxY });
    console.log(`${canvas.width}px`, `${canvas.height}px`);
}

function expandCanvasIfNeeded() {
    const X = maxX + 50; // เพิ่ม margin 50px
    const Y = maxY + 50;
    if (X > canvas.width / scale || Y > canvas.height / scale) {
        canvas.width = Math.max(canvas.width / scale, X) * scale;
        canvas.height = Math.max(canvas.height / scale, Y) * scale;
        canvas.style.width = `${Math.max(canvas.width / scale, X)}px`;
        canvas.style.height = `${Math.max(canvas.height / scale, Y)}px`;
        ctx.scale(scale, scale);
        draw(); // รีวาดหลังขยาย

        // เลื่อนหน้าเว็บไปยังจุดที่ลาก
        window.scrollTo({ left: maxX - window.innerWidth / 2, top: maxY - window.innerHeight / 2, behavior: "smooth" });
    }
}



canvas.addEventListener("contextmenu", (event) => {
    event.preventDefault(); // ป้องกันเมนูบริบทเริ่มต้นของเบราว์เซอร์
    document.getElementById("nodeForm").style.display = "block";
    draw();
});


canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    const zoomFactor = 0.1;
    const mouseX = event.offsetX;
    const mouseY = event.offsetY;

    if (event.deltaY < 0) {
        // Zoom in
        ctx.scale(1 + zoomFactor, 1 + zoomFactor);
        ctx.translate(-mouseX * zoomFactor, -mouseY * zoomFactor);
    } else {
        // Zoom out
        ctx.scale(1 - zoomFactor, 1 - zoomFactor);
        ctx.translate(mouseX * zoomFactor, mouseY * zoomFactor);
    }

    draw();
});

