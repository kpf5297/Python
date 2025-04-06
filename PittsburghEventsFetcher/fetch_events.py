import requests
import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('TICKETMASTER_API_KEY')
BASE_URL = 'https://app.ticketmaster.com/discovery/v2/'
DMA_ID = '360'  # Pittsburgh DMA

def fetch_events():
    url = f'{BASE_URL}events.json?dmaId={DMA_ID}&apikey={API_KEY}&size=200'
    response = requests.get(url)
    data = response.json()
    events = data['_embedded']['events']
    return events

def process_events(events):
    event_list = []
    venues = set()

    for event in events:
        event_data = {
            'name': event['name'],
            'id': event['id'],
            'url': event['url'],
            'start_date': event['dates']['start'].get('localDate', ''),
            'start_time': event['dates']['start'].get('localTime', '00:00:00'),
            'venue': event['_embedded']['venues'][0]['name']
        }
        venues.add(event_data['venue'])
        event_list.append(event_data)

    return pd.DataFrame(event_list), list(venues)

class VenueSelectionApp:
    def __init__(self, root, venues, events_df):
        self.root = root
        self.venues = venues
        self.events_df = events_df
        self.selected_venues = []

        self.root.title('Venue Selection')
        self.label = tk.Label(root, text='Select Venues')
        self.label.pack()

        self.venue_vars = []
        for venue in venues:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(root, text=venue, variable=var)
            chk.pack()
            self.venue_vars.append((var, venue))

        self.submit_button = tk.Button(root, text='Submit', command=self.submit)
        self.submit_button.pack()

    def submit(self):
        self.selected_venues = [venue for var, venue in self.venue_vars if var.get()]
        self.display_events()
        self.save_options()

    def display_events(self):
        filtered_events = self.events_df[self.events_df['venue'].isin(self.selected_venues)]
        print(filtered_events)

    def save_options(self):
        save_as = messagebox.askquestion('Save Events', 'Would you like to save the events as a file?')
        if save_as == 'yes':
            file_types = [('CSV file', '*.csv'), ('Text file', '*.txt'), ('ICS file', '*.ics')]
            file = filedialog.asksaveasfilename(filetypes=file_types, defaultextension=file_types)
            if file.endswith('.csv'):
                self.save_as_csv(file)
            elif file.endswith('.txt'):
                self.save_as_txt(file)
            elif file.endswith('.ics'):
                self.save_as_ics(file)

    def save_as_csv(self, file):
        filtered_events = self.events_df[self.events_df['venue'].isin(self.selected_venues)]
        filtered_events.to_csv(file, index=False)

    def save_as_txt(self, file):
        filtered_events = self.events_df[self.events_df['venue'].isin(self.selected_venues)]
        with open(file, 'w') as f:
            f.write(filtered_events.to_string(index=False))

    def save_as_ics(self, file):
        filtered_events = self.events_df[self.events_df['venue'].isin(self.selected_venues)]
        cal = Calendar()
        for _, event in filtered_events.iterrows():
            e = Event()
            e.name = event['name']
            start_dt = datetime.strptime(f"{event['start_date']} {event['start_time']}", '%Y-%m-%d %H:%M:%S')
            e.begin = start_dt
            e.end = start_dt + timedelta(hours=2)
            e.url = event['url']
            cal.events.add(e)
        with open(file, 'w') as f:
            f.writelines(cal)

if __name__ == '__main__':
    events = fetch_events()
    events_df, venues = process_events(events)

    root = tk.Tk()
    app = VenueSelectionApp(root, venues, events_df)
    root.mainloop()
