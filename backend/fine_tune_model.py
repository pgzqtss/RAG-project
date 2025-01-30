import pandas as pd
import tensorflow as tf
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer

# Load the dataset
df = pd.read_csv('training_data.csv')
X = df['medical_paper'].tolist()
Y = df['systematic_review'].tolist()

class MedicalPapersDataset(tf.data.Dataset):
    def __new__(cls, X, Y, tokenizer, max_length):
        def gen():
            for x, y in zip(X, Y):
                inputs = tokenizer(x, padding='max_length', max_length=max_length, truncation=True, return_tensors="tf")
                targets = tokenizer(y, padding='max_length', max_length=max_length, truncation=True, return_tensors="tf")
                yield ({"input_ids": tf.squeeze(inputs["input_ids"], axis=0), "attention_mask": tf.squeeze(inputs["attention_mask"], axis=0), "decoder_input_ids": tf.squeeze(targets["input_ids"], axis=0)}, tf.squeeze(targets["input_ids"], axis=0))
        
        return tf.data.Dataset.from_generator(
            gen,
            output_signature=(
                {
                    "input_ids": tf.TensorSpec(shape=(512,), dtype=tf.int32),
                    "attention_mask": tf.TensorSpec(shape=(512,), dtype=tf.int32),
                    "decoder_input_ids": tf.TensorSpec(shape=(512,), dtype=tf.int32),
                },
                tf.TensorSpec(shape=(512,), dtype=tf.int32)
            )
        )

# Initialize tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('t5-small')
model = TFAutoModelForSeq2SeqLM.from_pretrained('t5-small')

# Create the dataset
max_length = 512
dataset = MedicalPapersDataset(X, Y, tokenizer, max_length)

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=3e-5)
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

model.compile(optimizer=optimizer, loss=loss_fn)

# Train the model
model.fit(dataset.batch(8), epochs=3)

# Evaluate the model
model.evaluate(dataset.batch(8))  # Use your validation dataset

# Save the fine-tuned model
model.save_pretrained("fine-tuned-model")
tokenizer.save_pretrained("fine-tuned-model")

print("Fine-tuning complete and model saved.")
