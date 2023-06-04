import crypto from "crypto";

export const storeEncryptedDataInLocalStorage = (data, localStorageKey) => {
  const key = "mysecretkey";
  const encryptedData = encryptData(data, key);
  localStorage.setItem(localStorageKey, encryptedData);
};

export const getDataFromLocalStorage = (localStorageKey) => {
  const key = "mysecretkey";
  const encryptedData = localStorage.getItem(localStorageKey);
  if (encryptedData) {
    return decryptData(encryptedData, key);
  } else {
    return null;
  }
};

// Encryption function using AES algorithm
export const encryptData = (data, key) => {
  const cipher = crypto.createCipher("aes-256-cbc", key);
  let encryptedData = cipher.update(JSON.stringify(data));
  encryptedData = Buffer.concat([encryptedData, cipher.final()]);
  return encryptedData.toString("hex");
};

// Decryption function using AES algorithm
export const decryptData = (encryptedData, key) => {
  const decipher = crypto.createDecipher("aes-256-cbc", key);
  let decryptedData = decipher.update(Buffer.from(encryptedData, "hex"));
  decryptedData = Buffer.concat([decryptedData, decipher.final()]);
  return JSON.parse(decryptedData.toString());
};
