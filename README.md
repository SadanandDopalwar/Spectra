# Spectra
Spectra automates repetitive barcode input tasks in a Warehouse Management System (WMS) using desktop automation, clipboard handling, and socket communication.
This reduces manual entry mistakes, boosts processing speed, and improves warehouse efficiency.

✅ Key Features

🖱️ Automates cursor movements and keyboard input using pyautogui.

📋 Uses pyperclip for fast and reliable clipboard operations.

🌐 Communicates with external devices (e.g., cameras, scanners) via sockets.

🗂️ Customizable coordinates for cursor positioning.

⏱️ Configurable input delays for stable automation.

🔒 Supports user login checks with unique prefixes.

📑 Built-in rotating log file to track actions and errors.


⚙️ How It Works
1️⃣ Spectra listens for barcode input tasks or reads them from a source.
2️⃣ It uses pyautogui to control mouse and keyboard input to paste barcodes at specific screen coordinates.
3️⃣ Clipboard operations are handled via pyperclip for speed and reliability.
4️⃣ Sockets are used to interact with hardware (e.g., external cameras/scanners).
5️⃣ All events, actions, and errors are logged with coloredlogs and a rotating log file to prevent large log files from filling up storage.



