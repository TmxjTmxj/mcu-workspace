#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
// Demo network credentials only; not a user password.
static const char *AP_NAME="SmartFan-Lab", *AP_PASSWORD="fan-demo-2026";
static const char *SERVICE="d4b10000-4aa0-4d84-9200-1abce1000001";
static const char *COMMAND="d4b10001-4aa0-4d84-9200-1abce1000001";
static const char *STATUS_UUID="d4b10002-4aa0-4d84-9200-1abce1000001";
static WebServer web(80);
static HardwareSerial controllerUart(2);
static BLECharacteristic *stateCharacteristic;
static QueueHandle_t commandQueue;
static String latest="WAITING_FOR_STM32";
struct CommandLine { char text[24]; };
static bool enqueue(const String &text) {
    if(text.length()<3 || text.length()>22 || text[1]!=',') return false;
    if(text[0]!='S' && text[0]!='M' && text[0]!='D' && text[0]!='R') return false;
    for(unsigned i=2;i<text.length();++i) if(text[i]<'0'||text[i]>'9') return false;
    CommandLine line={}; text.toCharArray(line.text,sizeof(line.text));
    return xQueueSend(commandQueue,&line,0)==pdTRUE;
}
class CommandCallbacks:public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *characteristic) override {
        std::string value=characteristic->getValue();
        if(value.find('\0')!=std::string::npos) return;
        enqueue(String(value.c_str()));
    }
};
class ServerCallbacks:public BLEServerCallbacks {
    void onDisconnect(BLEServer *) override { BLEDevice::startAdvertising(); }
};
static const char PAGE[] PROGMEM=R"HTML(<!doctype html><meta charset="utf-8"><title>SmartFan</title>
<h1>智能风扇无线控制</h1><p>目标温度25–50°C；状态单位为0.01°C。命令是否生效以STM32回报为准。</p>
<button onclick="send('M,1')">自动</button><button onclick="send('M,0')">停机</button>
<button onclick="send('M,2')">手动</button><button onclick="send('R,0')">故障复位</button>
<p>目标°C <input id="s" type="number" min="25" max="50" value="35"><button onclick="send('S,'+Math.round(+document.querySelector('#s').value*100))">设置</button></p>
<p>手动速度% <input id="d" type="number" min="0" max="100" value="40"><button onclick="send('D,'+document.querySelector('#d').value)">设置</button></p>
<pre id="status"></pre><p id="ack"></p><script>async function send(c){let r=await fetch('/command',{method:'POST',body:c});document.querySelector('#ack').textContent=await r.text()}setInterval(async()=>{document.querySelector('#status').textContent=await(await fetch('/status')).text()},500)</script>)HTML";
void setup() {
    Serial.begin(115200); controllerUart.begin(115200,SERIAL_8N1,16,17);
    commandQueue=xQueueCreate(8,sizeof(CommandLine));
    if(!commandQueue) { Serial.println("FAIL COMMAND_QUEUE"); for(;;) delay(1000); }
    WiFi.mode(WIFI_AP); if(!WiFi.softAP(AP_NAME,AP_PASSWORD)) Serial.println("FAIL WIFI_AP");
    web.on("/",HTTP_GET,[]{web.send_P(200,"text/html; charset=utf-8",PAGE);});
    web.on("/status",HTTP_GET,[]{web.send(200,"text/plain",latest);});
    web.on("/command",HTTP_POST,[]{
        bool accepted=enqueue(web.arg("plain"));
        web.send(accepted?202:400,"text/plain",accepted?"QUEUED; await STM32 ACK/STATE":"INVALID_OR_QUEUE_FULL");
    }); web.begin();
    BLEDevice::init("SmartFan-BLE"); auto server=BLEDevice::createServer(); server->setCallbacks(new ServerCallbacks());
    auto service=server->createService(SERVICE);
    auto command=service->createCharacteristic(COMMAND,BLECharacteristic::PROPERTY_WRITE);
    command->setCallbacks(new CommandCallbacks());
    stateCharacteristic=service->createCharacteristic(STATUS_UUID,BLECharacteristic::PROPERTY_READ|BLECharacteristic::PROPERTY_NOTIFY);
    stateCharacteristic->addDescriptor(new BLE2902()); stateCharacteristic->setValue("WAITING");
    service->start(); BLEDevice::getAdvertising()->addServiceUUID(SERVICE); BLEDevice::startAdvertising();
    Serial.print("WIFI http://"); Serial.println(WiFi.softAPIP()); Serial.println("BLE SmartFan-BLE READY");
}
void loop() {
    web.handleClient(); CommandLine command;
    if(xQueueReceive(commandQueue,&command,0)==pdTRUE) { controllerUart.println(command.text); Serial.printf("TX %s\n",command.text); }
    static char line[100]; static unsigned used=0; static bool discard=false;
    while(controllerUart.available()) {
        char b=(char)controllerUart.read(); if(b=='\r') continue;
        if(b=='\n') {
            if(!discard) { line[used]=0; latest=line; Serial.println(line); stateCharacteristic->setValue(line); stateCharacteristic->notify(); }
            used=0; discard=false;
        } else if(used<sizeof(line)-1&&!discard) line[used++]=b;
        else discard=true;
    }
    delay(1);
}

