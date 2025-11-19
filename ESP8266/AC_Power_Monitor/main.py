import os
import network
import machine
import time
import umail
import socket

# File System configuration
def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    
if not file_exists('data.txt'):
    f = open('data.txt', 'w')
    f.write('mohammad.mujeeb@gmail.com,marghoob.hasan@gmail.com')
    f.close()
else:
    f = open('data.txt', 'r')
    toEmailAddresses = f.read().split(",")
    print(toEmailAddresses)
    f.close()
    
# Email Configuration
SENDER_EMAIL = "mujeeb.automation@gmail.com"
SENDER_NAME = "Informer"
APP_PASSWORD = "edwiliwuwfyqrufq"  # The 16-character app password
SMTP_SERVER = "smtp.gmail.com"  # Or your email provider's SMTP server
SMTP_PORT = 587  # Or your email provider's SMTP port (e.g., 465 for SSL)

# Connect to WiFi
sta_if = network.WLAN(network.WLAN.IF_STA)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('Ahmads', '03312018')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ipconfig('addr4'))

# Web Server Configuration
html = """<!DOCTYPE html>
<html>
    <head>
        <title>AC Power Monitor</title>
        <style>
            table {
              width: 100%;
              border-collapse: collapse; /* Optional: collapses borders between cells */
            }

            th, td {
              border: 1px solid black;
              padding: 10px; /* Adds 10px padding inside each cell */
              text-align: left; /* Optional: aligns text to the left */
            }
        </style>
    </head>
    <body> <h1>AC Power Monitor</h1>
        <table> <tr><th>Receiver's Email Address(es)</th></tr>
        <tr>
            <td>
                <center>
                    <form method=GET action="/">
                        <input type="text" value="%s" name="emails" length="300" size="200">
                        <br><br>
                        <input type="Submit" value=" Save ">
                    </form>
                </center>
            </td>
        </tr>
        </table>
    </body>
</html>
"""
import socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

# Function to Send an email
def send_email(subject, body):
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
    smtp.login(SENDER_EMAIL, APP_PASSWORD)
    
    for email in toEmailAddresses:
        # Send the email
        print('Sending email to ' + email)
        smtp.to(email)
        smtp.write("From:" + SENDER_NAME + "<"+ SENDER_EMAIL+">\n")
        smtp.write("Subject:" + subject + "\n")
        smtp.write(body)
        smtp.send()
    smtp.quit()

def get_formatted_time():
    now = time.localtime()
    formatted_specific_time = "{}/{}/{} {}:{}".format(now[1], now[2], now[0], now[3], now[4])
    return formatted_specific_time
    
# Create an ADC object for the A0 pin
adc = machine.ADC(0)
isPowerGone = True
highestValue = -1
sampleCount = 0

def pollingCallback(timer):
    global analog_value, adc, highestValue, sampleCount, isPowerGone
    
    # Read the analog value
    analog_value = adc.read()
        
    if highestValue < analog_value:
        highestValue = analog_value
        
    sampleCount = sampleCount + 1
        
    if sampleCount  > 50:
        if not isPowerGone and highestValue <= 900:
            print("Power Gone (Highest Value: ", highestValue, ")")
            text = "Power is Gone at " + get_formatted_time()
            send_email(text, text)
            isPowerGone = True
        
        if isPowerGone and highestValue > 900:
            print("Power Came Back (Highest Value: ", highestValue, ")")
            text = "Power came Back at " + get_formatted_time()
            send_email(text, text)
            isPowerGone = False
            
        highestValue = -1
        sampleCount = 0

timer = machine.Timer(3)
timer.init(mode=machine.Timer.PERIODIC, period=20, callback=pollingCallback)

# Web Server
while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    value = ",".join(toEmailAddresses)
    response = html.replace('%s', value)
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()

