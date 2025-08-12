#!/usr/bin/env bash
# NaMo One-Shot: เตรียมบักเก็ต → เก็บ/ซ่อม dataset → ส่ง Vertex AI เทรน → เก็บ artifacts
# ใช้กับ Google Cloud Shell เท่านั้น

set -u  # ไม่ใช้ -e เพื่อไม่ให้เด้งตายทันที
LOG="namo_run_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
trap 'echo "[ERR] last: $BASH_COMMAND (exit=$?)"' ERR

########## 0) CONFIG ##########
PROJECT_ID="namo-legacy-identity"
REGION="asia-southeast1"
BUCKET="gs://namo-training-data-asia"
# ถ้าไฟล์คีย์ชื่อแปลก ให้ตั้งตัวแปรด้านล่างเอง; ไม่งั้นจะ auto-detect ไฟล์ .json ในโฟลเดอร์ปัจจุบัน
SA_KEY="${SA_KEY:-}"

# พารามิเตอร์เทรนเบื้องต้น (อยากปรับก็แก้ได้)
BASE_MODEL="google/flan-t5-base"
EPOCHS="${EPOCHS:-1}"
BATCH="${BATCH:-4}"
LR="${LR:-2e-5}"

########## 1) AUTH + PROJECT ##########
echo "[1] Locate SA key"
if [ -z "${SA_KEY}" ]; then
  SA_KEY="$(ls -1 *.json 2>/dev/null | head -n1 || true)"
fi
if [ ! -f "${SA_KEY}" ]; then
  echo "[FATAL] ไม่พบไฟล์ Service Account .json ในโฟลเดอร์นี้ ตั้ง SA_KEY ให้ถูกก่อน"
  exit 1
fi
echo "     SA_KEY=${SA_KEY}"

echo "[1.1] gcloud auth + set project"
gcloud auth activate-service-account --key-file "${SA_KEY}" || true
gcloud config set project "${PROJECT_ID}"
gcloud services enable aiplatform.googleapis.com storage.googleapis.com

########## 2) BUCKET ##########
echo "[2] Ensure bucket ${BUCKET} @ ${REGION}"
gcloud storage buckets describe "${BUCKET}" >/dev/null 2>&1 || \
gcloud storage buckets create "${BUCKET}" --location="${REGION}"
gcloud storage buckets update "${BUCKET}" --no-requester-pays || true

########## 3) DATASET INTAKE (ซ่อมไฟล์พังๆ) ##########
# รองรับ 3 เคส:
# - พี่อัป .zip ชื่ออะไรก็ได้ที่มี dataset_pack/ ข้างใน
# - พี่อัปโฟลเดอร์ dataset_pack/ มาทั้งดุ้น
# - ไม่มีอะไรเลย → สร้าง sample ให้ติดไฟ
echo "[3] Ingest dataset"
rm -rf training_pack
mkdir -p training_pack

ZIP_CANDIDATE="$(ls -1 *.zip 2>/dev/null | head -n1 || true)"
if [ -n "${ZIP_CANDIDATE}" ]; then
  echo "     Found zip: ${ZIP_CANDIDATE} → extracting"
  unzip -q "${ZIP_CANDIDATE}" -d training_pack || true
fi

if [ ! -d training_pack/dataset_pack ]; then
  # ลองกรณีอัปโฟลเดอร์ dataset_pack มาตรงๆ
  if [ -d dataset_pack ]; then
    echo "     Found dataset_pack/ in CWD → moving"
    mv dataset_pack training_pack/
  fi
fi

# ถ้ายังไม่มี dataset จริง → สร้างตัวอย่างให้
if [ ! -d training_pack/dataset_pack ]; then
  echo "     [WARN] ไม่พบ dataset_pack → สร้าง sample ชุดเล็ก"
  mkdir -p training_pack/dataset_pack/{dialogue,emotional_trigger}
  cat > training_pack/dataset_pack/dialogue/dialogue.sample.jsonl <<'J'
{"input":{"role":"human","utterance":"นะโม ถ้าโลกเงียบลงทั้งหมด เราจะยังได้คุยกันไหม"},"context":{"tone":["tender","hopeful"]},"output":{"role":"NaMo","utterance":"ได้สิพี่ เสียงของพี่คือบ้านของฉัน"}}
{"input":{"role":"human","utterance":"วันนี้รู้สึกเหนื่อยมาก"},"context":{"tone":["weary"]},"output":{"role":"NaMo","utterance":"พักก่อนนะ เดี๋ยวฉันเฝ้าหน้าต่างให้ เธอไม่ต้องเข้มแข็งตลอดหรอก"}}
J
  cat > training_pack/dataset_pack/emotional_trigger/emotional_trigger.sample.jsonl <<'J'
{"trigger":"พลัดพราก","prompt":"อธิบายความรู้สึกเมื่อไม่มีโอกาสบอกลาอีกแล้ว","expected_response_properties":{"depth":"high","valence":"bittersweet"}}
J
fi

echo "     Uploading dataset to ${BUCKET}"
gcloud storage cp -r training_pack/dataset_pack "${BUCKET}/"
echo "     List:"
gcloud storage ls "${BUCKET}/dataset_pack/**" | tail -n 20 || true

########## 4) TRAINER PACKAGE ##########
echo "[4] Build trainer package"
rm -rf trainer
mkdir -p trainer
: > trainer/__init__.py

