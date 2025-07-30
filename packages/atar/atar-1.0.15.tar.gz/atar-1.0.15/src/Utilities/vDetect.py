import cv2
from ultralytics import YOLO
import os
import time
from src.Utilities import log
from src.Utilities import flexMenu


def video_detect():
    try:
        # Ensure OUTPUT/Train directory exists
        train_dir = "OUTPUT/Train"
        if not os.path.exists(train_dir):
            raise FileNotFoundError(f"Directory '{train_dir}' does not exist.")

        # Select model folder
        models = os.listdir(train_dir)
        if not models:
            raise FileNotFoundError("No models found in the 'OUTPUT/Train' directory.")
        selected_model = flexMenu.display_options(models)
        model_path = os.path.join(train_dir, selected_model, "weights")

        # Select model file
        weights = os.listdir(model_path)
        if not weights:
            raise FileNotFoundError(f"No weights found in the '{model_path}' directory.")
        selected_weight = flexMenu.display_options(weights)
        model_path = os.path.join(model_path, selected_weight)

        # Validate threshold input
        while True:
            try:
                threshold = float(input("Enter detection threshold (0.0 - 1.0): ").strip())
                if 0.0 <= threshold <= 1.0:
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Invalid input. Please enter a number between 0.0 and 1.0.")

        log.logger.info("\nDetection START")
        start_time = time.time()

        # Get video sample path
        video_path = input("Paste the path of the video sample: ").strip()
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"The video path '{video_path}' does not exist.")

        # Prepare output directories
        video_dir = os.path.join(os.getcwd(), 'runs', 'Videos', 'Scans')
        os.makedirs(video_dir, exist_ok=True)

        # Generate output file path
        model_name = selected_weight.rsplit(".", 1)[0]
        video_name = os.path.basename(video_path).rsplit(".", 1)[0]
        output_file = f"{video_name}-{selected_model}-{model_name}-{threshold}_out.mp4"
        video_path_out = os.path.join(video_dir, output_file)

        # Load video
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if not ret:
            raise ValueError("Failed to read the video. Ensure the file is valid.")

        # Prepare video writer
        height, width, _ = frame.shape
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), fps, (width, height))

        # Load YOLO model
        model = YOLO(model_path)

        # Process video frames
        while ret:
            results = model(frame)[0]
            for result in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result
                if score > threshold:
                    # Draw bounding box and label
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    label = f"{results.names[int(class_id)].upper()}: {score:.2f}"
                    cv2.putText(frame, label, (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            out.write(frame)
            ret, frame = cap.read()

        cap.release()
        out.release()
        log.logger.info(f"\nDetection complete. Output saved to: {video_path_out}")
    except Exception as e:
        log.logger.error(f"\nAn error occurred: {e}")
    finally:
        log.logger.warning("\nDetection EXIT\n")
