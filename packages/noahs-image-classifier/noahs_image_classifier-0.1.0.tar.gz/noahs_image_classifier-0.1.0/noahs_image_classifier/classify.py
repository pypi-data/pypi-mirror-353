
from PIL import Image, ImageOps
import numpy as np
import platform

try:
    if platform.system() == "Linux":
        import tflite_runtime.interpreter as tflite
    else:
        from tensorflow.lite.python.interpreter import Interpreter as tflite_Interpreter
        class tflite:
            Interpreter = tflite_Interpreter
except ImportError as e:
    raise ImportError("Neither `tflite_runtime` nor `tensorflow` is available. Please install one based on your OS.") from e

from noahs_camera_controller import list_available_cameras, capture_photo

class image_classifier:
    def __init__(self, model_path="model.tflite", class_names="labels.txt"):
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        with open(class_names, "r") as f:
            self.class_names = f.readlines()

    def classify(self, image_path):
        image = Image.open(image_path).convert("RGB")
        image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)

        # Normalize to [-1, 1] for float model
        input_data = np.expand_dims(np.asarray(image).astype(np.float32) / 127.5 - 1, axis=0)

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

        prediction = output_data[0]
        index = np.argmax(prediction)
        class_name = self.class_names[index].strip().split()[1]
        confidence_score = prediction[index]

        return {
            "image": image_path,
            "class": class_name,
            "confidence_score": confidence_score
        }

    def identify(self, image_path):
        return self.classify(image_path)["class"]
    
    def capture_and_identify(self):
        capture_photo("capture_and_identify")
        return self.identify("capture_and_identify.jpg")


if __name__ == "__main__":
    model = image_classifier(model_path="dog_or_frog/model.tflite", class_names="dog_or_frog/labels.txt")

    c1 = model.classify("dog_or_frog/images/dog.jpg")
    c2 = model.classify("dog_or_frog/images/frog.jpg")

    print("\n")
    print(c1)
    print("\n")
    print(c2)



















