# Curriculum Generation Module

Welcome to the Curriculum Generation Module project! This README file will guide you through the steps to set up the repository and start working on the project. The application is built on Streamlit and can be run both locally or as a hosted app with Streamlit.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setting Up the Repository](#setting-up-the-repository)
  - [Environment Variables](#environment-variables)
  - [Python Environment](#python-environment)
- [Running the Application Locally](#running-the-application-locally)
- [Hosting the Application](#hosting-the-application)

## Prerequisites

Before you begin, make sure you have the following:

- Access to the repository.
- OpenAI API key.
- Google Developer API keys for YouTube Data API and Custom Search API. You can obtain these by following the instructions in the guides:
  - [YouTube Data API Guide](https://developers.google.com/youtube/v3/getting-started)
  - [Custom Search API Guide](https://developers.google.com/custom-search/v1/overview)

## Setting Up the Repository

### Environment Variables

1. **Create a `secrets.toml` file:**

   If you can see the `curriculum_gen_module/.streamlit/secrets.toml.example` file, you'll need to create a `secrets.toml` file based on this example. Populate it with the following values:

   ```toml
   [api_keys]
   OPENAI_API_KEY = "your_openai_api_key"
   GOOGLE_API_KEY = "your_google_api_key"
   YOUTUBE_API_KEY = "your_youtube_api_key"

   [auth]
   PASSWORD = "password"

   [other]
   # Add any other required environment variables here
   ```

### Python Environment

1. **Install Python:**

   Make sure you have Python 3.9, 3.10, or 3.11 installed. You can download it from the [official Python website](https://www.python.org/).

2. **Create a Virtual Environment:**

   Navigate to the `curriculum_gen_module` directory from the base directory of the repository and create a virtual environment:
   Ex. from ~/github/nova-streamlit
   ```sh
   cd curriculum_gen_module
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**

   - On macOS and Linux:

     ```sh
     source venv/bin/activate
     ```

   - On Windows:

     ```sh
     .\venv\Scripts\activate
     ```

4. **Install Dependencies:**

   Install the required packages using `pip`:

   ```sh
   pip install -r requirements.txt
   ```

## Running the Application Locally

To run the application locally, use the following command:

```sh
streamlit run Home.py
```

This will open up your app in the default web browser, and you can start using it immediately.

## Hosting the Application

To host the application through Streamlit, follow these steps:

1. **Deploy on Streamlit Cloud:**

   Go to the [Streamlit Cloud](https://share.streamlit.io/) and deploy the app. Identify the repository and set the "main page" to `Home.py`.

2. **Populate Secrets:**

   In the app settings on Streamlit Cloud, populate the "SECRETS" section with the environment variables mentioned above.

Now your application should be running and accessible through the Streamlit Cloud.

---

If you encounter any issues or have questions, please contact Travis, Jackson, Gokul or Elian in the AI Camp Discord.

Happy coding!
