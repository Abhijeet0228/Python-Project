# Network Traffic Analysis Tool Suite

A comprehensive toolset for generating, analyzing, and visualizing network traffic data. This project consists of a desktop GUI application for interactive analysis and a Flask-based REST API for backend data services.

## 📂 Repository Structure

* **`network_analyzer_ui_v2.py`**: A desktop GUI application built with `tkinter` and `matplotlib`. It allows users to visualize traffic patterns, filter data, and view statistical plots.
* **`network_api_backend.py`**: A Flask web server that exposes REST endpoints to retrieve filtered traffic data and aggregated statistics (e.g., protocol counts, top IP addresses).
* **`mock_traffic.csv`**: The dataset used by the tools.
    * *Note*: If this file does not exist, running `network_analyzer_ui_v2.py` will automatically generate it with sample data.

## 🚀 Features

### Desktop GUI (`network_analyzer_ui_v2.py`)
* **Mock Data Generation**: Automatically creates realistic network traffic logs (Timestamp, Source/Dest IP, Protocol, Port, Length).
* **Interactive Visualization**:
    * Bar charts for Top Destination IPs.
    * Protocol distribution analysis.
* **Data Filtering**: Filter traffic logs by specific criteria.
* **Modern UI**: Built with `tkinter` and styled for a clean user experience.

### Backend API (`network_api_backend.py`)
* **RESTful Endpoints**: Serves traffic data in JSON format.
* **Server-Side Filtering**: Supports query parameters to filter data before retrieval.
* **Plotting Data**: Dedicated endpoints that return pre-calculated data for frontend charting libraries.

## 🛠️ Prerequisites

Ensure you have Python 3.x installed. You will need the following dependencies:

💻 Usage
1. Running the Desktop GUI
This is the standalone analyzer tool.

Open your terminal or command prompt.

Run the script:

Bash

python network_analyzer_ui_v2.py
The application window will open. If mock_traffic.csv is missing, it will be created automatically.

2. Running the Backend API
This starts a local web server to serve the traffic data.

Ensure mock_traffic.csv exists (run the GUI script once if it doesn't).

Run the Flask application:

Bash

python network_api_backend.py
The server will start (typically on http://127.0.0.1:5000).

Available API Endpoints:
GET /api/protocols: Get a list of all unique protocols available in the dataset.

GET /api/plot/protocol: Get counts for every protocol (useful for pie charts).

GET /api/plot/top_ips: Get the top 5 destination IP addresses by packet count.

GET /api/data: (Implied) Retrieve raw traffic data records (supports query parameters).

📊 Data Format (mock_traffic.csv)
The CSV data is structured with the following columns:

Timestamp: Date and time of the packet capture.

Source IP: The originating IP address.

Dest IP: The destination IP address.

Protocol: Network protocol (TCP, UDP, HTTP, SSH, etc.).

Length: Size of the packet in bytes.

Port: Destination port number.
