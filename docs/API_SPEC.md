# API Spec (เติมของจริง)

## REST
- `GET /health` → `{"status":"ok"}`
- `POST /process` → body:
  ```json
  {"inputs":[{"type":"audio","uri":"..."}], "options":{"preset":"default"}}
  ```
  response:
  ```json
  {"outputs":[{"type":"text","value":"..."}]}
  ```

## CLI
- `python app.py --input path --out out/ --preset default`
