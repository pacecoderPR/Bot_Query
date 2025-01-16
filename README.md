# Web Query

`Web Query` is a web content search tool built with React for the frontend and Python for the backend. This tool allows users to search content across websites and retrieve relevant results using Weaviate for semantic search.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Keys](#api-keys)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [Technologies Used](#technologies-used)
- [Installing Python Dependencies](#installing-python-dependencies)

---

## Prerequisites

- Node.js (v14 or above) for frontend development.
- Python (v3.7 or above) for backend (if using FastAPI, Flask, or Django).
- Weaviate (self-hosted or cloud-based).
- An API key for Weaviate.

## Setup Instructions

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/web-query.git
   cd web-query
2. **Create a virtual environment (recommended)**:

```bash

python -m venv venv
 venv/bin/activate  # On Windows, use `venv\Scripts\activate`
 ```
3. **Install Python dependencies**: Run the following command to install backend dependencies from requirements.txt:

```bash

pip install -r requirements.txt
Install backend dependencies: Depending on whether you are using FastAPI, Flask, or Django, install their respective dependencies:
```



# Example for FastAPI
```bash
pip install fastapi uvicorn
```
Then implement the necessary API to handle search queries (refer to the example in the previous sections).

5. **Weaviate Setup**:

You can either host Weaviate locally via Docker or use Weaviate Cloud.
If you're using Weaviate Cloud, generate an API key (detailed below).
Frontend Setup
Navigate to the frontend directory:

```bash

cd client
```
Install frontend dependencies: Ensure you have npm installed, then run:


```bash

npm install
```

Sign up for Weaviate Cloud: Visit Weaviate Cloud and create an account.

Generate the API key:

Navigate to the Weaviate dashboard.
Generate an API key to use for authenticating requests to Weaviate.
Weaviate Cloud and Local Setup: You can either use 
Create a .env file in the backend directory.
Add your environment variables to the .env file:
plaintext
```bash
WEAVIATE_API_KEY=your_weaviate_api_key_here
BACKEND_URL=http://127.0.0.1:8000
```
For example:

WEAVIATE_API_KEY: The API key generated from Weaviate Cloud.
BACKEND_URL: The URL of your backend server.
Make sure not to commit .env files or any sensitive information to public repositories.

Installing Python Dependencies
Create the requirements.txt file:

Make sure to specify all dependencies necessary for your backend, including FastAPI, requests, etc. For example:
plaintext
Copy
Edit
fastapi==0.73.0
uvicorn==0.17.0
requests==2.26.0
python-dotenv==0.19.1
Install the dependencies: Once you've created your requirements.txt, install all dependencies with:

```bash

pip install -r requirements.txt
```
Running the Project
Start the Backend API Server: Depending on your backend (FastAPI, Flask, Django), you can run:

For FastAPI:

```bash
uvicorn app:app --reload
```
Start the React Frontend: Navigate to the frontend directory and run:

```bash

npm start
```
Open in Browser: Navigate to http://localhost:3000 to see the search tool in action.

Testing
Once the project is running:

Enter the URL and search query in the input fields.
Click the "Search" button.
The search results will be displayed as cards.
Click "See HTML" to view the raw HTML content.
Technologies Used
Frontend: React, CSS, Axios for HTTP requests, React Icons.
Backend: Python (FastAPI/Flask/Django).
Search Engine: Weaviate (Cloud or self-hosted).
This README.md provides all the information you need to get your project running, including setting up API keys, creating environment variables, and managing dependencies through requirements.txt.

