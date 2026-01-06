import json
import urllib.request
import urllib.error
import os
import tempfile
import zipfile
import shutil
import subprocess
from pathlib import Path
from AppKit import NSAlert, NSAlertStyleInformational, NSAlertStyleCritical

RELEASE_URL = "https://api.github.com/repos/sooswastaken/ClipX/releases/tags/latest"

class Updater:
    @staticmethod
    def check_for_updates():
        """
        Check GitHub for the latest release.
        Returns a dictionary with release info or None if failed.
        """
        try:
            print(f"[Updater] Checking for updates from {RELEASE_URL}...")
            with urllib.request.urlopen(RELEASE_URL, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Extract relevant info
                    release_info = {
                        "tag_name": data.get("tag_name"),
                        "published_at": data.get("published_at"),
                        "body": data.get("body"),
                        "html_url": data.get("html_url"),
                        "assets": data.get("assets", [])
                    }
                    
                    # Find the asset download URL
                    for asset in release_info["assets"]:
                        if asset["name"] == "ClipX.zip":
                            release_info["download_url"] = asset["browser_download_url"]
                            break
                    
                    return release_info
        except Exception as e:
            print(f"[Updater] Error checking for updates: {e}")
            return None
        return None

    @staticmethod
    def _create_install_script(old_app_path, new_app_path, pid):
        """
        Create a shell script to swap the apps and restart.
        """
        script_content = f"""#!/bin/bash
# Wait for the old app to terminate
while kill -0 {pid} 2>/dev/null; do
    sleep 0.5
done

# Short delay to ensure file locks are released
sleep 1

# Move new app to old app location
echo "Replacing {old_app_path} with {new_app_path}"
rm -rf "{old_app_path}"
mv "{new_app_path}" "{old_app_path}"

# Relaunch
echo "Relaunching..."
open "{old_app_path}"

# Cleanup script
rm -- "$0"
"""
        script_path = os.path.join(tempfile.gettempdir(), f"clipx_update_{pid}.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        return script_path

    @staticmethod
    def install_and_restart(download_url):
        """
        Download, extract, and replace the running application.
        """
        try:
            print(f"[Updater] Downloading update from {download_url}...")
            
            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="ClipX_Update_"))
            zip_path = temp_dir / "ClipX.zip"
            
            # Download
            with urllib.request.urlopen(download_url) as response, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # Extract
            print("[Updater] Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            new_app_path = temp_dir / "ClipX.app"
            if not new_app_path.exists():
                print("[Updater] Error: ClipX.app not found in zip")
                return False

            # Detect current app path
            from AppKit import NSBundle
            current_bundle_path = NSBundle.mainBundle().bundlePath()
            
            # Check if we are running as a packaged app
            # CRITICAL: Only use sys.frozen to detect packaged app. 
            # Checking .endswith('.app') is DANGEROUS because when running from source,
            # the main bundle is often the Python interpreter itself (Python.app).
            is_packaged = getattr(os.sys, 'frozen', False)
            
            if is_packaged and current_bundle_path != str(new_app_path):
                print(f"[Updater] Preparing to replace {current_bundle_path}...")
                
                # Create and run update script
                script_path = Updater._create_install_script(
                    current_bundle_path, 
                    str(new_app_path), 
                    os.getpid()
                )
                
                print(f"[Updater] Launching update script: {script_path}")
                subprocess.Popen(['/bin/bash', script_path], start_new_session=True)
                
                # Signal success (caller should exit)
                return True
            else:
                print("[Updater] Not running as packaged app (or path mismatch), revealing in Finder instead.")
                subprocess.run(["open", "-R", str(new_app_path)])
                return False
            
        except Exception as e:
            print(f"[Updater] Error installing update: {e}")
            return False

    @staticmethod
    def show_update_dialog(release_info):
        """
        Show a dialog to the user about the update.
        Returns True if user wants to update, False otherwise.
        """
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Check for Updates")
        
        if release_info:
            published_date = release_info.get('published_at', 'Unknown date').split('T')[0]
            info_text = (
                f"Latest Release: {release_info.get('tag_name')}\n"
                f"Published: {published_date}\n\n"
                f"Release Notes:\n{release_info.get('body')}\n\n"
                "Would you like to download this update?"
            )
            alert.setInformativeText_(info_text)
            alert.addButtonWithTitle_("Download & Update")
            alert.addButtonWithTitle_("Cancel")
        else:
            alert.setMessageText_("Update Check Failed")
            alert.setInformativeText_("Could not verify release information. Please check your internet connection.")
            alert.setAlertStyle_(NSAlertStyleCritical)
            alert.addButtonWithTitle_("OK")

        response = alert.runModal()
        return response == 1000 # 1000 is the first button (Download/OK)
