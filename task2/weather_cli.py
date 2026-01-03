import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherApp:
    def __init__(self):
        """Initialize the weather app with API key"""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            print(" Error: OPENWEATHER_API_KEY not found in environment variables.")
            print("Please create a .env file with your API key:")
            print("OPENWEATHER_API_KEY=your_api_key_here")
            sys.exit(1)
        
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def fetch_weather(self, city):
        
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units (Celsius, m/s)
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f" Error: Request timed out. Please check your internet connection.")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to the weather service.")
            return None
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"Error: City '{city}' not found. Please check the spelling.")
            elif response.status_code == 401:
                print(f"Error: Invalid API key. Please check your credentials.")
            else:
                print(f" Error: HTTP {response.status_code} - {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f" Error: An unexpected error occurred - {e}")
            return None
    
    def display_weather(self, data):
        if not data:
            return
        
        try:
            # Extract weather information
            city = data['name']
            country = data['sys']['country']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            
            # Weather conditions
            weather_desc = data['weather'][0]['description'].capitalize()
            weather_main = data['weather'][0]['main']
            
            # Wind information
            wind_speed = data['wind']['speed']
            wind_deg = data['wind'].get('deg', 'N/A')
            
            # Additional info
            visibility = data.get('visibility', 'N/A')
            if visibility != 'N/A':
                visibility = visibility / 1000  # Convert to km
            
            clouds = data['clouds']['all']
            
            # Display formatted output
            print("\n" + "="*60)
            print(f" Weather Forecast for {city}, {country}")
            print("="*60)
            
            print(f"\n Temperature:")
            print(f"   Current: {temperature}°C")
            print(f"   Feels like: {feels_like}°C")
            
            print(f"\n  Conditions:")
            print(f"   {weather_main}: {weather_desc}")
            
            print(f"\n Humidity:")
            print(f"   {humidity}%")
            
            print(f"\n Wind:")
            print(f"   Speed: {wind_speed} m/s")
            if wind_deg != 'N/A':
                print(f"   Direction: {wind_deg}°")
            
            print(f"\n Additional Info:")
            print(f"   Pressure: {pressure} hPa")
            print(f"   Cloud Cover: {clouds}%")
            if visibility != 'N/A':
                print(f"   Visibility: {visibility:.1f} km")
            
            print("\n" + "="*60 + "\n")
            
        except KeyError as e:
            print(f" Error: Missing data in API response - {e}")
            print("The weather service may have returned incomplete data.")
    
    def run(self):
        """Run the weather application"""
        print("\n Weather Forecast Command-Line App")
        print("="*60)
        
        if len(sys.argv) > 1: # Get city name
            city = ' '.join(sys.argv[1:])
        else:
            city = input("\n  Enter city name: ").strip()
        
        if not city:
            print(" Error: City name cannot be empty.")
            sys.exit(1)
        
        print(f"\n Fetching weather data for '{city}'...")
        
        
        weather_data = self.fetch_weather(city) # Fetch and display weather
        self.display_weather(weather_data)


def main():
    try:
        app = WeatherApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n Weather app terminated by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
