<div align="center">

<pre>
 _______  _______  ______    _______  ___      ___      _______  ___            ___   _______  _______ 
|       ||   _   ||    _ |  |   _   ||   |    |   |    |       ||   |          |   | |       ||       |
|    _  ||  |_|  ||   | ||  |  |_|  ||   |    |   |    |    ___||   |          |   | |   _   ||  _____|
|   |_| ||       ||   |_||_ |       ||   |    |   |    |   |___ |   |          |   | |  | |  || |_____ 
|    ___||       ||    __  ||       ||   |___ |   |___ |    ___||   |___  ___  |   | |  |_|  ||_____  |
|   |    |   _   ||   |  | ||   _   ||       ||       ||   |___ |       ||   | |   | |       | _____| |
|___|    |__| |__||___|  |_||__| |__||_______||_______||_______||_______||___| |___| |_______||_______|

Fast, parallelized, and automated file deployment for remote devices.
tftp > [=======>file>--------] > devices
</pre>

</div>

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Parallel.IOS

A Python tool with a graphical user interface (GUI) developed to automate the copying and verification of IOS images (or other files) from a TFTP server to the flash memory of multiple Cisco devices. This script optimizes time and reduces manual work by performing simultaneous copies to various devices.

---

## Typical Scenario:

**Boss:**<br><br> We need to update the firmware version of all the company's network devices due to a critical vulnerability that was discovered last night!<br>
**🔴AND I NEED THIS READY BY 5 PM!!🔴**
<br><br><br>
**Infrastructure/Network Team (you, in this case!):<br><br>**<img src="/assets/CJ.jpg" alt="Screenshot 1" width="60%"> <br>*Oh shit! Here we go again!*

## The Problem:
You have 90 switches, a TFTP server, and the patience of a monk. What are you going to do? 😭 *<--is this you?*<br>
Copying files one by one manually isn't "infrastructure work," it's divine punishment. It's in these moments that you wonder if you should have studied botany or if you should have attended those acting classes.

## The Solution? (Or almost):
This tool is a Python script with a graphical interface that I made so you don't have to type `copy tftp flash:` until your fingers bleed.<br>
It automates the tedium and performs simultaneous uploads to multiple Cisco devices and then (*yes, there's more!*) after copying, it even checks if the file was copied correctly using its MD5 hash. (because life is too short to watch progress bars.)

## What does it do? (besides saving your time):

1. **Real Multitasking:** It attacks multiple devices at the same time. While TFTP struggles to make all the copies, you can pretend that you're reading the documentation (in reality you're doomscrooling on Instagram).

2. **Available space check:** Is it going to fit or not? Is there free space or not? It doesn't matter! You enter the file size, the script checks it for you, if there isn't enough space it warns you and doesn't start the copy.

3. **Integrity check (MD5 hash):** It checks if the file arrived intact or if it became a jumble of useless bits along the way.

4. **Graphical Interface:** Because sometimes we just want to click a pretty little button instead of fighting with the terminal.

## Compatibility

This script is compatible with Cisco **IOS/IOS-XE** and **NX-OS** (Nexus) devices. Just select the corresponding module (**Cisco IOS** or **Cisco NX-OS**) in the **Module** field of the "Advanced Config" section in the GUI before starting the transfer.

**Important!** You cannot mix IOS and NX-OS devices in the same run — every IP entered must match the type selected in the module. If a device of the wrong type is detected, the transfer to it will fail with an error telling you to switch modules, and the process will continue normally for the remaining devices. Other network operating systems (such as Junos, Arista EOS, etc.) are still **NOT** supported.

## Screenshots

<img src="/assets/screenshot-00.png" alt="Screenshot 1" width="85%">

<img src="/assets/screenshot-01.png" alt="Screenshot 1" width="85%"><br>

*Did you like the colors? Cool, right? Retro fashion is back in a big way.

## Prerequisites

To use this script, you will need:

