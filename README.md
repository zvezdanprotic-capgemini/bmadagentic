# BMAD - Business Model Assistance and Development

A multi-agent system based on the BMad-Method, featuring a FastAPI backend and React frontend.

## Project Structure

- `bmad-backend/`: FastAPI backend with LangChain and Azure OpenAI integration
- `bmad-frontend/`: React frontend (Vite) for the chat interface

## Prerequisites

- Python 3.9+ (for backend)
- Node.js 18+ (for frontend)
- Azure OpenAI API access

## Setup and Running Instructions

### Backend Setup

1. Navigate to the backend directory:

```bash
cd bmad-backend
```

2. Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   
Create a `.env` file in the `bmad-backend` directory with the following content:

```
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"
AZURE_OPENAI_ENDPOINT="your_endpoint_url"
AZURE_OPENAI_API_VERSION="2023-12-01-preview"
```

5. Run the backend server:

```bash
# Make sure you're in the bmad-backend directory
PYTHONPATH=. ./venv/bin/python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at http://localhost:8000.

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd bmad-frontend
```

2. Install dependencies:

```bash
npm install
```

3. Set up environment variables:

Create a `.env` file in the `bmad-frontend` directory with:

```
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173.

## Testing the Application

1. Make sure both backend and frontend servers are running.
2. Open your browser and go to http://localhost:5173.
3. You should see the BMAD Agentic System interface.
4. If the backend status shows "online", you can start interacting with the agents.

## Backend API Endpoints

- `GET /`: Check if the service is running
- `POST /chat`: Send a message to the agent system
- `GET /agents`: Get a list of available agents
- `GET /workflows`: Get a list of available workflows

## Troubleshooting

### Backend Issues

- **Azure OpenAI Connection**: Ensure your Azure OpenAI credentials are correct in the `.env` file.
- **Import Errors**: Make sure PYTHONPATH is set correctly when running the uvicorn server.
- **Port Already in Use**: If port 8000 is already in use, you can specify a different port with the `--port` flag.

### Frontend Issues

- **CORS Errors**: Make sure the backend CORS settings allow requests from your frontend origin.
- **API Connection**: Check that the `VITE_API_BASE_URL` in your `.env` file points to the correct backend URL.

## Testing Azure OpenAI Connection

You can test your Azure OpenAI connection using the included test script:

```bash
cd bmad-backend
python3 AzureTest.py
```

This will attempt to send a simple query to your Azure OpenAI deployment and display the response.

## Development Notes

- The backend uses FastAPI with LangGraph for agent orchestration.
- The frontend is built with React 19 and Vite.
- Communication between frontend and backend uses standard REST API calls.