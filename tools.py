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