"""
The power optimization algorithm is not a pure python program, it have a few shell script lines to perform certain
OS specific tasks. It's usage in any other application will not however require knowledge of shell scripting.
A basic knowledge of python programming is sufficient.

This script rely on the rfkill program that comes installed in some Raspberry Pi models. If the one in question does
not have it installed, please connect to the Internet before running this script for the first time as it will attempt
to install it. You can still install it manually using the "sudo apt-get install rfkill" bash command.

Author: Stephen Tipa Augustine
Date: 30/07/2022
"""
import subprocess
import os


class PowerOptimizer:

    def __init__(self, **kwargs):
        # Initializing properties
        self.kwargs = kwargs
        self.backup_config = None
        self.enable_ssh = None
        self.enable_hdmi = None
        self.enable_wifi = None
        self.enable_bluetooth = None
        self.enable_usb = None
        self.enable_onboard_led = None
        self.enable_ethernet = None
        self.kwarg_processor()

        # Validating program requirements
        self.validate_requirements()

        # Creating backup for the config.txt file
        if self.backup_config:
            self.create_config_backup()
        # Enabling ssh at boot
        if self.enable_ssh:
            self.setup_ssh_at_boot()

        self.hdmi_controller(enable=self.enable_hdmi)
        self.wifi_controller(enable=self.enable_wifi)
        self.bluetooth_controller(enable=self.enable_bluetooth)
        self.usb_controller(enable=self.enable_usb)
        self.onboard_led(enable=self.enable_onboard_led)
        self.ethernet_port(enable=self.enable_ethernet)

    def kwarg_processor(self):
        """
        This function processes the kwarg argument of the __init__ method.
        it should be called before any other methods that uses the properties below.
        :return: None
        """
        for key, value in self.kwargs.items():
            if key == 'backup_config':
                self.backup_config = value
            elif key == 'enable_ssh':
                self.enable_ssh = value
            elif key == 'enable_hdmi':
                self.enable_hdmi = value
            elif key == 'enable_wifi':
                self.enable_wifi = value
            elif key == 'enable_bluetooth':
                self.enable_bluetooth = value
            elif key == 'enable_usb':
                self.enable_usb = value
            elif key == 'enable_onboard_led':
                self.enable_onboard_led = value
            elif key == 'enable_ethernet':
                self.enable_ethernet = value

    @staticmethod
    def validate_requirements():
        """
        This method check if rfkill is installed in the system, if it is not it then installs it.
        This tool is used for managing the radio communication (WIFI and BLUETOOTH)
        :return: str
        """
        rfkill = os.system('command -v rfkill')
        if rfkill != 0:
            subprocess.run(['sudo', 'apt-get', 'update', '&&', 'sudo', 'apt-get', 'install', 'rfkill'])
        else:
            print('rfkill command found in the system')
        uhubctl = os.system('command -v uhubctl')
        if uhubctl != 0:
            subprocess.run(
                ['sudo', 'apt-get', 'update', '&&', 'sudo', 'apt-get', 'install libusb-1.0-0-dev', 'uhubctl'])
        return 'Validated'

    @staticmethod
    def create_config_backup():
        """
        This static method checks if the backup of the config.txt file has already been created.
        If not, it creates on and returns the path of the file.
        :return: str
        """
        if not os.path.exists('/boot/backupconfig.txt'):
            subprocess.run(['sudo', 'cp', '/boot/config.txt', '/boot/backupconfig.txt'])
        return '/boot/backupconfig.txt'

    @staticmethod
    def setup_ssh_at_boot():
        """
        Checks to see if ssh has been enabled at boot, if not it enables it at boot.
        For changes to take effect, a reboot is necessary. It returns path to the ssh file.
        :return: str
        """
        if not os.path.exists('/boot/ssh'):
            subprocess.run(['sudo', 'touch', '/boot/ssh'])
        return '/boot/ssh'

    @staticmethod
    def hdmi_controller(enable=True):
        """
        Enables or disables the hdmi controller
        :param enable: boolean
        :return: int
        """
        if enable:
            hdmi = subprocess.run(['sudo', '/opt/vc/bin/tvservice', '-p'])
        else:
            hdmi = subprocess.run(['sudo', '/opt/vc/bin/tvservice', '-o'])
        return hdmi.returncode

    @staticmethod
    def edit_config_file(clock, key, reset):
        """
        Manipulates the boot config file, reading and editing it.
        :param clock: int
        :param key: str
        :param reset: boolean
        :return: None
        """
        file_obj = open('/boot/config.txt', 'r')
        lines = file_obj.readlines()
        desire_line = None
        for i in lines:
            if (key + '=') in i:
                desire_line = i
        if desire_line is not None:
            if reset:
                lines.remove(desire_line)
            else:
                index = lines.index(desire_line)
                lines[index] = key + '=' + str(clock)
        else:
            lines.append('\n' + key + '=' + str(clock))

        file_obj = open('/boot/config.txt', 'w')
        file_obj.writelines(lines)
        file_obj.close()

    def ram_clock(self, clock=100, reset=False):
        self.edit_config_file(clock, 'sdram', reset)

    def gpu_clock(self, reset=False, clock=100):
        self.edit_config_file(clock, 'gpu', reset)

    def cpu_clock(self, reset=False, clock=100):
        self.edit_config_file(clock, 'arm_freq', reset)
        self.edit_config_file(clock, 'arm_freq_max', reset)

    @staticmethod
    def ethernet_port(enable=True):
        if enable:
            subprocess.run(['sudo', 'ifconfig', 'eth0', 'up'])
        else:
            subprocess.run(['sudo', 'ifconfig', 'eth0', 'down'])

    @staticmethod
    def bluetooth_controller(enable=True):
        """
        Enables or disables the bluetooth controller.
        :param enable: boolean
        :return: int
        """
        if enable:
            bt = subprocess.run(['sudo', 'rfkill', 'unblock', 'bluetooth'])
        else:
            bt = subprocess.run(['sudo', 'rfkill', 'block', 'bluetooth'])
        return bt.returncode

    @staticmethod
    def wifi_controller(enable=True):
        """
        Enables or disables the wifi controller.
        :param enable: boolean
        :return: int
        """
        if enable:
            wifi = subprocess.run(['sudo', 'rfkill', 'unblock', 'wifi'])
        else:
            wifi = subprocess.run(['sudo', 'rfkill', 'block', 'wifi'])
        return wifi.returncode

    @staticmethod
    def usb_controller(enable=True):
        """
        Enables or disables the usb controller.
        :param enable: boolean
        :return: int
        """
        if enable:
            subprocess.run(['sudo', 'uhubctl', '-a', 'on'])
        else:
            subprocess.run(['sudo', 'uhubctl', '-a', 'off'])

    @staticmethod
    def onboard_led(enable=True):
        """
        Enables or disables the onboard LEDs. This includes the power, active and ethernet LEDs.
        NOTE: Some models of the raspberry pi do not have support for disabling the power LED
        :param enable: boolean
        :return: None
        """
        if enable:
            subprocess.run(['echo', '1', '|','sudo','tee', '/sys/class/leds/led0/brightness', '>','/dev/null', '&&',
                            'echo', '1', '|', 'sudo', 'tee', '/sys/class/leds/led1/brightness', '>', '/dev/null'])
        else:
            subprocess.run(['echo', '0', '|', 'sudo', 'tee', '/sys/class/leds/led0/brightness', '>', '/dev/null', '&&',
                            'echo', '0', '|', 'sudo', 'tee', '/sys/class/leds/led1/brightness', '>', '/dev/null'])


if __name__ == '__main__':
    # A sample of the kwarg argument for instantiating the PowerOptimizer class
    while True:
        hdmi = int(input("Hdmi enabler:"))  # 1 for True and 0 for False
        wifi = int(input("Wifi enabler:"))
        bluetooth = int(input("Bluetooth enabler:"))
        usb = int(input("Usb enabler:"))
        led = int(input("Led enabler:"))
        cpu_clock = int(input("Cpu clock:"))  # e.g 100
        gpu_clock = int(input("Gpu clock:"))  # e.g 100
        ram_clock = int(input("Ram clock:"))  # e.g 100
        kwarg = {'backup_config': True, 'enable_ssh': True, 'enable_hdmi': hdmi == 1, 'enable_wifi': wifi == 1,
                 'enable_bluetooth': bluetooth == 1, 'enable_usb': usb == 1, 'enable_onboard_led': led == 1}
        obj = PowerOptimizer(**kwarg)
        obj.cpu_clock(clock=cpu_clock)  # 100 - 800
        obj.gpu_clock(clock=gpu_clock)
        obj.ram_clock(clock=ram_clock)
