# 🕵️‍♂️ Image Steganography (LSB Encoder/Decoder) – Day 48

## 💡 Overview
The **Image Steganography Tool** hides secret text messages inside an image using the  
**Least Significant Bit (LSB)** technique.  

This project demonstrates:
- bit manipulation  
- simple cryptography  
- image processing  
- building CLI tools  

It includes both **encoding** (hiding text) and **decoding** (extracting hidden text),  
with optional password-based XOR obfuscation for added privacy.

Perfect for cybersecurity enthusiasts, forensics practice,  
and anyone learning how data hiding works.

---

## 🚀 Features
- 🖼️ Hide messages invisibly inside PNG images  
- 🔓 Extract hidden messages from stego-images  
- 🔐 Optional password XOR for light obfuscation  
- 🧠 Uses LSB (Least Significant Bit) method  
- 📦 Works with RGB or RGBA images  
- 🎯 CLI tool (encode & decode modes)  
- 💻 Simple, clean, and lightweight  

---

## 🧠 Concepts Used
- Bitwise operations (`&`, `|`)  
- Binary encoding of text  
- LSB steganography  
- XOR encryption using SHA-256–derived key  
- Image processing with Pillow  
- CLI argument parsing  

---

## ▶️ Usage
- 🔐 Encode a secret message
- python stego.py encode input.png "This is a secret" output.png

## 🔐 Encode with password
- python stego.py encode input.png "Top secret data" output.png mypassword

## 🔓 Decode hidden message
- python stego.py decode output.png

## 🔓 Decode with password
- python stego.py decode output.png mypassword