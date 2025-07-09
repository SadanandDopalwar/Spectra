import pyautogui
import pyperclip
import time
import socket
import sys
import uuid
import asyncio
import json
import coloredlogs
import logging
from logging.handlers import RotatingFileHandler
from threading import Thread
import subprocess


is_connected = False
client_socket = None  # Initial socket state
file_path = 'C:\\Users\\Public\\Desktop\\settings.json'

# Read the settings from the specified JSON file
with open(file_path, 'r') as f:
    settings = json.load(f)
SERVER_IP = settings.get("cameraip")
SERVER_PORT = settings.get("cameraport")
pastedelay = settings.get("pastedelay")
x = settings.get("xcordinate")
y = settings.get("ycordinate")
userx = settings.get("userx")
usery = settings.get("usery")
SocketTimeout = settings.get("SocketTimeout")
coordinatingenabled = settings.get("coordinatingenabled")
IsUserLogin = settings.get("IsUserLogin")
UserPrefix = settings.get("UserPrefix")
BarcodePosition = settings.get("barcodeposition")
log_file_path = settings['logsettings']['log_file_path']
logsize = settings['logsettings']['logsize']
logscount = settings['logsettings']['logscount']

userbarcode = []

def logging_handler(log_file_path, logsize, logscount):
    logger = logging.getLogger(__name__)
    coloredlogs.install(
        level='DEBUG',
        logger=logger,
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        milliseconds=True,  # Include milliseconds in asctime
        level_styles={
            'debug': {'color': 'blue'},
            'info': {'color': 'white', 'intensity': 'bold'},
            'warning': {'color': 'green'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True}
        },
        field_styles={
            'asctime': {'color': 'cyan'},
            'hostname': {'color': 'cyan'},
            'levelname': {'color': 'blue', 'bold': True}
        }
    )

    file_handler = RotatingFileHandler(log_file_path, maxBytes=logsize*1024*1024, backupCount=logscount)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    return logger

logger = logging_handler(log_file_path, logsize, logscount)





