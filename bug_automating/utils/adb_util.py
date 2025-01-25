import logging
import re
import subprocess
import os
import time

from bug_automating.pipelines.placeholder import Placeholder


class ADBUtil:
    # Set the full path to the adb executable
    ADB_PATH = os.path.expanduser("/usr/local/bin/adb")

    @staticmethod
    def run_adb_command(command):
        command.insert(0, ADBUtil.ADB_PATH)
        try:
            print(f"Running command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            print(f"Output: {e.output}")
            return None

    @staticmethod
    def check_adb_connection():
        command = ['devices']
        output = ADBUtil.run_adb_command(command)
        if output:
            print("ADB Devices:\n", output)
            if "device" in output:
                return True
            elif "unauthorized" in output:
                print("Device unauthorized. Please check the device screen for authorization request.")
                return False
            else:
                print("No devices/emulators found.")
        return False

    @staticmethod
    def get_all_packages():
        command = ['shell', 'pm', 'list', 'packages']
        output = ADBUtil.run_adb_command(command)
        if output:
            packages = output.strip().split('\n')
            packages = [pkg.split(":")[1] for pkg in packages]  # Remove the "package:" prefix
            return packages
        return []

    @staticmethod
    def find_package_by_keyword(keyword):
        packages = ADBUtil.get_all_packages()
        matching_packages = [pkg for pkg in packages if keyword in pkg]
        return matching_packages

    @staticmethod
    def get_main_activity(package_name):
        command = ['shell', 'cmd', 'package', 'resolve-activity', '--brief', package_name]
        output = ADBUtil.run_adb_command(command)
        if output:
            # The output will be in the form of "package_name/activity_name"
            return output.split("/")[-1]
        return None

    @staticmethod
    def launch_app(package_name, activity_name):
        command = ['shell', 'am', 'start', '-n', f'{package_name}/{activity_name}']
        output = ADBUtil.run_adb_command(command)
        if output:
            print("Launch app output:\n", output)

    @staticmethod
    def close_app(package_name):
        command = ['shell', 'am', 'force-stop', f'{package_name}']
        output = ADBUtil.run_adb_command(command)
        if output:
            print("Close app output:\n", output)

    @staticmethod
    def tap_screen(x, y):
        command = ['shell', 'input', 'tap', str(x), str(y)]
        output = ADBUtil.run_adb_command(command)
        if output:
            print(f"Tapped at ({x}, {y})")

    @staticmethod
    def capture_screenshot(save_path):
        """
        take screenshot by using the adb command
        if error:
             adb emu screenrecord screenshot [destination-directory]
             take screenshot by using the adb command for clicking "take screenshot" button in command line
             https://developer.android.com/studio/run/emulator-take-screenshots
        alternative ways:
            1. adb emu kill
               kill the emulator, then it will save a snapshot,
               a screenshot in /Users/<username>/.android/avd/<emulator_name>.avd/snapshots/default_boot
            2. adb emu avd snapshot save <my_snapshot>
               save a snapshot of current status, e.g., <emulator_name> = Pixel_8_API_34_2
               a screenshot in /Users/<username>/.android/avd/<emulator_name>.avd/snapshots/<my_snapshot>
        """
        result = ADBUtil.run_adb_command(['shell', 'screencap', '/sdcard/screen.png'])
        ADBUtil.run_adb_command(['pull', '/sdcard/screen.png', save_path])
        ADBUtil.run_adb_command(['shell', 'rm', '/sdcard/screen.png'])
        if result is None:
            ADBUtil.run_adb_command(['emu', 'screenrecord', 'screenshot', save_path])

    @staticmethod
    def capture_screenshot_by_take_screenshot_button(save_path):
        """
        adb emu screenrecord screenshot [destination-directory]
        take screenshot by using the adb command for clicking "take screenshot" button in command line
        https://developer.android.com/studio/run/emulator-take-screenshots
        """
        ADBUtil.run_adb_command(['emu', 'screenrecord', 'screenshot', save_path])

    @staticmethod
    def back():
        command = ['shell', 'input', 'keyevent', '4']
        output = ADBUtil.run_adb_command(command)
        if output:
            print("Back button pressed")

    @staticmethod
    def double_tap(x, y):
        ADBUtil.tap_screen(x, y)
        ADBUtil.tap_screen(x, y)
        print(f"Double clicked at ({x}, {y})")

    @staticmethod
    def input_text(x, y, text=''):
        # First, tap on the specified coordinates
        tap_command = ['shell', 'input', 'tap', str(x), str(y)]
        ADBUtil.run_adb_command(tap_command)
        # event_type = 'text'
        # input_text = None
        # for char in text:
        #     if char == ' ':
        #         event_type = 'keyevent'
        #         input_text = "62"  # Space key
        #     elif char == '<':
        #         event_type = 'text'
        #         input_text = "%3C"  # Less than key
        #     elif char == '>':
        #         event_type = 'text'
        #         input_text = "%3E"  # Greater than key
        #     else:
        #         event_type = 'text'
        #         input_text = char
        #     # Then, input the text
        #     text_command = ['shell', 'input', event_type, input_text]
        #     # ADBUtil.run_adb_command(text_command)
        #     output = ADBUtil.run_adb_command(text_command)
        #     if output:
        #         print(f"Input text: {text}")

        special_chars = {
            ' ': '%s',
            # '<': '%3C',
            # '>': '%3E'
        }
        encoded_text = ''.join(special_chars.get(c, c) for c in text)

        # Then, input the text
        text_command = ['shell', 'input', 'text', encoded_text]
        output = ADBUtil.run_adb_command(text_command)
        if output:
            print(f"Input text: {text}")

    @staticmethod
    def long_tap(x, y, duration=2000):
        command = ['shell', 'input', 'swipe', str(x), str(y), str(x), str(y), str(duration)]
        output = ADBUtil.run_adb_command(command)
        if output:
            print(f"Long clicked at ({x}, {y}) for {duration}ms")

    @staticmethod
    def get_screen_size():
        output = ADBUtil.run_adb_command(['shell', 'wm', 'size'])
        if output:
            # Extract the screen size from the output
            size_str = output.split(":")[1].strip()
            width, height = map(int, size_str.split("x"))
            return width, height
        else:
            raise RuntimeError("Failed to get screen size.")

    @staticmethod
    def get_screen_orientation():
        """
        Gets the current screen orientation of the device.

        Returns:
            int: Orientation value (0: Portrait, 1: Landscape, 2: Reverse Portrait, 3: Reverse Landscape)
        """
        output = ADBUtil.run_adb_command(['shell', 'settings', 'get', 'system', 'user_rotation'])
        return int(output)

    @staticmethod
    def scroll(start_x, start_y, end_x, end_y, duration=1000):
        command = ['shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y), str(duration)]
        output = ADBUtil.run_adb_command(command)
        if output:
            print(f"Scrolled from ({start_x}, {start_y}) to ({end_x}, {end_y}) over {duration}ms")

    @staticmethod
    def scroll_with_coordinate_or_direction(coordinate=None, direction='down', duration=1000):
        screen_width, screen_height = ADBUtil.get_screen_size()
        orientation = ADBUtil.get_screen_orientation()
        print(orientation)
        if orientation == 1 or orientation == 3:  # Landscape or Reverse Landscape mode
            screen_width, screen_height = screen_height, screen_width

        half_screen_width = screen_width // 2
        half_screen_height = screen_height // 2
        start_x = half_screen_width
        start_y = half_screen_height

        if coordinate is None:
            if direction == 'up':
                end_x = start_x
                end_y = start_y + (screen_height // 2)
            elif direction == 'down':
                end_x = start_x
                end_y = start_y - (screen_height // 2)
            elif direction == 'right':
                end_x = start_x + (screen_width // 2)
                end_y = start_y
            elif direction == 'left':
                end_x = start_x - (screen_width // 2)
                end_y = start_y
            else:
                raise ValueError("Invalid direction. Use 'up', 'down', 'left', or 'right'.")
        else:
            end_x = coordinate[0]
            end_y = coordinate[1]
        print(start_x, start_y, end_x, end_y, duration)
        ADBUtil.scroll(start_x, start_y, end_x, end_y, duration)

    # @staticmethod
    # def scroll_with_coordinate_or_direction(coordinate=None, direction='down', duration=1000):
    #     # @todo down and up, cannot recover exactly?
    #     """
    #     Scrolls half the screen size in the specified direction.
    #
    #     Parameters:
    #     - direction: Direction of the scroll ('up', 'down', 'left', 'right')
    #     - screen_width: Width of the screen
    #     - screen_height: Height of the screen
    #     - duration: Duration of the scroll in milliseconds (default is 1000ms)
    #     """
    #     screen_width, screen_height = ADBUtil.get_screen_size()
    #     half_screen_width = screen_width // 2
    #     half_screen_height = screen_height // 2
    #     start_x = half_screen_width
    #     start_y = half_screen_height
    #
    #     # if end_x and end_y:
    #     #     start_x = half_screen_width
    #     #     start_y = half_screen_height
    #     if coordinate is None:
    #         if direction == 'down':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = half_screen_width
    #             end_y = 0
    #         elif direction == 'up':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = half_screen_width
    #             end_y = screen_height
    #         elif direction == 'right':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = 0
    #             end_y = half_screen_height
    #         elif direction == 'left':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = screen_width
    #             end_y = half_screen_height
    #         else:
    #             raise ValueError("Invalid direction. Use 'up', 'down', 'left', or 'right'.")
    #     else:
    #         end_x = coordinate[0]
    #         end_y = coordinate[1]
    #
    #     ADBUtil.scroll(start_x, start_y, end_x, end_y, duration)

    # @staticmethod
    # def scroll_with_coordinate_or_direction(coordinate=None, direction='down', duration=1000):
    #     screen_width, screen_height = ADBUtil.get_screen_size()
    #     orientation = ADBUtil.get_orientation()
    #
    #     if orientation == 1:  # Landscape mode
    #         screen_width, screen_height = screen_height, screen_width
    #
    #     half_screen_width = screen_width // 2
    #     half_screen_height = screen_height // 2
    #     start_x = half_screen_width
    #     start_y = half_screen_height
    #
    #     if coordinate is None:
    #         if direction == 'down':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = half_screen_width
    #             end_y = 0
    #         elif direction == 'up':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = half_screen_width
    #             end_y = screen_height
    #         elif direction == 'right':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = 0
    #             end_y = half_screen_height
    #         elif direction == 'left':
    #             start_x = half_screen_width
    #             start_y = half_screen_height
    #             end_x = screen_width
    #             end_y = half_screen_height
    #         else:
    #             raise ValueError("Invalid direction. Use 'up', 'down', 'left', or 'right'.")
    #     else:
    #         end_x = coordinate[0]
    #         end_y = coordinate[1]
    #
    #     ADBUtil.scroll(start_x, start_y, end_x, end_y, duration)

    @staticmethod
    def press_home():
        ADBUtil.run_adb_command(["shell", "input", "keyevent", "KEYCODE_HOME"])

    @staticmethod
    def press_enter():
        ADBUtil.run_adb_command(["shell", "input", "keyevent", "KEYCODE_ENTER"])

    @staticmethod
    def set_landscape_orientation():
        # Disable auto-rotate
        ADBUtil.run_adb_command(["shell", "settings", "put", "system", "accelerometer_rotation", "0"])
        # Set orientation to landscape
        ADBUtil.run_adb_command(
            ["shell", "content", "insert", "--uri", "content://settings/system", "--bind", "name:s:user_rotation",
             "--bind", "value:i:1"])

    @staticmethod
    def set_portrait_orientation():
        ADBUtil.run_adb_command(["shell", "settings", "put", "system", "accelerometer_rotation", "0"])
        ADBUtil.run_adb_command(
            ["shell", "content", "insert", "--uri", "content://settings/system", "--bind", "name:s:user_rotation",
             "--bind", "value:i:0"])

    @staticmethod
    def execute(action, coordinate=None, input_text=None, scroll_direction=None):
        # time.sleep(0.5)
        try:
            if action == Placeholder.TAP:
                ADBUtil.tap_screen(coordinate[0], coordinate[1])
            elif action == Placeholder.LONG_TAP:
                ADBUtil.long_tap(coordinate[0], coordinate[1])
            elif action == Placeholder.DOUBLE_TAP:
                ADBUtil.double_tap(coordinate[0], coordinate[1])
            elif action == Placeholder.INPUT:
                # print(action)
                ADBUtil.input_text(coordinate[0], coordinate[1], input_text)
            elif action == Placeholder.SCROLL:
                # @todo scroll to coordinate in the middle of screen
                ADBUtil.scroll_with_coordinate_or_direction(None, scroll_direction)
            elif action == Placeholder.HOME:
                ADBUtil.press_home()  # Add this line
            elif action == Placeholder.ENTER:
                ADBUtil.press_enter()  # Add this line
            elif action == Placeholder.LANDSCAPE:
                ADBUtil.set_landscape_orientation()
            elif action == Placeholder.PORTRAIT:
                ADBUtil.set_portrait_orientation()
            time.sleep(2)
        except Exception as e:
            print(f"When execute the operation: {e}")
            pass




