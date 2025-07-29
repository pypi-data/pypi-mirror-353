use pyo3::prelude::*;
use mac_address::get_mac_address;
use chrono::{Duration, Utc};
use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Key, Nonce,
};
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
use rand::Rng;

const KEY: &[u8] = b"your-32-byte-secret-key-here!!!!";
const NONCE_LEN: usize = 12;

#[pyfunction]
fn get_mac_address_py() -> PyResult<String> {
    let mac = get_mac_address()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    if let Some(mac) = mac {
        Ok(format!("{:02X?}", mac.bytes()))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("No MAC address found"))
    }
}

#[pyfunction]
fn encrypt_info() -> PyResult<String> {
    let mac = get_mac_address_py()?;
    encrypt_info_custom(&mac, 7)
}

#[pyfunction]
fn encrypt_info_custom(mac: &str, days: i64) -> PyResult<String> {
    let expiry = Utc::now() + Duration::days(days);
    let data = format!("{}|{}", mac, expiry.timestamp());
    
    let key = Key::<Aes256Gcm>::from_slice(KEY);
    let cipher = Aes256Gcm::new(key);
    
    let mut rng = rand::thread_rng();
    let mut nonce_bytes = [0u8; NONCE_LEN];
    rng.fill(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);
    
    let ciphertext = cipher
        .encrypt(nonce, data.as_bytes())
        .map_err(|e: aes_gcm::Error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let mut result = nonce_bytes.to_vec();
    result.extend(ciphertext);
    Ok(BASE64.encode(result))
}

#[pyfunction]
fn verify_info(encrypted: &str) -> PyResult<(bool, bool)> {
    let mac = get_mac_address_py()?;
    verify_info_custom(encrypted, &mac)
}

#[pyfunction]
fn verify_info_custom(encrypted: &str, mac: &str) -> PyResult<(bool, bool)> {
    let key = Key::<Aes256Gcm>::from_slice(KEY);
    let cipher = Aes256Gcm::new(key);
    
    let data = BASE64.decode(encrypted)
        .map_err(|e: base64::DecodeError| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    if data.len() < NONCE_LEN {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Invalid encrypted data"));
    }
    
    let (nonce_bytes, ciphertext) = data.split_at(NONCE_LEN);
    let nonce = Nonce::from_slice(nonce_bytes);
    
    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e: aes_gcm::Error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let decrypted = String::from_utf8(plaintext)
        .map_err(|e: std::string::FromUtf8Error| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let parts: Vec<&str> = decrypted.split('|').collect();
    if parts.len() != 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Invalid decrypted data format"));
    }
    
    let stored_mac = parts[0];
    let expiry_timestamp: i64 = parts[1].parse()
        .map_err(|e: core::num::ParseIntError| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let mac_mismatch = stored_mac != mac;
    let expired = Utc::now().timestamp() > expiry_timestamp;
    
    Ok((mac_mismatch, expired))
}

#[pymodule]
fn mac_validator(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_mac_address_py, m)?)?;
    m.add_function(wrap_pyfunction!(encrypt_info, m)?)?;
    m.add_function(wrap_pyfunction!(encrypt_info_custom, m)?)?;
    m.add_function(wrap_pyfunction!(verify_info, m)?)?;
    m.add_function(wrap_pyfunction!(verify_info_custom, m)?)?;
    Ok(())
} 