async def ping(host):
    try:
        # Use the subprocess.run method to execute the ping command ["ping", "-c", "1", host]
        result = subprocess.run(
            ["ping", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Ensures output is returned as a string
            check=True,  # Raises CalledProcessError if the command fails
        )
        #logger.info(result)
        # Return True if the exit code is 0 (success)
        return result.returncode == 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


async def UserLoginCase(userbarcode, uid):
    UserId = userbarcode[1]
    Password = userbarcode[2]
    await asyncio.sleep(pastedelay)
    current_position = pyautogui.position()
    logger.info("Current cursor Position for UID: %s, %s", current_position, uid)
    logger.info("Started Coordinates Disabled Event for UID %s", uid)
    pyautogui.click()
    
    
            
            # Copy the data to clipboard
    pyperclip.copy(UserId)
    logger.info("Copied barcode data to clipboard for UID: %s, %s", UserId, uid)
            
            # Paste data
    pyautogui.hotkey('ctrl', 'v')  # Use 'command' instead of 'ctrl' on macOS
            
            # Press enter
    pyautogui.press('tab')

    pyperclip.copy(Password)
    logger.info("Copied barcode data to clipboard for UID: %s, %s", Password, uid)
            
            # Paste data
    pyautogui.hotkey('ctrl', 'v')  # Use 'command' instead of 'ctrl' on macOS
            
            # Press enter
    pyautogui.press('enter')
    logger.info("User data processed successfully for UID: %s", uid)
    





async def paste_on_focus(barcode_data, barcode_received, uid):
    if not barcode_data or (barcode_received.startswith((UserPrefix))):
        logger.warning("Barcode data is None or blank.")
        return  # Ignore if barcode_data is None or blank
    await asyncio.sleep(pastedelay)
    
    # Log current position of the cursor
    current_position = pyautogui.position()
    logger.info("Current cursor Position for UID: %s, %s", current_position, uid)
    
    
    # Move to the specified coordinates
    if coordinatingenabled:
        logger.info("Started Coordinates Enabled Event for UID: %s", uid)
        logger.info("Moving cursor to coordinates for UID: %s, %s, %s", x, y, uid)
        pyautogui.moveTo(x, y, duration=1)  # Adding a duration for smooth movement
        
        # Adding a small delay to ensure cursor has moved
        await asyncio.sleep(0.05)
        
        # Log new position of the cursor
        new_position = pyautogui.position()
        logger.info("New cursor position for UID: %s, %s", new_position, uid)
        
        # Ensure the cursor is at the new position before clicking
        if new_position == (x, y):
            # Click at the specified coordinates
            pyautogui.click()
            
            # Copy the data to clipboard
            pyperclip.copy(barcode_data)
            logger.info("Copied barcode data to clipboard for UID: %s, %s", barcode_data, uid)
            
            # Paste data
            pyautogui.hotkey('ctrl', 'v')  # Use 'command' instead of 'ctrl' on macOS
            
            # Press enter
            pyautogui.press('enter')
            logger.info("Barcode data processed successfully for UID: %s", uid)
        else:
            logger.error("Cursor did not move to the correct position for UID: %s", uid)

    else:
        logger.info("Started Coordinates Disabled Event for UID %s", uid)
        pyautogui.click()
            
        # Copy the data to clipboard
        pyperclip.copy(barcode_data)
        logger.info("Copied barcode data to clipboard for UID: %s, %s", barcode_data, uid)
            
        # Paste data
        pyautogui.hotkey('ctrl', 'v')  # Use 'command' instead of 'ctrl' on macOS
        
        # Press enter
        pyautogui.press('enter')
        logger.info("Barcode data processed successfully for UID: %s", uid)



async def main(client_socket, is_connected):  
    global userbarcode   
    client_socket.settimeout(SocketTimeout)
    while is_connected:
        try:
            data = client_socket.recv(1024)
            # Decode and print the received data
            if not data:  # Check if the connection is closed
                logger.info("Connection closed by PLC.")
                is_connected = False
                break
            logger.info("Received Data: %s", data)
            barcode_received = data.decode().strip()
            barcode_array = barcode_received.split(',')
            
            uid = str(uuid.uuid1())
            if IsUserLogin == True and barcode_received.startswith((UserPrefix)):
                userbarcode.append(barcode_array[0])
            elif len(userbarcode) == 1:
                userbarcode.append(barcode_array[0])
                logger.info("Captured second barcode: %s", barcode_received)

            elif len(userbarcode) == 2:
                userbarcode.append(barcode_array[0])
                logger.info("Captured third barcode: %s", barcode_array[0])
                logger.info("All user barcodes collected: %s", userbarcode)

                # Call your function after collecting all three barcodes
                await UserLoginCase(userbarcode, uid)

                # Reset for the next USER sequence
                userbarcode = []
            else:               
                #barcode_data = ']d1,5|\MS11198820895|O|FRK/GGN|S|O|03|P|S|F|78,]C0,SF103'
                barcode_data = barcode_array[BarcodePosition]
                logger.info("Decoded Barcode for UID: %s, %s", barcode_data, uid)
                await paste_on_focus(barcode_data, barcode_received, uid)

        except socket.timeout:
            logger.warning("Socket timeout, attempting to continue...")
            continue  # Continue loop on timeout

        except socket.error as e:
            logger.error("Connection error: %s", e)
            is_connected = False
            break  # Exit the loop on a connection error


async def connect_barcode(SERVER_IP, SERVER_PORT):
    global client_socket, is_connected
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        logger.info(f"Connected to {SERVER_IP}:{SERVER_PORT}")
        is_connected = True
        Thread(target=lambda: asyncio.run(main(client_socket, is_connected))).start()   
        return client_socket, is_connected
    except socket.error as e:
        logger.error(f"Failed to connect to {SERVER_IP}:{SERVER_PORT}: {e}")
        is_connected = False
        Thread(target=lambda: asyncio.run(main(client_socket, is_connected))).start() 
        return None, False

async def monitor_connection():
    global client_socket, is_connected
    while True:
        if is_connected:
            # If connected, just monitor by pinging the IP
            if not await ping(SERVER_IP):
                logger.warning(f"Connection to {SERVER_IP} lost, closing socket...")
                client_socket.close()
                client_socket = None
                is_connected = False
            else:
                logger.info(f"Connection to {SERVER_IP} is healthy")
        else:
            # If not connected, attempt to reconnect
            logger.info(f"Attempting to reconnect to {SERVER_IP}:{SERVER_PORT}...")
            client_socket, is_connected = await connect_barcode(SERVER_IP, SERVER_PORT)
            if not is_connected:
                logger.info(f"Waiting before retrying...")
                await asyncio.sleep(0.1)  # Wait before next reconnection attempt
            else:
                logger.info(f"Successfully reconnected to {SERVER_IP}:{SERVER_PORT}")
        
        await asyncio.sleep(2)  # Check connection every 2 seconds


asyncio.run(monitor_connection())