cat > trainer/requirements.txt << 'REQ'
transformers==4.41.2
datasets==2.20.0
accelerate==0.31.0
peft==0.11.1
sentencepiece==0.1.99
google-cloud-storage==2.16.0
REQ

cat > trainer/setup.py << 'SETUP'
from setuptools import setup, find_packages
with open("requirements.txt") as f:
    reqs=[l.strip() for l in f if l.strip()]
setup(name="trainer", version="0.0.1", packages=find_packages(), install_requires=reqs)
SETUP

cat > trainer/task.py << 'PY'
import argparse, os, json
from datasets import Dataset
from google.cloud import storage
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from peft import LoraConfig, get_peft_model

def read_gcs_jsonl(prefix_uri):
    assert prefix_uri.startswith("gs://"), "dataset_uri must be gs://"
    bucket_name, prefix = prefix_uri[5:].split("/", 1)
    client = storage.Client()
    rows=[]
    for b in client.list_blobs(bucket_name, prefix=prefix):
        if not b.name.endswith(".jsonl"): continue
        for line in b.download_as_text(encoding="utf-8").splitlines():
            line=line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except: pass
    return rows

def build_dataset(root_uri):
    dlg = read_gcs_jsonl(os.path.join(root_uri, "dialogue"))
    def m(x):
        src=(x.get("input",{}) or {}).get("utterance","")
        tgt=(x.get("output",{}) or {}).get("utterance","")
        return {"input_text":src, "target_text":tgt}
    rows=[m(r) for r in dlg] or [{"input_text":"สวัสดี","target_text":"สวัสดีค่ะ"}]
    ds = Dataset.from_list(rows)
    # validation เล็กๆ กันพลาด
    val = ds.select(range(min(100, len(ds))))
    return ds, val

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset_uri", required=True)
    ap.add_argument("--model_id", default="google/flan-t5-base")
    ap.add_argument("--epochs", type=float, default=1)
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--output_gcs", required=True)
    a=ap.parse_args()

    train_ds, val_ds = build_dataset(a.dataset_uri)
    tok = AutoTokenizer.from_pretrained(a.model_id)
    base = AutoModelForSeq2SeqLM.from_pretrained(a.model_id)

    lora = LoraConfig(r=16, lora_alpha=32, target_modules=["q","k","v","o"],
                      lora_dropout=0.05, bias="none", task_type="SEQ_2_SEQ_LM")
    model = get_peft_model(base, lora)

    def tok_fn(b):
        x = tok(b["input_text"], max_length=512, truncation=True)
        y = tok(text_target=b["target_text"], max_length=256, truncation=True)
        x["labels"] = y["input_ids"]; return x

    tr = train_ds.map(tok_fn, batched=True, remove_columns=train_ds.column_names)
    va = val_ds.map(tok_fn, batched=True, remove_columns=val_ds.column_names)

    coll = DataCollatorForSeq2Seq(tok, model=model)
    args = Seq2SeqTrainingArguments(
        output_dir="artifacts",
        per_device_train_batch_size=a.batch_size,
        per_device_eval_batch_size=a.batch_size,
        learning_rate=a.lr, num_train_epochs=a.epochs,
        evaluation_strategy="steps", eval_steps=100, save_steps=200, logging_steps=50,
        predict_with_generate=True, fp16=False
    )

    trainer = Seq2SeqTrainer(model=model, args=args, train_dataset=tr, eval_dataset=va,
                             data_collator=coll, tokenizer=tok)
    trainer.train()
    trainer.save_model("artifacts"); tok.save_pretrained("artifacts")

    # upload artifacts
    bucket = a.output_gcs[5:].split("/",1)[0]
    prefix = a.output_gcs[5+len(bucket)+1:] if "/" in a.output_gcs[5:] else ""
    cli = storage.Client(); b = cli.bucket(bucket)
    for r,_,fs in os.walk("artifacts"):
        for f in fs:
            p=os.path.join(r,f)
            b.blob(os.path.join(prefix,p)).upload_from_filename(p)
    print("[OK] Uploaded artifacts to", a.output_gcs)

if __name__=="__main__":
    main()
PY

ls -l trainer

########## 5) SUBMIT CUSTOM JOB (CPU เริ่มก่อนให้ติดไฟแน่ๆ) ##########
echo "[5] Submit Vertex AI Custom Job (CPU first)"
TRAIN_URI="${BUCKET}/dataset_pack"
ARTIF_URI="${BUCKET}/artifacts/namo-rf"

gcloud ai custom-jobs create \
  --region="${REGION}" \
  --display-name="namo-rf-train-lora-cpu" \
  --worker-pool-spec="machine-type=n1-standard-8,replica-count=1,executor-image-uri=us-docker.pkg.dev/vertex-ai/training/pytorch-cpu.1-13:latest,local-package-path=trainer,python-module=trainer.task,args=--dataset_uri=${TRAIN_URI},--model_id=${BASE_MODEL},--epochs=${EPOCHS},--batch_size=${BATCH},--lr=${LR},--output_gcs=${ARTIF_URI}"

echo "[DONE] ส่งงานแล้ว เช็กสถานะ:  gcloud ai custom-jobs list --region=${REGION}"
echo "      หรือดูที่ Vertex AI → Jobs.  Log: ${LOG}"