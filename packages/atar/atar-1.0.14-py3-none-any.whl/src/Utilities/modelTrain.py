import os
import time
from datetime import datetime  # For timestamp
from ultralytics import YOLO
from src.Utilities import flexMenu
from src.Utilities import log

def m_train():
    start_time = time.time()
    m = ""
    try:
        # Code that might raise an exception
        f = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
        
        # Ensure the output folder structure exists
        model_path = os.path.join(os.getcwd(), "OUTPUT", "yolov8DefaultModels")
        if not os.path.exists(model_path):
            os.makedirs(model_path)  # Create directory if it doesn't exist
        
        model_name = flexMenu.display_options(f)
        model_path = os.path.join(model_path, model_name)
        
        data_path = os.path.join("OUTPUT", "datasets")
        f = os.listdir(data_path)
        y = os.getcwd()
        
        print("\n\t DATASETS :")
        dataset_name = flexMenu.display_options(f)  # Capture the selected dataset name
        data_path = os.path.join(y, data_path, dataset_name, "data.yaml")
        
        # Configure Training Parameters
        print("\n\tConfigure Training Parameters : ")
        epochs = int(input("\n\t  ======> Insert Epochs Value   : "))
        imgsz = int(input("\n\t  ======> Insert imgsz Value    : "))
        
        # Handling device input validation
        device_input = input("\n\t  ======> Insert device Value (cpu or GPU ID): ").strip().lower()
        if device_input == "cpu":
            device = device_input
        else:
            try:
                device = int(device_input)  # Try converting to an integer for GPU ID
            except ValueError:
                raise ValueError("Invalid device input. Please enter 'cpu' or a valid GPU ID.")
        
        lr = float(input("\n\t  ======> Insert learning Rate Value  : "))
        
        project = os.path.join("OUTPUT", "Train")
        
        # Setting model variant
        model_map = {
            "yolov8n.pt": "n",
            "yolov8s.pt": "s",
            "yolov8m.pt": "m",
            "yolov8l.pt": "l",
            "yolov8x.pt": "x"
        }
        
        m = model_map.get(model_name, "")
        
        if not m:
            raise ValueError("Invalid model selected.")
        
        # Generate a timestamp and include it in the folder name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        name = f"{dataset_name}-{timestamp}-train-e{epochs}-i{imgsz}-lr{lr}-v8{m}"
        
        model = YOLO(model_path)
        
        # Logging training start
        log.logger.info("\nTraining START")
        print("\n")
        
        model.train(data=data_path, epochs=epochs, imgsz=imgsz, device=device,
                    project=project, name=name, show_labels=True, lr0=lr)

    except Exception as e:
        # Handle exceptions
        end_time = time.time()
        log.logger.error(f"\nAn error occurred: {e}\nExecution time: %.2f seconds", end_time - start_time)
    
    else:
        # If no exception occurred
        end_time = time.time()
        log.logger.info("\nNo errors occurred. Training completed successfully.\nExecution time: %.2f seconds", end_time - start_time)

    finally:
        # Code that will run regardless of whether an exception occurred
        log.logger.critical("\nTraining EXIT")
        print("\n")
