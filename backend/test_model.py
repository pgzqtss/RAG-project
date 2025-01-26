import pandas as pd
import tensorflow as tf
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer, create_optimizer
from tensorflow.keras.losses import SparseCategoricalCrossentropy
import time

# Check GPU availability
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print("GPU is available. Dynamic memory growth enabled.")
else:
    print("No GPU detected. Running on CPU.")

# Load model and tokenizer
print("Loading fine-tuned model and tokenizer...")
model = TFAutoModelForSeq2SeqLM.from_pretrained("fine-tuned-model")
tokenizer = AutoTokenizer.from_pretrained("fine-tuned-model")

# Load test dataset
print("Loading test dataset...")
df_test = pd.read_csv('testing_data.csv')
X_test = df_test['medical_paper'].tolist()
Y_test = df_test['systematic_review'].tolist()

# Define dataset
class MedicalPapersTestDataset(tf.data.Dataset):
    def __new__(cls, X, Y, tokenizer, max_length):
        def gen():
            for x, y in zip(X, Y):
                inputs = tokenizer(x, padding='max_length', max_length=max_length, truncation=True, return_tensors="tf")
                targets = tokenizer(y, padding='max_length', max_length=max_length, truncation=True, return_tensors="tf")
                yield (
                    {
                        "input_ids": tf.squeeze(inputs["input_ids"], axis=0),
                        "attention_mask": tf.squeeze(inputs["attention_mask"], axis=0),
                        "decoder_input_ids": tf.squeeze(targets["input_ids"], axis=0),
                    },
                    tf.squeeze(targets["input_ids"], axis=0),
                )

        return tf.data.Dataset.from_generator(
            gen,
            output_signature=(
                {
                    "input_ids": tf.TensorSpec(shape=(512,), dtype=tf.int32),
                    "attention_mask": tf.TensorSpec(shape=(512,), dtype=tf.int32),
                    "decoder_input_ids": tf.TensorSpec(shape=(512,), dtype=tf.int32),
                },
                tf.TensorSpec(shape=(512,), dtype=tf.int32),
            ),
        )

max_length = 512
test_dataset = MedicalPapersTestDataset(X_test, Y_test, tokenizer, max_length)

# Define loss function
loss_fn = SparseCategoricalCrossentropy(from_logits=True)

# Define optimizer and warmup
batch_size = 1  # Use a small batch size to avoid memory issues
epochs = 1
steps_per_epoch = len(X_test) // batch_size
total_steps = steps_per_epoch * epochs  # Total training steps
warmup_steps = int(0.1 * total_steps)  # 10% of total steps for warmup

# Create optimizer
optimizer, schedule = create_optimizer(
    init_lr=3e-5,               # Initial learning rate
    num_warmup_steps=warmup_steps,  # Warmup steps
    num_train_steps=total_steps    # Total training steps
)

# Compile the model
print("Compiling the model...")
model.compile(optimizer=optimizer, loss=loss_fn)

# Evaluate the model
print("Evaluating the model...")
results = model.evaluate(test_dataset.batch(batch_size))
print(f"Test Loss: {results}")

inputs = tokenizer(
    "This is a test sentence for XLA warmup.",
    return_tensors="tf",
    padding="max_length",
    max_length=128,
    truncation=True
)

# Warmup XLA
_ = model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    max_length=128,
    num_beams=1
)

print("XLA initialization completed.")


# Make predictions on the test dataset
print("Making predictions...")

decoded_predictions = []
batch_size = 8
test_dataset = tf.data.Dataset.from_tensor_slices(X_test).batch(batch_size)

for i, batch in enumerate(test_dataset):
    print(f"Processing batch {i + 1}/{len(X_test) // batch_size}...")

    # Ensure batch is a list of strings
    texts = [x.decode("utf-8") if isinstance(x, bytes) else x for x in batch.numpy()]

    # Tokenize the batch
    inputs = tokenizer(
        texts,
        return_tensors="tf",
        padding="max_length",
        max_length=512,  # Limit input length
        truncation=True
    )

    # Measure generation time
    start_time = time.time()
    outputs = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=64,  # Limit output length
        num_beams=1,    # Use Greedy Search
        early_stopping=True
    )
    end_time = time.time()

    print(f"Batch {i + 1} processed in {end_time - start_time:.2f} seconds.")

    # Decode predictions
    decoded_predictions.extend([
        tokenizer.decode(output, skip_special_tokens=True) for output in outputs
    ])

# Print sample predictions
print("Printing sample predictions:")
for i in range(min(5, len(X_test))):
    print(f"Medical Paper {i + 1}: {X_test[i]}")
    print(f"Actual Review {i + 1}: {Y_test[i]}")
    print(f"Predicted Review {i + 1}: {decoded_predictions[i]}")
    print("------")