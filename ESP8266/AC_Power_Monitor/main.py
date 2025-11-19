import network
import machine
import time
import umail

# EMail configuration
# Email Configuration
SENDER_EMAIL = "mujeeb.automation@gmail.com"
SENDER_NAME = "Mujeeb Mohammad"
APP_PASSWORD = "edwiliwuwfyqrufq"  # The 16-character app password
#RECEIVER_EMAIL = "mohammad.mujeeb@gmail.com"
RECEIVER_EMAIL = "marghoob.hasan@gmail.com"
SMTP_SERVER = "smtp.gmail.com"  # Or your email provider's SMTP server
SMTP_PORT = 587  # Or your email provider's SMTP port (e.g., 465 for SSL)

# Function to Send an email
def send_email(subject, body):
    # Send the email
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
    smtp.login(SENDER_EMAIL, APP_PASSWORD)
    smtp.to(RECEIVER_EMAIL)
    smtp.write("From:" + SENDER_NAME + "<"+ SENDER_EMAIL+">\n")
    smtp.write("Subject:" + subject + "\n")
    smtp.write(body)
    smtp.send()
    smtp.quit()

# Connect to WiFi
sta_if = network.WLAN(network.WLAN.IF_STA)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('Ahmads', '03312018')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ipconfig('addr4'))

# Create an ADC object for the A0 pin
adc = machine.ADC(0)
isPowerGone = True
lastTimePoll = -1
lastTimeMaster = -1
highestValue = -1

while True:
    
    currentTime = time.ticks_ms()
    
    if currentTime - lastTimePoll > 50:    
        # Read the analog value
        analog_value = adc.read()
        
        if highestValue < analog_value:
            highestValue = analog_value
            
        lastTimePoll = currentTime
        
    if currentTime - lastTimeMaster > 2000:
        if not isPowerGone and highestValue <= 850:
            print("Power Gone")
            send_email("Power is Gone", "Power is Gone")
            isPowerGone = True
        
        if isPowerGone and highestValue > 850:
            print("Power Came Back")
            send_email("Power came Back", "Power came Back")
            isPowerGone = False
            
        highestValue = -1
        lastTimeMaster = currentTime


