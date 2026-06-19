#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// 1. The exact same data bucket we built on the STM32
typedef struct __attribute__((packed)) {
    uint16_t sync_header;  
    float    inner_temp;   
    float    surr_temp;    
    uint8_t  alert_inner;  
    uint8_t  alert_surr;   
    uint8_t  checksum;     
} SensorPacket_t;

SensorPacket_t rx_packet;

// ==========================================
// NETWORK SETTINGS - CHANGE THESE!
// ==========================================
const char* ssid = "wifi";
const char* password = "1234567890#";
const char* mqtt_server = "10.172.99.147"; // The IP of your Linux Hub
// ==========================================

// Network Objects
WiFiClient espClient;
PubSubClient client(espClient);

// ESP32-S3 Pin Routing
#define RX_PIN 16 
#define TX_PIN 17 
HardwareSerial STM32Serial(1); 

// Helper function to connect to MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect as "ESP32_Node1"
    if (client.connect("ESP32_Node1")) {
      Serial.println("CONNECTED to Broker!");
    } else {
      Serial.print("FAILED, rc=");
      Serial.print(client.state());
      Serial.println(" Trying again in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  STM32Serial.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(2000);
  
  // 1. Connect to Wi-Fi
  Serial.println();
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi Connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // 2. Point to the Linux Mosquitto Broker (Port 1883 is the standard MQTT port)
  client.setServer(mqtt_server, 1883);
}

void loop() {
  // Keep the MQTT connection alive
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read data from the STM32
  if (STM32Serial.available() >= sizeof(SensorPacket_t)) {
    STM32Serial.readBytes((uint8_t*)&rx_packet, sizeof(SensorPacket_t));

    // Validate Packet
    if (rx_packet.sync_header == 0xAABB) {
      uint8_t sum = 0;
      uint8_t *ptr = (uint8_t*)&rx_packet;
      for(int i = 0; i < sizeof(SensorPacket_t) - 1; i++) {
          sum += ptr[i];
      }

      if (sum == rx_packet.checksum) {
        // SUCCESS! Format the data into a lightweight JSON string
        char jsonBuffer[128];
        snprintf(jsonBuffer, sizeof(jsonBuffer), 
                 "{\"inner_temp\":%.1f, \"surr_temp\":%.1f, \"alert_inner\":%d, \"alert_surr\":%d}", 
                 rx_packet.inner_temp, rx_packet.surr_temp, rx_packet.alert_inner, rx_packet.alert_surr);
                 
        // Print it to the local USB monitor
        Serial.print("Publishing: ");
        Serial.println(jsonBuffer);
        
        // PUBLISH it to the Broker on the "factory/node1/sensors" topic!
        client.publish("factory/node1/sensors", jsonBuffer);
        
      } else {
        Serial.println("UART Error: Checksum mismatch!");
      }
    } else {
      Serial.println("UART Error: Out of sync! Flushing...");
      while(STM32Serial.available()) { STM32Serial.read(); }
    }
  }
}