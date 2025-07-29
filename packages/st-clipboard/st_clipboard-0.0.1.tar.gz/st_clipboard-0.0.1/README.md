# Clipboard Copy Utilities for Streamlit

This Python package provides easy-to-use functions to copy text to the clipboard
within Streamlit applications, supporting both **HTTP** and **HTTPS** contexts.

## Key Features

- **Works seamlessly on both HTTP and HTTPS:**  
  Supports the modern, secure Clipboard API (`navigator.clipboard.writeText`) used in HTTPS environments,  
  and falls back to the legacy `document.execCommand('copy')` method for HTTP or older browsers.

- **No dependency on UI elements:**  
  Clipboard copy commands can be triggered programmatically anywhere in your Streamlit app  
  without requiring explicit user interaction with buttons, making integration flexible and convenient.

- **Fully compatible with Streamlit's iframe-based rendering:**  
  1% UI footprint — runs almost invisibly without affecting layout.  

## Why Use This Package?

Streamlit apps run inside iframes and are often served over HTTPS, which imposes strict browser security policies on clipboard access.  
This package provides a reliable way to copy text to the clipboard regardless of the protocol or browser limitations by using both secure and fallback methods.

## Installation

```bash
pip install st-clipboard
```

## Usage Example
Here is an example Streamlit app showing two columns with text inputs and buttons — one using the secure clipboard copy (for HTTPS), and the other using the unsecured fallback (for HTTP):

```python
import streamlit as st

from st_clipboard import copy_to_clipboard, copy_to_clipboard_unsecured


# Create two columns: HTTPS (left), HTTP (right)
col_https, col_http = st.columns(2)

with col_https:
    st.markdown("### HTTPS Clipboard Copy")
    https_text = st.text_input("Enter text to copy (HTTPS):", value="Hello HTTPS")
    if st.button("Copy to clipboard (HTTPS)"):
        copy_to_clipboard(https_text)
        st.success("Copied to clipboard using secure method!")

with col_http:
    st.markdown("### HTTP Clipboard Copy")
    http_text = st.text_input("Enter text to copy (HTTP):", value="Hello HTTP")
    if st.button("Copy to clipboard (HTTP)"):
        copy_to_clipboard_unsecured(http_text)
        st.success("Copied to clipboard using unsecured method!")

```
