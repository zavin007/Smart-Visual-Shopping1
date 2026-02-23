import tensorflow as tf
print(f"TensorFlow Version: {tf.__version__}")
gpus = tf.config.list_physical_devices('GPU')
print(f"GPUs Available: {len(gpus)}")
if gpus:
    for gpu in gpus:
        print(f" - {gpu}")
else:
    print("❌ No GPU detected by TensorFlow.")
    print("Note: TensorFlow 2.10+ on Windows Native does NOT support GPU. You need WSL2 or Docker.")
