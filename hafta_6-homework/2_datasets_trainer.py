"""
Datasets + Trainer Kullanımı (movie_metadata.csv ile — Overview + IMDB_Rating varsayılan)

Özellikler:
- CSV'den kolon tespiti (movie_title & imdb_score)
- imdb_score -> binary label; threshold otomatik seçilebilir (auto_select_threshold)
- TRAIN seti için otomatik undersample (varsa)
- Tokenization sırasında 'label' korunur ve 'labels' olarak rename edilir
- TrainingArguments için modern/legacy uyumluluğu (fallback)
- Model ./fine_tuned_model altına kaydedilir
"""

import os
import random
from collections import Counter
import numpy as np
from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ---------- AYARLAR ----------
MODEL_NAME = "distilbert-base-uncased"
DATA_PATH = "data/movie_metadata.csv"
OUTPUT_DIR = "./fine_tuned_model"
RANDOM_SEED = 42
DEFAULT_THRESHOLD = 7.0   # fallback threshold
UNDERSAMPLE = True        # Train kümesini dengelemek için undersample
MIN_SAMPLES_PER_CLASS_FOR_AUTO = 10  # auto threshold seçerken sınıf başına minimum örnek
# -----------------------------

def seed_everything(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass

def infer_text_and_label_candidates(column_names):
    # Öncelikli text ve label kolonları
    text_priority = ["movie_title", "overview", "review", "description", "plot"]
    label_priority = ["imdb_score", "IMDB_Rating", "rating", "score"]

    text_col = None
    label_col = None
    for t in text_priority:
        if t in column_names:
            text_col = t
            break
    for l in label_priority:
        if l in column_names:
            label_col = l
            break

    return text_col, label_col

def auto_select_threshold(raw_dataset, rating_col="imdb_score", min_samples_per_class=MIN_SAMPLES_PER_CLASS_FOR_AUTO):
    ratings = []
    for ex in raw_dataset:
        try:
            ratings.append(float(ex[rating_col]))
        except Exception:
            pass
    if len(ratings) == 0:
        print("[auto_select_threshold] rating verisi bulunamadı; varsayılan threshold kullanılıyor:", DEFAULT_THRESHOLD)
        return float(DEFAULT_THRESHOLD)

    lo, hi = float(np.min(ratings)), float(np.max(ratings))
    best_thr = DEFAULT_THRESHOLD
    best_balance = float("inf")
    for thr in np.linspace(lo, hi, 41):
        labels = (np.array(ratings) > thr).astype(int)
        counts = np.bincount(labels, minlength=2)
        if counts[0] < min_samples_per_class or counts[1] < min_samples_per_class:
            continue
        ratio = abs(counts[0] - counts[1]) / (counts[0] + counts[1])
        if ratio < best_balance:
            best_balance = ratio
            best_thr = thr

    if best_balance == float("inf"):
        print("[auto_select_threshold] Uyarı: uygun bir threshold bulunamadı; varsayılan kullanılacak:", DEFAULT_THRESHOLD)
        return float(DEFAULT_THRESHOLD)

    print(f"[auto_select_threshold] seçilen threshold: {best_thr:.3f} (balance ratio: {best_balance:.3f})")
    return float(best_thr)

def load_and_prepare_dataset(data_path=DATA_PATH, test_size=0.2, auto_threshold=True):
    print(f"CSV yükleniyor: {data_path}")
    raw = load_dataset("csv", data_files={"full": data_path})["full"]

    text_col, label_col = infer_text_and_label_candidates(raw.column_names)
    if text_col is None:
        raise ValueError("Text kolonu bulunamadı.")
    if label_col is None:
        raise ValueError("Label kolonu bulunamadı.")

    print(f"Seçilen text kolon: {text_col}, label kolon (raw): {label_col}")

    threshold = auto_select_threshold(raw, rating_col=label_col) if auto_threshold else DEFAULT_THRESHOLD
    print(f"Using RATING_THRESHOLD = {threshold}")

    def normalize_label(example):
        val = float(example[label_col])
        return {"label": 1 if val > threshold else 0}

    ds = raw.map(normalize_label)

    if text_col != "text":
        ds = ds.rename_column(text_col, "text")

    ds = ds.map(lambda x: {"text": x["text"], "label": x["label"]})
    ds = ds.remove_columns([c for c in ds.column_names if c not in ("text", "label")])

    ds = ds.shuffle(seed=RANDOM_SEED)
    split = ds.train_test_split(test_size=test_size, seed=RANDOM_SEED)
    train_ds = split["train"]
    eval_ds = split["test"]

    if UNDERSAMPLE:
        pos = train_ds.filter(lambda x: x["label"] == 1)
        neg = train_ds.filter(lambda x: x["label"] == 0)
        if len(pos) == 0 or len(neg) == 0:
            balanced_train = train_ds
        else:
            min_len = min(len(pos), len(neg))
            pos_sub = pos.shuffle(seed=RANDOM_SEED).select(range(min_len))
            neg_sub = neg.shuffle(seed=RANDOM_SEED).select(range(min_len))
            balanced_train = concatenate_datasets([pos_sub, neg_sub]).shuffle(seed=RANDOM_SEED)
        train_ds = balanced_train

    print(f"Final train boyutu: {len(train_ds)}, eval boyutu: {len(eval_ds)}")
    print("Final train dağılım:", Counter(train_ds["label"]))
    print("Final eval dağılım:", Counter(eval_ds["label"]))
    return train_ds, eval_ds

def setup_tokenizer_and_model(model_name=MODEL_NAME, num_labels=2):
    print(f"Model ve tokenizer yükleniyor: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    return tokenizer, model

def tokenize_dataset(dataset, tokenizer, max_length=256):
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding=False, max_length=max_length)
    columns_to_remove = [c for c in dataset.column_names if c not in ("text", "label")]
    tokenized = dataset.map(tokenize_function, batched=True, remove_columns=columns_to_remove)
    if "label" in tokenized.column_names:
        tokenized = tokenized.rename_column("label", "labels")
    return tokenized

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted", zero_division=0)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

def create_training_arguments_safe(output_dir=OUTPUT_DIR):
    base_kwargs = dict(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        report_to=None,
        seed=RANDOM_SEED,
        save_total_limit=2,
    )
    modern_kwargs = dict(
        **base_kwargs,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
    )
    try:
        ta = TrainingArguments(**modern_kwargs)
        return ta
    except TypeError:
        fallback_kwargs = dict(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            logging_dir="./logs",
            logging_steps=10,
            seed=RANDOM_SEED,
        )
        ta = TrainingArguments(**fallback_kwargs)
        return ta

def train_model_with_trainer():
    seed_everything()
    train_dataset, eval_dataset = load_and_prepare_dataset()
    tokenizer, model = setup_tokenizer_and_model()
    train_tokenized = tokenize_dataset(train_dataset, tokenizer)
    eval_tokenized = tokenize_dataset(eval_dataset, tokenizer)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    training_args = create_training_arguments_safe()
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=eval_tokenized,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.evaluate()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    return trainer, model, tokenizer

if __name__ == "__main__":
    trainer, model, tokenizer = train_model_with_trainer()
