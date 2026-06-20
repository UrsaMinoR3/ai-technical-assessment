# AI Technical Assessment

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Run Locally
`ash
cp infra/.env.example .env
docker-compose -f infra/docker-compose.yml up --build
`

### API Docs
Once running, visit http://localhost:8000/docs
"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\README.md" -Encoding utf8

# api/app files
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\api\app\routers\.gitkeep" -Encoding utf8
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\api\app\services\.gitkeep" -Encoding utf8
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\api\app\models\.gitkeep" -Encoding utf8
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\api\app\schemas\.gitkeep" -Encoding utf8
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\api\app\core\.gitkeep" -Encoding utf8
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\tests\.gitkeep" -Encoding utf8
@".gitkeep"@ | Out-File -FilePath "c:\Users\Midni\Desktop\Blackpool Project\ai-technical-assessment\docs\.gitkeep" -Encoding utf8

# main.py
@"
from fastapi import FastAPI

app = FastAPI(title="AI Technical Assessment API")

@app.get("/health")
def health():
    return {"status": "ok"}
