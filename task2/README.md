# Weather Forecast Command-Line App

A Python command-line application that fetches weather details from OpenWeatherMap API and presents readable results.

## Features

✅ **Comprehensive Weather Data**
- Temperature (current and feels like)
- Humidity levels
- Wind speed and direction
- Weather conditions and descriptions
- Cloud cover and visibility
- Atmospheric pressure

✅ **Secure API Key Management**
- Uses environment variables to keep API keys secure
- Never hardcode sensitive credentials

✅ **Robust Error Handling**
- Handles invalid city names
- Network timeout and connection errors
- Invalid API key detection
- Missing or incomplete data handling

## Tech Stack

- **Python 3.x**
- **Requests** - HTTP library for API calls
- **python-dotenv** - Environment variable management

## Setup Instructions

### 1. Get Your API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the API keys section

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```
OPENWEATHER_API_KEY=your_actual_api_key_here
```

**Important:** Never commit your `.env` file to version control!

## Usage

### Method 1: Interactive Mode

Run the script without arguments and enter the city name when prompted:

```bash
python weather_cli.py
```

### Method 2: Command-Line Arguments

Pass the city name directly as an argument:

```bash
python weather_cli.py London
```

For multi-word city names:

```bash
python weather_cli.py "New York"
python weather_cli.py Los Angeles
```

### Example Output

```
🌤️  Weather Forecast Command-Line App
============================================================

⏳ Fetching weather data for 'London'...

============================================================
🌍 Weather Forecast for London, GB
============================================================

🌡️  Temperature:
   Current: 15.5°C
   Feels like: 14.2°C

☁️  Conditions:
   Clouds: Overcast clouds

💧 Humidity:
   72%

🌬️  Wind:
   Speed: 5.5 m/s
   Direction: 220°

📊 Additional Info:
   Pressure: 1013 hPa
   Cloud Cover: 90%
   Visibility: 10.0 km

============================================================
```

## Error Handling

The app handles various error scenarios:

- **Invalid City Name**: Displays a helpful error message
- **Network Issues**: Handles timeouts and connection errors
- **Invalid API Key**: Alerts you if the API key is incorrect
- **Missing Data**: Gracefully handles incomplete API responses

## Project Structure

```
task2/
├── weather_cli.py       # Main command-line application
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment variables
├── .env               # Your actual API key (git-ignored)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Challenges Addressed

✅ **Use API keys securely**: API keys stored in `.env` file, not in code  
✅ **Display humidity, wind, and conditions**: All weather metrics shown clearly  
✅ **Error handling for wrong input**: Comprehensive error handling implemented

## Dependencies

- `requests>=2.31.0` - For making HTTP requests to the API
- `python-dotenv>=1.0.0` - For loading environment variables

## Notes

- The free OpenWeatherMap API tier has rate limits (60 calls/minute)
- Weather data updates every 10 minutes
- Temperature is shown in Celsius, wind speed in m/s

## License

This project is open source and available for educational purposes.
