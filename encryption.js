async function deriveKey(password, salt) {
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        { name: "PBKDF2" },
        false,
        ["deriveKey"]
    );

    return crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt", "decrypt"]
    );
}

async function encryptData(password, data) {
    const salt = crypto.getRandomValues(new Uint8Array(16)); // Generate random salt
    const iv = crypto.getRandomValues(new Uint8Array(12));   // AES-GCM IV

    const key = await deriveKey(password, salt);
    const encryptedData = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        data
    );

    return {
        encrypted: new Uint8Array(encryptedData),
        iv: iv,
        salt: salt
    };
}

async function encryptText(password, data) {
    const encoder = new TextEncoder();
    return await encryptData(password, encoder.encode(data));
}

async function decryptData(password, encrypted, iv, salt) {
    const key = await deriveKey(password, salt);
    const decryptedData = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encrypted
    );

    return decryptedData;
}

async function decryptText(password, encrypted, iv, salt) {
    const decoder = new TextDecoder();

    return decoder.decode(await decryptData(password, encrypted, iv, salt));
}

function encryptedToStr(encrypted, iv, salt) {
    return JSON.stringify({
        encrypted: btoa(String.fromCharCode(...encrypted)),
        iv: btoa(String.fromCharCode(...iv)),
        salt: btoa(String.fromCharCode(...salt))
    });
}

const decode = str => Uint8Array.from(atob(str), c => c.charCodeAt(0));
function encryptedFromStr(s) {
    const obj = JSON.parse(s);
    return {
        encrypted: decode(obj.encrypted),
        iv: decode(obj.iv),
        salt: decode(obj.salt)
    };
}

async function encryptTextToStr(password, text) {
    const enc = await encryptText(password, text);
    return encryptedToStr(enc.encrypted, enc.iv, enc.salt);
}

async function decryptTextFromStr(password, s) {
    const enc = encryptedFromStr(s);
    return await decryptText(password, enc.encrypted, enc.iv, enc.salt);
}

async function test() {
    a = await encryptText("password", "hallo hallo");
    console.log(a);
    a_str = encryptedToStr(a.encrypted, a.iv, a.salt);
    console.log(a_str);
    a1 = encryptedFromStr(a_str);
    console.log(a1);
    b = await decryptText("password", a1.encrypted, a1.iv, a1.salt);
    console.log(b);
}


// Now the whole thing for files:

function downloadFile(data, filename, type) {
    let file = new Blob([data], {type: type});
    let a = document.createElement("a");
    let url = URL.createObjectURL(file);
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	setTimeout(function() {
		document.body.removeChild(a);
		window.URL.revokeObjectURL(url);
	}, 0);
}

async function encryptFile(password, file) {
    const fileArrayBuffer = await file.arrayBuffer();
    return encryptData(password, new Uint8Array(fileArrayBuffer));
}

function packageEncryptedData(salt, iv, encrypted) {
    const resultData = new Uint8Array(salt.length + iv.length + encrypted.length);
    resultData.set(salt, 0);
    resultData.set(iv, salt.length);
    resultData.set(encrypted, salt.length + iv.length);
    return resultData;
}

function unpackageEncryptedFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => {
            const buffer = reader.result;
            const uint8Array = new Uint8Array(buffer);

            // Extract salt (16 bytes)
            const salt = uint8Array.slice(0, 16);

            // Extract IV (12 bytes)
            const iv = uint8Array.slice(16, 28);

            // Extract encrypted data (remaining data)
            const encryptedData = uint8Array.slice(28);

            resolve( { salt: salt, iv: iv, encrypted: encryptedData });
        };

        reader.onerror = () => window.alert("Reading file failed!");

        reader.readAsArrayBuffer(file);
    });
}
