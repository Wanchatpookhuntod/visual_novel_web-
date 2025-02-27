function parseYAML(yamlString) {
  const lines = yamlString.split("\n");
  const result = {};
  const stack = [{ object: result, indent: -1, key: null }];

  lines.forEach(line => {
    if (line.trim() === "" || line.trim().startsWith("#")) return; // ข้ามบรรทัดว่างและคอมเมนต์

    const indentLevel = line.search(/\S/);
    const trimmedLine = line.trim();

    // ลดระดับ Stack หาก indent น้อยลง
    while (stack.length > 1 && stack[stack.length - 1].indent >= indentLevel) {
      stack.pop();
    }

    let currentObject = stack[stack.length - 1].object;

    if (trimmedLine.startsWith("-")) {
      // กรณีเป็น List
      const value = parseValue(trimmedLine.slice(1).trim());

      if (!Array.isArray(currentObject[stack[stack.length - 1].key])) {
        currentObject[stack[stack.length - 1].key] = [];
      }
      currentObject[stack[stack.length - 1].key].push(value);
    } else {
      // กรณีเป็น Key-Value
      const keyValue = trimmedLine.split(/:(.+)/);
      if (keyValue.length < 2) return;

      const key = keyValue[0].trim();
      let value = keyValue[1].trim();

      if (value === "") {
        // ถ้าไม่มีค่า -> เป็น Object ใหม่
        currentObject[key] = {};
        stack.push({ object: currentObject[key], indent: indentLevel, key });
      } else {
        // กำหนดค่าให้ Object
        currentObject[key] = parseValue(value);
      }
    }
  });

  return result;
}

function parseValue(value) {
  if (value === "true") return true;
  if (value === "false") return false;
  if (!isNaN(value) && value !== "") return Number(value);
  if (value === "null" || value === "~") return null;
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1); // ตัด " หรือ '
  }
  return value;
}

const yamlString = `
app:
  name: MyApplication
  version: 2.0
  description: "This is a sample YAML configuration file."

database:
  host: localhost
  port: 5432
  username: admin
  password: secret

features:
  - Authentication
  - Logging
  - Analytics

users:
  - name: Alice
    role: admin
  - name: Bob
    role: user

logging:
  level: debug
  format: json

api_keys:
  google: "AIzaSy12345"
  stripe: "sk_test_67890"
`;

const jsonData = parseYAML(yamlString);
console.log(jsonData)