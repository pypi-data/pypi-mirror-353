# ATAR CLI

ATAR CLI is a command line interface that wraps common tasks for training and
running YOLOv8 based fire detection models. It provides a simple interactive
menu to download datasets, start and resume training, validate models and run
live or video based detection.

## Installation

The project can be installed from source using `pip`:

```bash
pip install -e .
```

The tool requires Python 3.7+ and depends on packages such as `ultralytics`,
`roboflow` and `supervision`.

## Usage

After installation run the CLI with:

```bash
atar-cli
```

The following menu options are available:

1. **Download RoboFlow training dataset** – Fetch a dataset from Roboflow.
2. **Train** – Start a new training run using a selected model and dataset.
3. **Resume existing training** – Continue a previous training run.
4. **Validate** – Evaluate a trained model on a validation dataset.
5. **Live Test** – Run detection on frames from a webcam.
6. **Test on an existing file** – Perform detection on a saved video file.
7. **Quit** – Exit the CLI.

Select an option by entering the corresponding number. Some options will ask for
additional input such as dataset paths or model names.

## Development

Install the development requirements and run the test suite with `pytest` to
ensure everything works as expected.

```bash
pip install -r requirements.txt  # if available
pytest -q
```

Contributions are welcome! Feel free to open issues or pull requests on the
[GitHub repository](https://github.com/otman-dev/atar-cli).
