# Project Setup

## Running the Project


### Backend
By using docker:
```sh
   docker compose up
```

#### OR ,

1. Create a virtual environment:
   ```sh
   python -m venv venv
   ```
2. Activate the virtual environment:
   - **Windows**:
     ```sh
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```sh
     source venv/bin/activate
     ```
3. Install dependencies from `requirements.txt`:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the backend server:
   ```sh
   python run.py
   ```

## OpenAI API Keys
Ensure that OpenAI API keys is added in .env
- **Backend**: Store the API key in an `.env` file or a secure environment variable.

## Tech Stack Used
- **Backend**: FastAPI, Python
- **Programming Languages**: Python