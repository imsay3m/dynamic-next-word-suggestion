# Dynamic Next Word Suggestion Web App

![App Screenshot](https://awesomescreenshot.s3.amazonaws.com/image/4502693/55923982-40c9424cedf71682440728f48429e625.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJSCJQ2NM3XLFPVKA%2F20250812%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250812T111022Z&X-Amz-Expires=28800&X-Amz-SignedHeaders=host&X-Amz-Signature=04cc4152b1eb4bbd065e43b15f6ee1dc30c955c48ef0128becdfad29bdb400f7)

A full-stack web application that provides real-time phrase suggestions. This tool allows users to select from pre-loaded datasets, upload their own text files, or paste custom text to receive relevant autocomplete-style predictions. The prediction logic is based on a fast phrase-matching retrieval system.

The application also features an LSTM neural network that can be trained on any text corpus for experimental single-word prediction.

## ✨ Core Features

-   **Dynamic Dataset Discovery**: Automatically finds and lists all `.txt` datasets in the `data/` directory.
-   **File Upload**: Users can upload their own `.txt` corpus directly through the web interface.
-   **Custom Text Input**: A text area allows users to paste any text for on-the-fly use.
-   **Real-time Next Word Suggestions**: Uses a fast retrieval model to provide instant and relevant phrase completions.
-   **LSTM Model Training (Local Only)**: Includes a TensorFlow/Keras LSTM model for experimental next-word prediction.
-   **Responsive UI**: The interface is designed to be clean, modern, and usable across desktop, tablet, and mobile devices.
-   **Dockerized**: Comes with a `Dockerfile` and `docker-compose.yml` for easy and consistent local development and deployment.

## 🔧 Tech Stack

-   **Backend**: FastAPI
-   **Machine Learning**: TensorFlow / Keras
-   **Frontend**: HTML, CSS, JavaScript (with Font Awesome for icons)
-   **Deployment**: Docker, Render (or any other platform that supports Docker)

## ⚠️ Important Note on Training

The live version of this application deployed on services like Render runs on a server with limited CPU and RAM resources. Training a neural network is a computationally intensive task.

**Therefore, the LSTM model training feature is intended for local use only.**

-   **Live Deployed App**: The "Train Model" button will likely be slow or may cause the server to time out and crash. The primary purpose of the live app is to showcase the fast **next word retrieval** predictions.
-   **Local Development**: To train the LSTM model on a new dataset, please run the application on your local machine using Docker. This will give you access to your computer's full processing power for a much faster and more reliable training experience.

## 🚀 Getting Started (Local Development)

Follow these steps to run the application on your local machine. This is the recommended way to use the model training features.

### Prerequisites

-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
-   [Git](https://git-scm.com/) installed.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/imsay3m/dynamic-next-word-suggestion
    cd dynamic-next-word-suggestion
    ```

2.  **Build and run with Docker Compose:**
    This is the easiest and recommended method. It uses the `docker-compose.yml` file to configure and run the application with live code reloading.

    ```bash
    docker-compose up --build
    ```

    To run it in the background (detached mode), use:

    ```bash
    docker-compose up -d --build
    ```

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8000`.

Your application is now running. Any changes you make to the source code will be reflected instantly, with the server automatically restarting.

### Stopping the Application

To stop the containers managed by Docker Compose, run:

```bash
docker-compose down
```

## 📝 How to Use the App

1.  **Select a Dataset**: Choose a pre-loaded dataset from the dropdown menu.
2.  **Upload Your Own**: Use the "Upload New Dataset" form to upload any `.txt` file. It will automatically appear in the dropdown.
3.  **Use Custom Text**: Select the "Custom (Manual Input)" option and paste text into the `textarea` that appears.
4.  **Train the Model (Local Only)**: Click the **Train Model** button to train the LSTM. The training progress will appear in the logs.
5.  **Get Predictions**: Once a model is trained, start typing in the "Prediction Input" box to get next-word suggestions. For non-trained datasets, you will get instant next word-matching suggestions.

## 📁 Project Structure

```
.
├── app.py             # FastAPI backend logic
├── model.py           # LSTM model definition and training
├── utils.py           # Helper functions
├── Dockerfile         # Blueprint for the Docker image
├── docker-compose.yml # Configuration for local development
├── requirements.txt   # Python dependencies
├── .gitignore         # Files to ignore for Git
├── .dockerignore      # Files to ignore for Docker builds
├── data/              # Folder for .txt datasets
├── models/            # Folder for trained models
├── static/            # CSS and JavaScript files
└── templates/         # HTML templates
```

## 📦 Adding New Datasets

Simply add any `.txt` file to the `data/` directory. The application will automatically detect it on the next startup. Alternatively, use the file upload feature in the web UI.
