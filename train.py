"""
Train MobileNetV2 on Fashion Product Dataset
Run after: python download_dataset.py
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
import json

# Configuration
DATA_DIR = "data/fashion-dataset/organized"
MODEL_SAVE_PATH = "trained_model.keras"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10

def train_model():
    print("[START] Starting Model Training on Fashion Dataset...")
    
    # Check if dataset exists
    if not os.path.exists(DATA_DIR):
        print(f"[ERROR] Dataset not found at {DATA_DIR}")
        print("   Please run: python download_dataset.py first!")
        return
    
    # Count categories
    categories = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    num_classes = len(categories)
    print(f"[INFO] Found {num_classes} categories")
    
    # Data Generators with Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2  # 20% for validation
    )
    
    print("\n[LOAD] Loading training data...")
    train_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    print("\n[LOAD] Loading validation data...")
    validation_generator = train_datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    # Save class indices for later use
    class_indices = train_generator.class_indices
    with open("class_indices.json", "w") as f:
        json.dump(class_indices, f)
    print(f"[SAVE] Saved class indices to class_indices.json")
    
    # Build Model
    print("\n[BUILD] Building model...")
    base_model = MobileNetV2(
        weights='imagenet', 
        include_top=False, 
        input_shape=(224, 224, 3)
    )
    
    # Freeze base model layers
    base_model.trainable = False
    
    # Add classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"\n[INFO] Model Summary:")
    print(f"   - Base: MobileNetV2 (ImageNet)")
    print(f"   - Classes: {num_classes}")
    print(f"   - Training samples: {train_generator.samples}")
    print(f"   - Validation samples: {validation_generator.samples}")
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            patience=3,
            restore_best_weights=True
        ),
        ModelCheckpoint(
            MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Train
    print("\n[TRAIN] Starting training...")
    print("=" * 50)
    
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        callbacks=callbacks
    )
    
    print("\n" + "=" * 50)
    print("[OK] Training Complete!")
    print(f"[SAVE] Best model saved to: {MODEL_SAVE_PATH}")
    
    # Final stats
    final_acc = max(history.history['val_accuracy'])
    print(f"[RESULT] Best Validation Accuracy: {final_acc:.2%}")
    
    # Fine-tune (optional - unfreeze some layers)
    print("\n[FINETUNE] Fine-tuning top layers...")
    base_model.trainable = True
    
    # Freeze all but last 20 layers
    for layer in base_model.layers[:-20]:
        layer.trainable = False
    
    model.compile(
        optimizer=Adam(learning_rate=0.0001),  # Lower learning rate
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history_fine = model.fit(
        train_generator,
        epochs=5,
        validation_data=validation_generator,
        callbacks=callbacks
    )
    
    print("\n[DONE] Fine-tuning complete!")
    model.save(MODEL_SAVE_PATH)
    print(f"[SAVE] Final model saved to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_model()