1. **TFTP Server:** A **TFTP** server configured and operational on your network, accessible by the devices, and with the image (or file) you want to copy hosted on it. Recommended: [Tftpd64](https://pjo2.github.io/tftpd64/)
2. **Device Access:** Credentials (username and password) for SSH access to the devices.

3. **Coffee☕ and faith in UDP🙏**

## How to Use

### Prerequisites:
```bash
Python 3.x
```
### Running the beast:

1. **Download the Repository:**

```bash
git clone https://github.com/solopx/parallelios.git
cd parallelios
```
2. **Install the dependencies:**

```bash
pip install -r requirements.txt
```
3. **Run:**

```bash
python src/main.py
```

4. **Fill in the Information in the GUI:**

* **TFTP Server IP Address:** IP address of your TFTP server.

* **Filename:** Full name of the image/file on the TFTP server (e.g., `c2960s-universalk9-mz.152-7.E2.bin`).
* **MD5 Hash:** The expected MD5 hash value for the file (verify the file's MD5 hash using the commands: certutil, md5sum, or through official sources).

* **Size (MB):** Estimated file size in `Megabytes (MB)`. The size entered in this field will be used to check if there is available space on the destination devices before copying. `Note: If you input it as 0 or leave this field blank, the check will not be performed.`

* **Username:** Your username for authentication for the devices.

* **Password:** Your authentication password for the devices.

* **Enable Pass:** Check this box if the devices require an enable password and enter it. `Note: This option is automatically disabled when selecting the "Cisco NX-OS" module, since NX-OS doesn't use enable mode.`

* **Module:** Select the destination device type: **Cisco IOS** (default) or **Cisco NX-OS**.

* **Devices:** A list of IP addresses of the destination devices, separated by commas (e.g., `192.168.1.1, 192.168.1.2, 192.168.1.3`). 

5. **Start Copy(ies):** Click on the green magical **Start Transfer** button.

6. **Output Log:** The output log at the bottom of the window will show you the status of the process for each device in real time. (Cool, huh?)

7. **Have your coffee** and enjoy the beautiful view of your office while you wait for the process to finish.

## Notes: ##

### MD5 hash: ###

You can obtain the MD5 hash of the file to be copied from reliable sources such as official websites or by using the command line.

To check the MD5 hash of a file on `Windows` systems, use the following at the command prompt:
```bash
certutil -hashfile "C:\Path\To\Desired\File.bin" MD5
```
For `Linux/Unix` systems, use:
```bash
md5sum "C:\Path\To\Desired\File.bin"
```

### TFTP Packet Size: ###

In some iOS versions, the TFTP packet size can be customized to optimize copy time. You can check if your devices have this functionality with the command:

```bash
Switch(config)# ip tftp blocksize <value>
```

Valid values ​​are between 512 (default) and 8192.

## Troubleshooting and Debug Logs

The script generates a log file called `copy-tftp-flash.log` at the root directory. This file contains low-level details of interactions with devices and is extremely useful for debugging.

## Notes on `MAX_WORKERS` and `TIMEOUT_MAX` ##

The `MAX_WORKERS` field defines the maximum number of simultaneous copy operations. The default value is `5`. If you are processing a large number of devices and have a robust network infrastructure and a capable TFTP server, you can adjust this value to increase the number of simultaneous transfers and performance. Keep in mind, however, that a very high value can overload your resources.

The `TRANSFER TIMEOUT` field defines the maximum time (in minutes) that the script will wait to transfer the file to each device.

## File Structure

This application is currently divided into the following main files:

* `main.py` - Application entry point. Connects the graphical interface to the network logic, manages input validations, and routes execution to the correct transfer engine (IOS or NX-OS) based on the selected module.

* `gui.py` - Graphical interface in Tkinter. Defines the layout, visual styles, and exposes the widgets for the main to orchestrate.

* `engine_core.py` - Shared functions and state used by both transfer engines: IP validation, disk space check, logging, and parallel transfer orchestration (`ThreadPoolExecutor`).

* `ios_engine.py` - Transfer engine specific to Cisco IOS/IOS-XE devices (`flash:` filesystem, `verify /md5` command, enable mode).

* `nxos_engine.py` - Transfer engine specific to Cisco NX-OS devices (`bootflash:` filesystem, `show file ... md5sum` command, no enable mode).

## Future

In future updates, I intend to add some relaxing elevator music while the copies are being made and a truck horn sound when they are completed. I also intend to add support for other manufacturers and the SCP/SFTP protocol as an alternative to TFTP.

## Contributions

Contributions are welcome! If you have ideas for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

Developed by solopx
GitHub: [https://github.com/solopx/](https://github.com/solopx/)