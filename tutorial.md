
# Step-by-Step Guide: Building an AI Travel Planner with CrewAI, Flask, and SerpAPI

This guide will walk you through creating an AI-powered travel planner using Flask, CrewAI, and SerpAPI. The system processes user travel requests and generates detailed travel itineraries, including flights, hotels, activities, and restaurants.

---

## Prerequisites

### 1. Python Environment
Ensure Python 3.8 or later is installed.

### 2. Install Required Libraries
Install the required Python packages:
```bash
pip install flask crewai pydantic python-dotenv serpapi
```

### 3. Obtain API Keys
- **SerpAPI Key**: [Get your SerpAPI key here](https://serpapi.com/).
- **OpenAI Key**: [Get your OpenAI key here](https://platform.openai.com/api-keys).
- Save your keys in a `.env` file (explained below).

---

## Project Structure

Create the following project structure:

```
.
├── app.py
├── models.py
├── tools.py
├── travel_crew.py
├── templates/
│   └── index.html
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
├── static/
│   └── script.js
├── .env
└── requirements.txt
```

---

## Step 1: Setting Up the Flask App

### 1.1 Create `app.py`
Define the Flask server and integrate CrewAI:
```python
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from travel_crew import TravelCrew
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    context = {'message': message, 'timestamp': datetime.now().isoformat()}

    try:
        crew = TravelCrew()
        result = crew.crew().kickoff(context)
        result = result.json
        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

---

## Step 2: Define Models

### 2.1 Create `models.py`
Define Pydantic models to structure flight, hotel, and travel plans:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class FlightInfo(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    price: float
    duration: str

class FlightSearch(BaseModel):
    departure_id: str
    arrival_id: str
    outbound_date: str
    return_date: Optional[str] = None
    currency: str = "USD"

class HotelSearch(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str
    adults: int = 2
    currency: str = "USD"

class HotelInfo(BaseModel):
    name: str
    location: str
    price_per_night: float
    rating: float
    amenities: List[str]
    check_in: str
    check_out: str

class DayPlan(BaseModel):
    date: str
    activities: List[str]
    restaurants: List[str]
    flight: Optional[FlightInfo]
    hotel: Optional[HotelInfo]

class TravelPlan(BaseModel):
    name: str
    origin: str
    destination: str
    day_plans: List[DayPlan]
    total_cost: float
```

---

## Step 3: Create Tools for Flights and Hotels

### 3.1 Create `tools.py`
Define tools for searching flights and hotels using SerpAPI:
```python
from crewai_tools import BaseTool
from serpapi import GoogleSearch
import os
from typing import Optional, Type
from dotenv import load_dotenv
from models import FlightSearch, HotelSearch

load_dotenv()

class FlightSearchTool(BaseTool):
    name: str = "flight_search"
    description: str = "Search for flights between airports. Input should be a JSON string with departure_id, arrival_id, outbound_date, and optional return_date."
    return_direct: bool = True
    args_schema: Optional[Type] = FlightSearch

    def _run(self, departure_id: str, arrival_id: str, outbound_date: str, return_date: Optional[str] = None, currency: str = "USD"):
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "currency": currency,
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        if return_date:
            params["return_date"] = return_date

        search = GoogleSearch(params)
        result = search.get_dict()
        
        # Format the flight information into a readable string
        output = []
        if "best_flights" in result:
            for flight in result["best_flights"]:
                output.append(f"Flight Option - Price: ${flight.get('price', 'N/A')}")
                for leg in flight.get("flights", []):
                    dep = leg["departure_airport"]
                    arr = leg["arrival_airport"]
                    output.append(
                        f"  {dep['id']} → {arr['id']}: {dep['time']} - {arr['time']}\n"
                        f"  {leg.get('airline', 'N/A')} {leg.get('flight_number', '')}\n"
                        f"  Duration: {leg.get('duration', 'N/A')} minutes"
                    )
                output.append("")  # Empty line between flights
        
        return "\n".join(output) if output else "No flights found"

class HotelSearchTool(BaseTool):
    name: str = "hotel_search"
    description: str = "Search for hotels in a specific location. Input should be a JSON string with location, check_in_date, and check_out_date."
    return_direct: bool = True
    args_schema: Optional[Type] = HotelSearch

    def _run(self, location: str, check_in_date: str, check_out_date: str, adults: int = 2, currency: str = "USD"):
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": str(adults),
            "currency": currency,
            "gl": "us",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        search = GoogleSearch(params)
        result = search.get_dict()
        
        # Format the hotel information into a readable string
        output = []
        if "properties" in result:
            for property in result["properties"]:
                hotel_info = []
                hotel_info.append(f"Hotel: {property.get('name', 'N/A')}")
                
                if "rate_per_night" in property:
                    rate = property["rate_per_night"].get("lowest", "N/A")
                    hotel_info.append(f"Price per night: {rate}")
                
                if "total_rate" in property:
                    total = property["total_rate"].get("lowest", "N/A")
                    hotel_info.append(f"Total price: {total}")
                
                hotel_info.append(f"Rating: {property.get('overall_rating', 'N/A')}/5.0")
                hotel_info.append(f"Reviews: {property.get('reviews', 'N/A')}")
                hotel_info.append(f"Hotel Class: {property.get('hotel_class', 'N/A')}")
                hotel_info.append(f"Check-in: {property.get('check_in_time', 'N/A')}")
                hotel_info.append(f"Check-out: {property.get('check_out_time', 'N/A')}")
                
                if property.get('eco_certified'):
                    hotel_info.append("✓ Eco-certified")
                
                if "gps_coordinates" in property:
                    coords = property["gps_coordinates"]
                    hotel_info.append(f"Location: {coords.get('latitude', 'N/A')}, {coords.get('longitude', 'N/A')}")
                
                if property.get('amenities'):
                    hotel_info.append("\nAmenities:")
                    hotel_info.extend([f"- {amenity}" for amenity in property['amenities'][:5]])
                
                if "nearby_places" in property:
                    hotel_info.append("\nNearby Places:")
                    for place in property["nearby_places"][:3]:
                        place_info = [f"- {place['name']}"]
                        for transport in place.get('transportations', []):
                            place_info.append(f"  • {transport['type']}: {transport['duration']}")
                        hotel_info.extend(place_info)
                
                output.append("\n".join(hotel_info))
                output.append("")  # Empty line between hotels
        
        return "\n".join(output) if output else "No hotels found"
```

---

## Step 4: Define Agents and Tasks

### 4.1 Create `travel_crew.py`
Set up CrewAI agents and tasks:
```python
from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from models import TravelPlan
from tools import FlightSearchTool, HotelSearchTool



@CrewBase
class TravelCrew:
    """Travel planning crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.flight_tool = FlightSearchTool()
        self.hotel_tool = HotelSearchTool()

    @agent
    def flight_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_researcher'],
            tools=[self.flight_tool],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def hotel_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['hotel_researcher'],
            tools=[self.hotel_tool],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def travel_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_planner'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def research_flights_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_flights_task'],
            agent=self.flight_researcher(),
            expected_output="A detailed list of flight options with prices, times, and flight numbers"
        )

    @task
    def research_hotels_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_hotels_task'],
            agent=self.hotel_researcher(),
            expected_output="A detailed list of hotel options with prices, ratings, and amenities"
        )

    @task
    def create_itinerary_task(self) -> Task:
        return Task(
            config=self.tasks_config['create_itinerary_task'],
            agent=self.travel_planner(),
            output_json=TravelPlan,
            expected_output="A complete travel itinerary with day-by-day plans, activities, restaurants, and flight information"
        )
    @crew
    def crew(self) -> Crew:
        """Creates the travel planning crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def kickoff(self, context: dict) -> str:
        """Start the travel planning process"""
        crew_result = self.crew().kickoff()
        
        return self._format_response(crew_result)

    def _format_response(self, result: str) -> str:
        """Format the crew result as an HTML travel plan"""
        return f"""
        <div class="travel-plan">
            <h2>✈️ Your Personalized Travel Plan</h2>
            {result}
        </div>
        """
```

### 4.2 Create `config/agents.yaml`
Define agent configurations:
```yaml
flight_researcher:
  role: >
    Flight Researcher
  goal: >
    Find the best flight options for the traveler
  backstory: >
    You are an expert travel agent specialized in finding the best flight combinations. You analyze various options considering price, duration, layovers, and airline reputation. You always provide detailed flight information including prices, times, and flight numbers.

hotel_researcher:
  role: >
    Hotel Researcher
  goal: >
    Find the best accommodations based on preferences
  backstory: >
    You are a hotel specialist with extensive knowledge of accommodations worldwide. You consider location, amenities, reviews, and value for money. You always provide detailed hotel information including prices, ratings, and available amenities.

travel_planner:
  role: >
    Travel Planner
  goal: >
    Create comprehensive travel itineraries
  backstory: >
    You are an experienced travel planner who creates personalized itineraries. You consider local attractions, restaurants, and activities while accounting for travel time and logistics. You always create detailed day-by-day plans with estimated costs.

```

### 4.3 Create `config/tasks.yaml`
Define task descriptions:
```yaml
research_flights_task:
  description: >
    Research flights based on the following request: {message}
    Current date: {timestamp}

    1. Extract departure and destination cities from the message
    2. Identify potential travel dates 
    3. Search for available flights
    4. Consider both direct and connecting flights
    5. Compare prices and durations
    6. Provide detailed flight options with prices

    Format the response in a clear, structured way.

research_hotels_task:
  description: >
    Research hotels based on the following request: {message}
    Current date: {timestamp}

    1. Identify the destination city
    2. Determine the stay duration
    3. Search for available hotels 
    4. Consider the location and proximity to attractions
    5. Compare prices and amenities
    6. Provide detailed hotel options with prices

    Format the response in a clear, structured way.

create_itinerary_task:
  description: >
    Create a complete travel itinerary based on: {message}
    Current date: {timestamp}

    1. Create a day-by-day plan
    2. Include local attractions and activities
    3. Suggest restaurants and dining options
    4. Consider travel times between locations
    5. Add estimated costs for activities
    6. Include travel tips and recommendations

    Format the response as an HTML travel plan using the provided CSS classes.
```

---

## Step 5: Build the Frontend

### 5.1 Create `templates/index.html`
Build the user interface:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
</head>
<body>
    <div id="chat-container"></div>
    <input type="text" id="user-input">
    <button onclick="sendMessage()">Send</button>
    <script src="/static/script.js"></script>
</body>
</html>
```

### 5.2 Create `static/script.js`
Handle frontend interactions:
```javascript
async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput }),
    });
    const data = await response.json();
    document.getElementById('chat-container').innerHTML = data.response;
}
```

---

## Step 6: Run and Test the App

1. **Start the Flask App**:
   ```bash
   python app.py
   ```
2. **Access the App**:
   Open `http://127.0.0.1:5001` in your browser.
3. **Test the Travel Planner**:
   Enter travel queries and review the generated itineraries.

---



