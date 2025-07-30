import os
import shutil
import subprocess
import tarfile
import tempfile
from platformdirs import user_data_dir
import requests
from sage_web_apps.constants import APP_NAME, SAGE_RESULTS_FOLDER, SAGE_EXECUTABLE
from sage_web_apps.utils import get_sage_download_url
import re
import zipfile

class SageFileManager:

    def __init__(self, version: str):
        """
        Initialize the SageFileManager with the specified SAGE version.
        This class handles file management tasks for SAGE applications.
        """
        self.version = version

        self.app_dir = user_data_dir(appname=APP_NAME, appauthor=False, version=version)
        self.sage_executable_directory = os.path.join(self.app_dir, "sage")
        self.sage_executable_path = os.path.join(self.app_dir, "sage", SAGE_EXECUTABLE)
        self.results_directory_path = os.path.join(self.app_dir, SAGE_RESULTS_FOLDER)
        self.setup_appdir()

        self.setup_sage()
        self.check_sage_executable()
        

    def setup_appdir(self):
        # Create the directory if it doesn't exist
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir, exist_ok=True)

        # create sage dir
        if not os.path.exists(self.sage_executable_directory):
            os.makedirs(self.sage_executable_directory, exist_ok=True)

        # create directory for results
        results_dir = os.path.join(self.app_dir, SAGE_RESULTS_FOLDER)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)

    def setup_sage(self):
        # check if sage executable exists, if not download it
        if os.path.exists(self.sage_executable_path):
            print(f"Sage executable already exists at {self.sage_executable_path}")
        else:
            sage_download_url = get_sage_download_url(self.version)
            
            # Implement download logic here
            with tempfile.TemporaryDirectory(dir=self.sage_executable_directory, delete=False) as tmp_dir:
                # Download the archive file with original filename
                response = requests.get(sage_download_url, stream=True)
                if response.status_code != 200:
                    raise Exception(f"Failed to download Sage: HTTP status {response.status_code}")
                
                # Get filename from URL or headers
                if "Content-Disposition" in response.headers:
                    filename = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0].strip('"')
                else:
                    filename = os.path.basename(sage_download_url)
                
                archive_path = os.path.join(tmp_dir, filename)
                with open(archive_path, "wb") as f:
                    f.write(response.content)

                # Extract based on file extension
                if filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                    with tarfile.open(archive_path, "r:gz") as tar:
                        tar.extractall(path=tmp_dir)
                elif filename.endswith('.zip'):
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(tmp_dir)
                else:
                    raise Exception(f"Unsupported archive format: {filename}")

                # Find the extracted directory (should be sage-v*-arch-*-linux-gnu)
                extracted_dirs = [
                    d for d in os.listdir(tmp_dir) 
                    if (d.startswith("sage-v") or "sage" in d.lower()) and os.path.isdir(os.path.join(tmp_dir, d))
                ]
                if not extracted_dirs:
                    raise Exception("Could not find extracted Sage directory")
                extracted_dir = os.path.join(tmp_dir, extracted_dirs[0])

                # Clear the sage executable directory to avoid conflicts
                for file in os.listdir(self.sage_executable_directory):
                    path = os.path.join(self.sage_executable_directory, file)
                    if os.path.isfile(path):
                        os.remove(path)

                # Copy all files, ensuring sage executable goes to the right location
                for file in os.listdir(extracted_dir):
                    src = os.path.join(extracted_dir, file)
                    dst = os.path.join(self.sage_executable_directory, file)
                    print(f"Copying {src} to {dst}")
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                        # Make the sage executable actually executable
                        if file == "sage" or file == "sage.exe":
                            os.chmod(dst, 0o755)
                            # Rename sage.exe to sage for compatibility
                            if file == "sage.exe":
                                sage_exe_path = dst
                                sage_path = os.path.join(self.sage_executable_directory, "sage")
                                shutil.copy2(sage_exe_path, sage_path)
                                os.chmod(sage_path, 0o755)

    def check_sage_executable(self):
        # check if sage executable can run
        if not os.path.exists(self.sage_executable_path):
            raise FileNotFoundError(f"Sage executable not found at {self.sage_executable_path}. Please ensure Sage is downloaded and extracted correctly.")
        if not os.access(self.sage_executable_path, os.X_OK):
            raise PermissionError(f"Sage executable at {self.sage_executable_path} is not executable. Please check permissions.")
        
        # try to run the sage executable to check if it works
        try:
            result = subprocess.run([self.sage_executable_path, "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Sage executable at {self.sage_executable_path} failed to run: {result.stderr.strip()}")
            print(f"Sage version: {result.stdout.strip()}")
        except Exception as e:
            raise RuntimeError(f"Failed to run Sage executable: {str(e)}")
        
    def run_search(self, params: dict, output_path: str, include_fragment_annotations: bool = True, output_type: str = "csv"):
        
        # with tmp dir save params

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            json_path = tmp_file.name
            import json

            with open(json_path, 'w') as f:
                json.dump(params, f, indent=4)
        
            command = [
                self.sage_executable_path,
                json_path,
            ]
            if include_fragment_annotations:
                command.append("--annotate-matches")

            if output_type == "parquet":
                command.append("--parquet")

            # create output directory if it doesn't exist
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)

            command_str = " ".join(command)
            print(f"Running Sage command: {command_str}")

            try:
                result = subprocess.run(command, capture_output=True, text=True)
            except Exception as e:
                print(f"Error running Sage command: {str(e)}")
                

            # write logs
            log_file = os.path.join(output_path, "sage.log")
            with open(log_file, "w") as f:
                f.write("Sage run command:\n")
                f.write(command_str + "\n\n")
                f.write("Sage stdout:\n")
                f.write(result.stdout + "\n\n")
                f.write("Sage stderr:\n")
                f.write(result.stderr + "\n")


