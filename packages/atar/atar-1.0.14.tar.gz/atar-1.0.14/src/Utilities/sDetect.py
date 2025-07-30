import os
import datetime
import time
import argparse
from src.Utilities import log
from src.Utilities import flexMenu

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover - optional dependency
    YOLO = None

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency
    cv2 = None

try:
    import supervision as sv
except Exception:  # pragma: no cover - optional dependency
    sv = None


def is_fire_detected(detections) -> bool:
    """Return ``True`` if class id ``0`` is present in ``detections``."""
    try:
        class_ids = detections.class_id
    except AttributeError:
        return False

    # Attempt NumPy-like equality check first
    try:
        result = class_ids == 0
        if hasattr(result, "any"):
            return result.any()
    except (TypeError, ValueError):
        pass

    # Fallback for iterables or objects exposing underlying data
    try:
        for cid in class_ids:
            if cid == 0:
                return True
    except TypeError:
        data = getattr(class_ids, "data", None)
        if data is not None:
            return 0 in data

    return False


def create_directories(path: str):
    """Create directories if they don't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        log.logger.info(f"Created missing directory: {path}")


def create_video_writer(video_cap, output_filename):
    """Initialize a video writer object."""
    frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    return cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))


def stream():
    current_time = datetime.datetime.now()
    desired_format = "%Y-%m-%d_%H-%M-%S_"
    formatted_time = current_time.strftime(desired_format)

    log.logger.info("\nSTREAM START")
    start_time = time.time()

    if YOLO is None or cv2 is None or sv is None:
        raise ImportError("Required dependencies for streaming are not installed")

    def parse_arguments() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="YOLOv8 live")
        parser.add_argument("--webcam-resolution", default=[1920, 1080], nargs=2, type=int)
        return parser.parse_args()

    try:
        # Define the base output path
        base_path = "OUTPUT/runs/Streams"
        create_directories(base_path)

        model_path = "OUTPUT/Train/"
        x = os.listdir(model_path)
        train = flexMenu.display_options(x)
        model_path = model_path + train + "/weights/"
        x = os.listdir(model_path)
        m = flexMenu.display_options(x)
        model_path = model_path + "/" + m
        m = m.rsplit(".", 1)[0]

        model = YOLO(model_path)
        args = parse_arguments()
        frame_width, frame_height = args.webcam_resolution
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        output_file = os.path.join(base_path, f"{formatted_time}{train}{m}.mp4")
        writer = create_video_writer(cap, output_file)

        box_annotator = sv.BoxAnnotator(thickness=2)

        while True:
            ret, frame = cap.read()
            results = model(frame)
            detections = sv.Detections.from_ultralytics(results[0])
            frame = box_annotator.annotate(scene=frame, detections=detections)

            # Trigger alert when a detection of class id 0 is present
            if is_fire_detected(detections):
                log.logger.critical('ALAAAAAAARRM RINGING FIRE !!!!!')

            cv2.imshow("yolov8", frame)
            writer.write(frame)

            if cv2.waitKey(30) == 27:  # ESC key to exit
                break

        cap.release()
        writer.release()
        cv2.destroyAllWindows()

    except Exception as e:
        end_time = time.time()
        log.logger.error(f"\nAn error occurred: {e}\nExecution time: %.2f seconds", end_time - start_time)
    else:
        end_time = time.time()
        log.logger.info("\nNo errors occurred DONE SUCCESS\nExecution time: %.2f seconds", end_time - start_time)
    finally:
        log.logger.critical("\nSTREAM EXIT")
        print("\n")
