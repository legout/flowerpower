# FlowerPower Web Application – User Guide

## Introduction
FlowerPower is a web application for managing projects, pipelines, and job queues with real-time, interactive features.

## Installation

### Prerequisites
- Python 3.9+
- Recommended: virtualenv

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-org/flowerpower.git
   cd flowerpower
   ```
2. Install dependencies:
   ```sh
   pip install -r web_ui/requirements.txt
   ```
3. Run the application:
   ```sh
   python web_ui/run.py
   ```
4. Access the web UI at [http://localhost:8000](http://localhost:8000)

## Features

### Project Management
- Create, edit, and manage multiple projects.
- Configure project settings via an intuitive dashboard.
- View project status and overview.

### Pipeline Management
- Add and edit pipelines with configuration options.
- Execute pipelines with custom arguments.
- Queue and schedule pipeline runs.
- Visualize pipeline DAGs interactively.

### Job Queue Operations
- Monitor and manage job queues in real time.
- Start/stop workers and scheduler.
- Pause, resume, or cancel jobs.
- View job execution history and logs.

## Step-by-Step Instructions

### Creating a Project
1. Navigate to the Projects section.
2. Click "New Project".
3. Fill in project details and save.

### Adding a Pipeline
1. Go to the Pipelines section.
2. Click "Add Pipeline".
3. Configure pipeline settings and save.

### Executing a Pipeline
1. Select a pipeline from the list.
2. Click "Run" and provide runtime arguments if needed.
3. Monitor execution status in real time.

### Managing the Job Queue
1. Open the Job Queue section.
2. Start/stop workers or scheduler as needed.
3. Pause, resume, or cancel jobs from the queue.

## Screenshots

> _Screenshots should be added here. Use the application and capture relevant screens for each section._

---
For troubleshooting and advanced usage, see the Developer Guide.