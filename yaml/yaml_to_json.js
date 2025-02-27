document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('yamlFileInput').addEventListener('change', convertYaml);
});

function convertYaml() {
    const fileInput = document.getElementById('yamlFileInput');
    const file = fileInput.files[0];

    if (!file) {
        displayOutput('<span class="error">กรุณาเลือกไฟล์ YAML</span>');
        return;
    }

    const reader = new FileReader();
    reader.onload = function (event) {
        try {
            const yamlString = event.target.result;
            const jsonData = parseYamlToJson(yamlString); // แปลง YAML เป็น JSON
            displayOutput(JSON.stringify(jsonData, null, 2)); // แสดง JSON บนหน้าเว็บ
            processJsonData(jsonData); // ใช้ JSON กับฟังก์ชันอื่น
        } catch (error) {
            displayOutput(`<span class="error">เกิดข้อผิดพลาด: ${error.message}</span>`);
        }
    };

    reader.readAsText(file);
}

// ฟังก์ชันแปลง YAML เป็น JSON
function parseYamlToJson(yamlString) {
    return jsyaml.load(yamlString);
}

// ฟังก์ชันแสดงค่า JSON บน HTML
function displayOutput(content) {
    const outputDiv = document.getElementById('output');
    outputDiv.innerHTML = `<pre>${content}</pre>`;
}

// ✅ ฟังก์ชันที่ใช้ JSON ที่แปลงแล้ว
function processJsonData(data) {
    if (data.converstions && data.converstions.scene_1 && data.converstions.scene_1.dialog) {
        const dialog = data.converstions.scene_1.dialog;
        console.log("Dialog:", dialog);
        alert("พบจำนวนบทสนทนา: " + dialog.length);
    } else {
        console.log("ไม่มีข้อมูลบทสนทนา");
    }
}