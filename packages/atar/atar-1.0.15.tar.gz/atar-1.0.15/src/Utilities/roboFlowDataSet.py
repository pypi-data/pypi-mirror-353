import time
from src.Utilities import log
import os
import subprocess
import platform


def roboflow_dataset():
    start_time = time.time()

    # User input for the Roboflow dataset URL and desired dataset name
    roboflow_url = input("Enter the Roboflow dataset URL: ")
    dataset_name = input("Enter the desired dataset name: ")

    try:
        # Create necessary directories if they don't exist
        output_dir = "OUTPUT/datasets"
        dataset_dir = os.path.join(output_dir)  # Base folder for datasets

        # Ensure the base dataset directory (OUTPUT/datasets) exists
        os.makedirs(dataset_dir, exist_ok=True)

        # Change to the datasets directory
        os.chdir(dataset_dir)

        # Log download start
        log.logger.info("\nDOWNLOAD START\n")
        print("\nDownloading Dataset...\n")

        # Step 1: Download the dataset
        zip_file = "roboflow.zip"
        subprocess.run(
            ["curl", "-L", roboflow_url, "-o", zip_file],
            check=True
        )

        # Step 2: Unzip the dataset
        if platform.system() == "Windows":
            # Use Expand-Archive on Windows
            subprocess.run(
                ["powershell", "Expand-Archive", zip_file, "-DestinationPath", dataset_name],
                check=True
            )
        else:
            # Use unzip on Linux with the destination directory specified
            subprocess.run(["unzip", zip_file, "-d", dataset_name], check=True)

        # Step 3: Remove the ZIP file
        os.remove(zip_file)

    except subprocess.CalledProcessError as e:
        # Handle subprocess errors and log them
        end_time = time.time()
        log.logger.error(f"\nAn error occurred during dataset download: {e}\nExecution time: %.2f seconds", end_time - start_time)
    except FileNotFoundError as e:
        # Handle missing file errors and log them
        end_time = time.time()
        log.logger.error(f"\nAn error occurred: {e}\nExecution time: %.2f seconds", end_time - start_time)
    except Exception as e:
        # Handle other exceptions and log them
        end_time = time.time()
        log.logger.error(f"\nAn error occurred: {e}\nExecution time: %.2f seconds", end_time - start_time)
    else:
        # Log success if no errors occurred
        end_time = time.time()
        log.logger.info("\nNo errors occurred DONE SUCCESS\nExecution time: %.2f seconds", end_time - start_time)
    finally:
        # Log and reset working directory
        log.logger.warning("\nDatasetDownload EXIT\n")
        os.chdir("../../")
