# Setup Guide

This guide will help you set up the Cyber Cypher project on any machine.

## Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd cyber-cypher
```

### 2. Create a Virtual Environment

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**On Windows:**
```bash
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt when the virtual environment is activated.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all the required packages listed in `requirements.txt`.

### 5. Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   **On Windows (if cp doesn't work):**
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file and fill in your actual values:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: Your database connection string
   - Any other required environment variables

### 6. Initialize the Database (if applicable)

If your project uses a database with migrations:

```bash
alembic upgrade head
```

### 7. Run the Application

**Backend API:**
```bash
uvicorn supervisor.api.main:app --reload
```

**Frontend UI (if applicable):**
```bash
cd ui
npm install
npm run dev
```

## Verification

To verify everything is set up correctly, you can run:

```bash
python demo.py
```

Or run the tests:

```bash
pytest
```

## Deactivating the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:

```bash
deactivate
```

## Troubleshooting

### Issue: `pip` command not found
- Make sure Python is installed and added to your PATH
- Try using `python -m pip` instead of `pip`

### Issue: Permission errors during installation
- On Windows: Run your terminal as Administrator
- On macOS/Linux: Use `pip install --user -r requirements.txt`

### Issue: Virtual environment activation not working
- On Windows: You may need to enable script execution:
  ```bash
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Issue: Module not found errors
- Make sure your virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Updating Dependencies

If you install new packages, update the requirements file:

```bash
pip freeze > requirements.txt
```

## Notes

- **Never commit your `.env` file** - it contains sensitive information
- Always activate the virtual environment before working on the project
- The `venv/` directory is not tracked by git - it will be created fresh on each machine
- Keep your `requirements.txt` file up to date when adding new dependencies
