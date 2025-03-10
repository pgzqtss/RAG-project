import pandas as pd
import tensorflow as tf
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer

# Load the fine-tuned model and tokenizer
model = TFAutoModelForSeq2SeqLM.from_pretrained("fine-tuned-model")
tokenizer = AutoTokenizer.from_pretrained("fine-tuned-model")

# Load the testing dataset
df_test = pd.read_csv('testing_data.csv')
X_test = df_test['medical_paper'].tolist()
Y_test = df_test['systematic_review'].tolist()

class MedicalPapersTestDataset(tf.data.Dataset):
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

# Create the testing dataset
max_length = 512
test_dataset = MedicalPapersTestDataset(X_test, Y_test, tokenizer, max_length)

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=3e-5)
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer=optimizer, loss=loss_fn)

# Evaluate the model on the testing dataset
results = model.evaluate(test_dataset.batch(4))
print(f"Test Loss: {results}")

# Make predictions on the testing dataset
predictions = model.predict(test_dataset.batch(4))

# Decode the predictions
decoded_predictions = [tokenizer.decode(pred, skip_special_tokens=True) for pred in predictions['logits']]

# Print some sample predictions
for i in range(5):
    print(f"Medical Paper: {X_test[i]}")
    print(f"Actual Review: {Y_test[i]}")
    print(f"Predicted Review: {decoded_predictions[i]}")
    print("------")