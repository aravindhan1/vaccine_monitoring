# Smart Vaccine Cold Chain Monitoring System

An industrial-grade, fault-tolerant embedded IoT architecture designed to strictly monitor the 2°C–8°C cold chain for vaccine storage. Built using a distributed multi-node network of STM32 microcontrollers and ESP32 wireless gateways.

## 🚀 System Architecture
* **Edge Nodes (STM32F446RE & STM32F401RE):** Runs a custom FreeRTOS implementation utilizing DMA-driven ADC pipelines to read analog temperature sensors with zero CPU blocking. 
* **Hardware Bridge (UART):** Direct memory-mapped USART bridge passing packed C-structs with checksum validation between the STM32 nodes and ESP32 modules.
* **IoT Gateway (ESP32):** Acts as a wireless bridge, wrapping edge telemetry into lightweight JSON payloads and publishing them via MQTT.
* **Central Hub (Ubuntu/Linux):** Hosts a local Mosquitto MQTT broker, resolving cross-subnet routing and enterprise AP isolation.
* **Alert Manager (Python):** Concurrent threading system that listens to MQTT topics, evaluates factory thresholds, and dispatches cooldown-regulated SMTP email alerts.
* **Live Dashboard (HTML/JS):** Zero-latency WebSockets dashboard for remote telemetry visualization without page reloads.

## 🛠️ Tech Stack
* **Firmware:** C/C++, FreeRTOS, STM32CubeIDE, Arduino Core (ESP32)
* **Backend:** Python, Mosquitto MQTT, WebSockets
* **Protocols:** UART, I2C, MQTT, SMTP, HTTP

## 📂 Directory Structure
* `/pn01/` - STM32CubeIDE FreeRTOS project for Node 1 (F446RE)
* `/pn02/` - STM32CubeIDE bare-metal/RTOS project for Node 2 (F401RE)
* `/node1_iot/` - ESP32 Gateway firmware
* `main.py` - Python Alert Manager & Web Server
* `index.html` - Live WebSockets Dashboard
