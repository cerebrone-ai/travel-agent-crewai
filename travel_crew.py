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
    

if __name__ == "__main__":
    crew = TravelCrew()
    crew.kickoff({"message": "I want to travel to Paris from changigarh for 3 days in March", "timestamp": datetime.now().isoformat()})
