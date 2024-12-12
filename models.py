from pydantic import BaseModel, Field
from typing import List, Optional

class FlightInfo(BaseModel):
    airline: str = Field(..., description="Name of the airline")
    flight_number: str = Field(..., description="Flight number")
    departure_time: str = Field(..., description="Departure time")
    arrival_time: str = Field(..., description="Arrival time")
    price: float = Field(..., description="Price of the flight")
    duration: str = Field(..., description="Duration of flight")


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
    name: str = Field(..., description="Name of the hotel")
    location: str = Field(..., description="Location of the hotel")
    price_per_night: float = Field(..., description="Price per night")
    rating: float = Field(..., description="Hotel rating")
    amenities: List[str] = Field(..., description="List of amenities")
    check_in: str = Field(..., description="Check-in time")
    check_out: str = Field(..., description="Check-out time")

class DayPlan(BaseModel):
    date: str = Field(..., description="Date of the day")
    activities: List[str] = Field(..., description="List of activities")
    restaurants: List[str] = Field(..., description="List of restaurants")
    flight: Optional[FlightInfo] = Field(None, description="Flight information")
    hotel: Optional[HotelInfo] = Field(None, description="Hotel information")

class TravelPlan(BaseModel):
    name: str = Field(..., description="Name of the travel plan")
    origin: str = Field(..., description="Origin city")
    destination: str = Field(..., description="Destination city")
    day_plans: List[DayPlan] = Field(..., description="List of day plans")
    total_cost: float = Field(..., description="Total estimated cost") 
    