import os
import platform
import sys
import urllib.request
import winreg
import zipfile
from shutil import rmtree

CAIRO_VERSION = "1.15.12"
INSTALL_DIRECTORY = os.path.expanduser("~")  # User directory


class addWindowsPath:
    """This class set adds the Cairo Installation to Path"""

    def __init__(self, path):
        self.new_path_to_add = path

    def get_windows_path_var(self):
        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
            with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                path, _ = winreg.QueryValueEx(key, "PATH")

                return path

    def set_windows_path_var(self, value):
        import ctypes

        with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
            with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, value)

        # Tell other processes to update their environment
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
        SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            u"Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result),
        )

    def add_to_windows_path(self):
        path = self.new_path_to_add
        try:
            old_path = self.get_windows_path_var()
        except WindowsError:
            old_path = None

        if old_path is None:
            print(
                "warning",
                "Unable to get the PATH value. It will not be updated automatically",
            )

            return

        new_path = path
        if path in old_path:
            old_path = old_path.replace(path + ";", "")

        if old_path:
            new_path += ";"
            new_path += old_path

        self.set_windows_path_var(new_path)


def cleanInstall(temp):
    print("Starting to clean")
    for files in temp:
        if ".zip" in files:
            print("remove {} file".format(files))
            os.remove(files)
        else:
            print("remove {} directory".format(files))
            rmtree(files)


if __name__ == "__main__":
    if sys.platform.startswith("win") or (sys.platform == "cli" and os.name == "nt"):
        os.chdir(INSTALL_DIRECTORY)
        print("Installing Cairo dll in {}.".format(os.getcwd()))
        tempFiles = []
        cairoFolder = os.path.join(os.getcwd(), "Cairo")
        tempStore = "cairo-windows-{}".format(CAIRO_VERSION)
        downloadUrl = "https://github.com/preshing/cairo-windows/releases/download/{}/cairo-windows-{}.zip".format(
            CAIRO_VERSION, CAIRO_VERSION
        )

        print("Downloading Cairo From %s" % downloadUrl)
        # Get from `downloadUrl` and save in `tempStore`
        urllib.request.urlretrieve(downloadUrl, tempStore + ".zip")

        print("Download Complete. Extracting")

        # Extracts the Zip File downloaded
        with zipfile.ZipFile(tempStore + ".zip", "r") as zip_ref:
            zip_ref.extractall(cairoFolder)

        # Adding files to be removed
        tempFiles.append(os.path.join(os.getcwd(), tempStore + ".zip"))
        tempFiles.append(os.path.join(os.getcwd(), "Cairo", tempStore))
        print(
            "Copying required files to `{}`".format(os.path.join(os.getcwd(), "Cairo"))
        )
        try:
            if platform.architecture()[0] == "32bit":
                os.rename(
                    os.path.join("Cairo", tempStore, "lib", "x86", "cairo.dll"),
                    os.path.join("Cairo", "libcairo-2.dll"),
                )
            elif platform.architecture()[0] == "64bit":
                os.rename(
                    os.path.join("Cairo", tempStore, "lib", "x64", "cairo.dll"),
                    os.path.join("Cairo", "libcairo-2.dll"),
                )
            else:
                print("Platform Not supported")
                cleanInstall(tempFiles)
                sys.exit()
        except:
            print("Looks like the file is already copied.")
        print("Adding `{}` to Path".format(cairoFolder))
        windows = addWindowsPath(os.path.join(os.getcwd(), "Cairo"))
        windows.add_to_windows_path()
        cleanInstall(tempFiles)
