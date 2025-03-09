# RotKey: Client-Initiated Dynamic Session Key Rotation Browser Extension Tool

## Description

RotKey is a novel browser extension solution that enhances session security by generating session keys on the client side and dynamically rotating them at regular intervals.

## Getting Started

### Dependencies

* Google Chrome Browser
* Server Dependencies:
  - Python 3.12.3
  - Flask
  - Cryptography library (pip install cryptography)
  - MySQL
  - Nginx
  - Gunicorn

### Installing

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/lewlipop/RotKey.git
   cd RotKey
   
2. **Navigate to Extensions**:
   In the address bar, type `chrome://extensions/` and press Enter. This will open the Extensions page.

3. **Enable Developer Mode**:
   In the top right corner of the Extensions page, toggle the **Developer mode** switch to the **ON** position.

4. **Load Unpacked Extension**:
   Once Developer Mode is enabled, click the **Load unpacked** button.

5. **Select Extension Directory**:
   A file dialog will appear. Navigate to the folder RotKey_Symmetric_Key where the RotKey extension files (e.g., `manifest.json`, `background.js`, etc.) are located and select the directory.

6. **Verify the Extension**:
   After selecting the directory, the extension will be loaded into Chrome. You should see your extension listed on the Extensions page with an option to enable/disable it.

### Using the Extension

1. **Enable the extension**:
   - Toggle to enable the extension.

2. **Click on the RotKey Extension Icon**:
   - In Chrome, locate the **RotKey** extension icon in the toolbar (usually in the top-right corner of the browser).
   - Click the **RotKey** icon to open the extension's popup window.

3. **Start Rotation**:
   - In the popup window, click the **"Start Rotation"** button.
   - This action will trigger the following:
     - A new **256-bit symmetric key** will be generated.
     - The server will be updated via the `/update-key` endpoint with the new key.
     - A **countdown timer** for 5 mimnutes will start for the next key rotation.

4. **Monitor the Countdown**:
   - Once the key rotation begins, the countdown timer will indicate the time remaining before the next key rotation.
   - The extension will automatically update the key at regular intervals as configured.

## Notes
- You may need to be authenticated or have the proper server access for the key rotation process to be successful.
- The extension will notify you if there are any issues or errors during the key update process.
  
## Troubleshooting
- If the **"Start Rotation"** button does not work, ensure the extension has the correct permissions and that the server is accessible.
- If the countdown timer is not starting, verify that the extension is properly connected to the server and the `/update-key` endpoint is functioning.

### Using RotKey on Test Webpage

Our team has created a website for you to test RotKey on. The website is **https://p2bg4rotkey-ict2214.zapto.org/index.php**. 
- There are a total of 3 pages created - Home (index.php), Login (login.php) and Register (register.php).
- You can navigate among these web pages and attempt to **perform registration and login with RotKey running**.

### Checking of RotKey Status on Test Webpage

Our test webpage allows you to check for the presence of RotKey with the **"Check RotKey Status"** button. This function check for RotKey under three conditions. 

1. If RotKey extension is **not loaded into the browser**, a Windows alert box will reflect **"RotKey Extension is Not installed!"**. 
2. If RotKey extension is **loaded but not yet enabled**, the Windows alert box will reflect **"RotKey is Not Enabled Yet!"**.
3. If RotKey extension is **loaded and enabled**, the Windows alert will reflect **"RotKey Synced!"**.

## Help
If you encounter any issues with the **RotKey** extension, follow these troubleshooting steps:

## Extension Errors
If the extension isn't working as expected, follow these steps to check for errors:

1. **Open Chrome Developer Tools**:
   - Press `F12` or right-click anywhere on the page and select **Inspect**.
   - In the Developer Tools window, go to the **Console** tab for logs.
   - For background page logs, navigate to `chrome://extensions/`, locate the **RotKey** extension, and click **Inspect** under the "Inspect views" section.

2. **Check for Errors**:
   - Look for any error messages related to the extension's background script or popup.

## Server Errors
### Disclaimer: 
- The server is only valid till **the end of April 2025**.
- For easy reference, the back end server source code in the /flaskapp and /html folder are copied over to the repository. It is recommended to login to the server
for better context and understanding.

If there are issues on the server side (e.g., key updates or decryption failures), follow these steps:

1. **Access the Server via SSH**:
   - IP: 23.102.235.79
   - Username: ict2214P2BG4
   - Password: rotKey1$th3b35t

3. **Disable Gunicorn running on server**
   - Disable Gunicorn to stop the flask from running in production with the command
     ```bash
     systemctl stop gunicorn 

4. **Check Flask Server Console Output**:
   - Navigate to app.py at the /var/www/flaskapp directory with the command
     ```bash
     cd /var/www/flaskapp
   - Uncomment the code 
     ```bash
      if __name__ == "__main__":
         app.run(host="0.0.0.0", port=5000, debug=True)
    
   - after that, run the command to run Flask in debugging mode
     ```bash
     python3 app.py

   - Review the console output of your Flask server for any error messages related to key decryption or updates.
   - Common errors might include missing keys, incorrect endpoints, or failed key update attempts.
  
5. **Enable Gunicorn again to run on server**
   - Once the issues have been resolved, comment out the code in app.py
     ```bash
     #if __name__ == "__main__":
     #    app.run(host="0.0.0.0", port=5000, debug=True)
     
   - Enable Gunicorn again to run flask in production.
     ```bash
     systemctl start gunicorn

## Authors

1. Mervin
2. Lewis
3. Damian
4. Gin Young
5. Sean
