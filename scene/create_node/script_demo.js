let allNodeValue = {};

const canvas = document.getElementById("flowchartCanvas");
const ctx = canvas.getContext("2d");

// 🛠 ค่าซูมและแพน
let zoomLevel = 1;
let offsetX = 0, offsetY = 0;
let isPanning = false, startPanX = 0, startPanY = 0;
const scaleFactor = 1.1; // อัตราส่วนซูม

canvas.width = window.innerWidth - 20;
canvas.height = window.innerHeight - 20;

let nodes = [];
let connections = [];
let selectedNode = null;
let isDragging = false;

// ✅ ฟังก์ชันแปลงพิกัดเมาส์ให้สัมพันธ์กับการซูม & การแพน
function getTransformedPoint(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: (clientX - rect.left - offsetX) / zoomLevel,
        y: (clientY - rect.top - offsetY) / zoomLevel
    };
}

// ✅ ฟังก์ชันวาดโหนด
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

    // วาดตัวอักษร
    ctx.fillStyle = "black";
    ctx.font = "bold 14px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(title, x + width / 2, y + height / 2);
}

// ✅ ฟังก์ชันวาดทั้งหมด
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(zoomLevel, zoomLevel);

    connections.forEach(({ from, to }) => {
        ctx.beginPath();
        ctx.moveTo(from.x + from.width + 5, from.y + from.height / 2);
        ctx.bezierCurveTo(
            from.x + from.width + 50, from.y + from.height / 2,
            to.x - 50, to.y + to.height / 2,
            to.x - 5, to.y + to.height / 2
        );
        ctx.strokeStyle = "black";
        ctx.lineWidth = 2;
        ctx.stroke();
    });

    nodes.forEach(node => {
        drawRoundedRect(node.x, node.y, node.width, node.height, 5, node.title, node === selectedNode);
    });

    ctx.restore();
}

// ✅ ฟังก์ชันค้นหาโหนดที่ถูกคลิก
function getNodeAt(clientX, clientY) {
    const { x, y } = getTransformedPoint(clientX, clientY);
    return nodes.find(node => x > node.x && x < node.x + node.width && y > node.y && y < node.y + node.height);
}

// ✅ Event: คลิกเพื่อเลือกโหนด
canvas.addEventListener("mousedown", (event) => {
    if (event.button === 1) { // Middle mouse button for panning
        isPanning = true;
        startPanX = event.clientX - offsetX;
        startPanY = event.clientY - offsetY;
    } else {
        selectedNode = getNodeAt(event.clientX, event.clientY);
        if (selectedNode) {
            isDragging = true;
        }
    }
});

canvas.addEventListener("mouseup", () => { 
    isDragging = false; 
    isPanning = false; 
});

canvas.addEventListener("mousemove", (event) => {
    if (isPanning) {
        offsetX = event.clientX - startPanX;
        offsetY = event.clientY - startPanY;
        draw();
    } else if (isDragging && selectedNode) {
        const { x, y } = getTransformedPoint(event.clientX, event.clientY);
        selectedNode.x = x - selectedNode.width / 2;
        selectedNode.y = y - selectedNode.height / 2;
        expandCanvasIfNeeded(selectedNode); 
        draw();
    }
});

// ✅ Event: ซูมด้วย Mouse Wheel
canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    const { clientX, clientY } = event;
    const { x, y } = getTransformedPoint(clientX, clientY);

    const zoomFactor = event.deltaY < 0 ? scaleFactor : 1 / scaleFactor;
    const newZoomLevel = zoomLevel * zoomFactor;

    if (newZoomLevel > 0.5 && newZoomLevel < 2) { 
        zoomLevel = newZoomLevel;
        offsetX = clientX - x * zoomLevel;
        offsetY = clientY - y * zoomLevel;
        draw();
    }
});

// ✅ เพิ่มโหนดใหม่
function addNode(title, x, y) {
    nodes.push({ title, x, y, width: 100, height: 50 });
    draw();
}

// ✅ ลบโหนดที่เลือกด้วยปุ่ม Delete
document.addEventListener("keydown", (event) => {
    if (event.key === "Delete" && selectedNode) {
        nodes = nodes.filter(node => node !== selectedNode);
        connections = connections.filter(conn => conn.from !== selectedNode && conn.to !== selectedNode);
        delete allNodeValue[selectedNode.title];
        selectedNode = null;
        draw();
    }
});


function expandCanvasIfNeeded(node) {
    const padding = 50; // ระยะห่างขอบก่อนขยาย
    let expanded = false;

    // ตรวจสอบขอบขวา
    if (node.x + node.width + padding > canvas.width / zoomLevel) {
        canvas.width = (node.x + node.width + padding) * zoomLevel;
        expanded = true;
    }

    // ตรวจสอบขอบล่าง
    if (node.y + node.height + padding > canvas.height / zoomLevel) {
        canvas.height = (node.y + node.height + padding) * zoomLevel;
        expanded = true;
    }

    if (expanded) {
        draw(); // วาดใหม่เมื่อขยาย canvas
    }
}


// ✅ ตัวอย่างการเพิ่มโหนด
addNode("Node 1", 100, 100);
addNode("Node 2", 300, 150);
draw();
