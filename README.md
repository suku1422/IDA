# IDA Project

## Overview
The Instructional Design Agent (IDA) is a web application designed to assist instructional designers in creating e-learning courses. It provides tools for gathering context, analyzing content, generating outlines, creating storyboards, and developing assessments.

## Project Structure
```
ida-project
├── src
│   ├── __init__.py
│   ├── auth.py
│   ├── db_manager.py
│   ├── openai_client.py
│   ├── config.py
│   └── components
│       ├── __init__.py
│       ├── context_gatherer.py
│       ├── content_analyzer.py
│       ├── outline_generator.py
│       ├── storyboard_generator.py
│       └── assessment_creator.py
├── main.py
├── .env
├── client_secrets.json
├── requirements.txt
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd ida-project
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
- Create a `.env` file in the root directory and add your environment variables, including API keys and database settings.
- Obtain the `client_secrets.json` file from the Google Cloud Console for OAuth authentication.

## Usage
1. Run the application:
   ```
   streamlit run main.py --server.port=8501
   ```
2. Follow the on-screen instructions to log in and start creating your e-learning course.

## Features
- User authentication via Google OAuth.
- Context gathering for instructional design.
- Content analysis to identify gaps.
- Structured content outline generation.
- Storyboard creation for course presentation.
- Final assessment generation with multiple-choice questions.

## License
This project is licensed under the MIT License. See the LICENSE file for details.