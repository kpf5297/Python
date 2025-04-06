# Pittsburgh Events Fetcher

A Python application to fetch and filter events in the Greater Pittsburgh area using the Ticketmaster API.

## Features
- Fetch events for the Greater Pittsburgh area.
- Filter events by selected venues.
- Display the filtered events.
- Save the filtered events as a CSV, text file, or ICS calendar file.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/kpf5297/PittsburghEventsFetcher.git
   cd PittsburghEventsFetcher
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API key:
   ```plaintext
   TICKETMASTER_API_KEY=YOUR_API_KEY
   ```

## Usage

1. Run the application:
   ```sh
   python fetch_events.py
   ```

2. Follow the instructions in the GUI to select venues and save the filtered events.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```