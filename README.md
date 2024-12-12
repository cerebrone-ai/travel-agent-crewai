
# AI Travel Planner with CrewAI and Flask

## Overview
The **AI Travel Planner** is a Flask-based web application that uses **CrewAI** and **SerpAPI** to create personalized travel itineraries. The application generates detailed travel plans, including:
- Flight options
- Hotel recommendations
- Day-by-day activity plans
- Local dining suggestions

## Features
- 🛫 **Flight Search**: Find flights based on user input (departure, destination, dates).
- 🏨 **Hotel Recommendations**: Discover accommodations tailored to preferences and budgets.
- 🗓️ **Day-by-Day Itineraries**: Create comprehensive plans including activities and dining.
- 💰 **Cost Estimation**: Provide total estimated travel costs.

## Tech Stack
- **Backend**: Flask, CrewAI
- **Frontend**: HTML, TailwindCSS, JavaScript
- **APIs**: SerpAPI for flight and hotel data
- **Modeling**: Pydantic for data validation

## Project Structure
```
.
├── app.py                 # Main Flask app
├── models.py              # Pydantic models for data validation
├── tools.py               # Tools for flight and hotel search
├── travel_crew.py         # CrewAI agents and tasks
├── templates/
│   └── index.html         # Frontend HTML template
├── static/
│   └── script.js          # Frontend JavaScript
├── config/
│   ├── agents.yaml        # Agent configurations
│   └── tasks.yaml         # Task configurations
├── .env                   # API keys and environment variables
└── requirements.txt       # Python dependencies
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-travel-planner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file and add your API keys:
```
SERPAPI_API_KEY=your_serpapi_key
OPENAI_API_KEY=your_openai_key
```

### 4. Run the Application
Start the Flask server:
```bash
python app.py
```

Access the app in your browser at [http://127.0.0.1:5001](http://127.0.0.1:5001).

## How It Works
1. **User Input**: Enter a travel request (e.g., "Plan a 5-day trip to Paris from New York in March").
2. **AI Processing**:
   - Flight and hotel options are fetched using SerpAPI.
   - Itinerary is generated using CrewAI agents and tasks.
3. **Output**: A detailed travel plan is displayed, including flights, hotels, activities, and costs.

## Future Enhancements
- 🚗 **Car Rentals**: Add car rental suggestions.
- 🌍 **Local Guides**: Provide localized tips and cultural insights.
- 📈 **Budget Comparison**: Show plans for different budget levels.

## License
This project is licensed under the MIT License.