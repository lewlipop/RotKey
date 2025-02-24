
function hexToArrayBuffer(hex) {
    const typedArray = new Uint8Array(hex.match(/[\da-f]{2}/gi).map(h => parseInt(h, 16)));
    return typedArray.buffer;
}

async function importKeyFromHex(hex) {
    const keyBuffer = hexToArrayBuffer(hex);
    return await window.crypto.subtle.importKey(
        "raw",
        keyBuffer,
        { name: "AES-GCM" },
        false,
        ["encrypt", "decrypt"]
    );
}

async function encryptWithKey(plaintext, key, iv) {
    const encoder = new TextEncoder();
    const encoded = encoder.encode(plaintext);
    return await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encoded
    );
}

async function fetchSharedKey() {
    const resp = await fetch("/get-shared-key");
    const data = await resp.json();
    document.getElementById("serverKey").textContent = data.sharedKey ? data.sharedKey : data.error;
    return data.sharedKey;
}

document.getElementById("testForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const plaintext = document.getElementById("plaintext").value;
    const iv = new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    const sharedKeyHex = await fetchSharedKey();
    if (!sharedKeyHex) {
        document.getElementById("output").textContent = "Shared key not available.";
        return;
    }
    let cryptoKey;
    try {
        cryptoKey = await importKeyFromHex(sharedKeyHex);
    } catch (err) {
        document.getElementById("output").textContent = "Error importing key: " + err;
        return;
    }
    let ciphertextBuffer;
    try {
        ciphertextBuffer = await encryptWithKey(plaintext, cryptoKey, iv);
    } catch (err) {
        document.getElementById("output").textContent = "Encryption error: " + err;
        return;
    }
    const ciphertextArray = Array.from(new Uint8Array(ciphertextBuffer));
    const response = await fetch("/decrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ encryptedData: ciphertextArray, iv: Array.from(iv) })
    });
    const result = await response.json();
    document.getElementById("output").textContent = result.decryptedData ? result.decryptedData : result.error;
});
