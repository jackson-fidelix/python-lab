import streamlit as st
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions


img_file_buffer = st.camera_input("Don't forget take a photo")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    img_tensor = tf.io.decode_image(bytes_data, channels=3) # tres canais de cores - RGB

    img_resized = tf.image.resize(img_tensor, [224, 224]) # tamanho da imagem

    preprocessed_img = preprocess_input(tf.expand_dims(img_resized, axis=0))

    
    model = MobileNetV2(weights='imagenet') # o modelo vai buscar no banco de imagens (imagenet)

    predictions = model.predict(preprocessed_img)

    decoded_predictions = decode_predictions(predictions, top=1)[0]

    dominant_object = decoded_predictions[0][1]
    score_object = decoded_predictions[0][2]

    st.write(f"Dominant Object: {dominant_object} - {score_object * 100:.2f}%") # retorno

# command to execute project ".\.venv\Scripts\streamlit.exe run tensorflow\identify-objects\index.py"