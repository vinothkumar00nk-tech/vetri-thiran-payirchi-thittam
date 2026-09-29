# ComicCraft

ComicCraft is a complete AI-assisted five-panel comic generator.

## Stack

- FastAPI + Jinja2 backend
- Vanilla HTML/CSS/JavaScript frontend
- Gemini Flash: panel/story outline generation
- Gemini Pro: comic script generation
- Hugging Face Inference API: panel image generation
- Pillow: image handling
- fpdf2: PDF export
- Pydantic Settings: configuration
- Pytest: automated tests

The application also includes a `mock` image provider. This lets you run and test the full application without an image API key. For real AI images, use `IMAGE_PROVIDER=hf`.

## 1. Requirements

- Python 3.11+ recommended
- VS Code
- Internet connection for Gemini/Hugging Face API calls

## 2. Create the environment

### Windows PowerShell

```powershell
cd ComicCraft
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```bat
cd ComicCraft
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure `.env`

Copy `.env.example` to `.env`.

For a real AI run, add:

```env
GEMINI_API_KEY=your_gemini_key
HF_API_KEY=your_huggingface_token
IMAGE_PROVIDER=hf
```

For a no-key local UI/test run:

```env
IMAGE_PROVIDER=mock
```

`mock` generates attractive placeholder panels with Pillow and does not call an external image service.

## 4. Run

```bash
python run.py
```

Open:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## 5. Test

```bash
pytest -q
```

## 6. API example

```http
POST /generate-comic/json
Content-Type: application/json

{
  "story_prompt": "A young inventor discovers a machine that can freeze time.",
  "character_name": "Alex",
  "setting": "Futuristic city",
  "tone": "Adventure",
  "art_style": "Modern comic book"
}
```

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       ├── exporters.py
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       └── layout_builder.py
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/.gitkeep
│   ├── generated/.gitkeep
│   └── exports/.gitkeep
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── tests/
│   ├── __init__.py
│   ├── test_layout.py
│   └── test_routes.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## Troubleshooting

### `GEMINI_API_KEY is missing`

Create `.env` from `.env.example` and set the key.

### `HF_API_KEY is missing`

Either set a Hugging Face token or temporarily use:

```env
IMAGE_PROVIDER=mock
```

### PDF has no image

Generate the comic again and make sure the panel files exist under `static/panels/`.

### Port already in use

Change:

```env
PORT=8001
```

and run again.

## Security

Never commit `.env` or API keys to Git. The included `.gitignore` already excludes `.env`.
