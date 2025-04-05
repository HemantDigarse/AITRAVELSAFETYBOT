import sys
from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk

# Load environment variables
load_dotenv()

# Version check
if sys.version_info < (3, 11, 0):
    print("This program requires Python 3.11.0 or higher")
    sys.exit(1)

import google.generativeai as genai
import json  # For handling location-specific data (example)
import datetime
import requests
from PIL import Image, ImageTk

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Update model configuration
model = genai.GenerativeModel('gemini-pro')  # Fixed model name

# Add weather data function
# After existing imports
import requests

# After GEMINI_API_KEY definition
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(location):
    """Get current weather for location"""
    try:
        # Fixed API endpoint and error handling
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Weather API error: Status code {response.status_code}")
            return "Weather information unavailable"
            
        data = response.json()
        temp = round(float(data['main']['temp']), 1)
        description = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        feels_like = round(float(data['main']['feels_like']), 1)
        
        return f"Weather in {location}: {description}, {temp}°C (Feels like {feels_like}°C), Humidity: {humidity}%"
    except Exception as e:
        print(f"Weather error: {str(e)}")
        return "Weather information unavailable"

# After the weather functions and before the GUI class
def generate_safety_advice(user_query, location=None):
    """Generates travel safety advice using Gemini."""
    try:
        # Add transport-related context
        transport_context = ""
        if "transport" in user_query.lower() or "travel" in user_query.lower():
            transport = get_transport_options(location)
            if transport:
                transport_context = "\nAvailable transportation options:\n"
                icons = {
                    'bus_station': '🚌',
                    'train_station': '🚂',
                    'taxi_stand': '🚕',
                    'airport': '✈️'
                }
                for transport_type, locations in transport.items():
                    if locations:
                        pretty_name = transport_type.replace('_', ' ').title()
                        transport_context += f"{icons.get(transport_type, '🚏')} {pretty_name}\n"

        prompt = f"You are a helpful travel safety assistant. A user has asked: '{user_query}'"
        if location:
            prompt += f" They are currently in or planning to visit {location}."
        if transport_context:
            prompt += transport_context
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."

# After imports
from tkinter import messagebox, filedialog
import webbrowser
from datetime import datetime, timedelta

# After weather functions, before GUI class
def get_local_time(location):
    """Get local time for a location"""
    try:
        url = f"http://worldtimeapi.org/api/timezone/Europe/{location}"
        response = requests.get(url)
        data = response.json()
        return data['datetime']
    except:
        return None

def get_currency_rate(base="USD", target="EUR"):
    """Get currency exchange rate"""
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        response = requests.get(url)
        data = response.json()
        return data['rates'].get(target, "Rate not available")
    except:
        return "Currency service unavailable"

# Add these functions after get_currency_rate()

# Add these imports at the top
from geopy.geocoders import Nominatim
import folium
import webbrowser

# Replace the get_nearby_hospitals and get_hotels functions
def get_nearby_hospitals(location):
    """Get nearby hospitals using OpenStreetMap data"""
    try:
        geolocator = Nominatim(user_agent="travel_safety_assistant")
        location_data = geolocator.geocode(location)
        
        if location_data:
            url = f"https://nominatim.openstreetmap.org/search.php?q=hospital+near+{location}&format=json"
            response = requests.get(url)
            hospitals = response.json()
            
            return [{"name": h["display_name"].split(",")[0],
                    "contact": "Emergency: 108",
                    "address": h["display_name"]} 
                    for h in hospitals[:5]]  # Get top 5 results
        return []
    except Exception as e:
        print(f"Error fetching hospitals: {e}")
        return []

def show_hotels(self):
    """Display hotel recommendations with real data"""
    try:
        hotels = get_hotels(self.current_location)
        if hotels and hotels.get("nearby_hotels"):
            info = f"Nearby Hotels in {self.current_location}:\n\n"
            info += "\n".join([f"🏨 {h}" for h in hotels["nearby_hotels"]])
        else:
            info = f"No hotels found in {self.current_location}. Please check the location name or try a nearby city."
        messagebox.showinfo("Hotels", info)
    except Exception as e:
        print(f"Error showing hotels: {e}")
        messagebox.showerror("Error", "Unable to fetch hotel information. Please try again later.")

def get_hotels(location, price_range="all"):
    """Get hotel recommendations using OpenStreetMap data"""
    try:
        geolocator = Nominatim(user_agent="travel_safety_assistant")
        location_data = geolocator.geocode(location)
        
        if location_data:
            params = {
                'q': f'hotel in {location}',
                'format': 'json',
                'limit': 10,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get('https://nominatim.openstreetmap.org/search', 
                                  params=params, 
                                  headers=headers)
            
            if response.status_code == 200:
                hotels = response.json()
                if hotels:
                    return {
                        "nearby_hotels": [h["display_name"] for h in hotels if 'hotel' in h["display_name"].lower()]
                    }
            return {"nearby_hotels": []}
        return {"nearby_hotels": []}
    except Exception as e:
        print(f"Error fetching hotels: {e}")
        return {"nearby_hotels": []}

# Fix the get_nearby_hospitals function
def get_nearby_hospitals(location):
    """Get nearby hospitals using OpenStreetMap data"""
    try:
        geolocator = Nominatim(user_agent="travel_safety_assistant")
        location_data = geolocator.geocode(location)
        
        if location_data:
            params = {
                'q': f'hospital in {location}',
                'format': 'json',
                'limit': 5,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get('https://nominatim.openstreetmap.org/search', 
                                  params=params, 
                                  headers=headers)
            
            if response.status_code == 200:
                hospitals = response.json()
                if hospitals:
                    return [{"name": h["display_name"].split(',')[0],
                            "contact": "Emergency: 108",
                            "address": h["display_name"]} 
                            for h in hospitals]
            return []
        return []
    except Exception as e:
        print(f"Error fetching hospitals: {e}")
        return []

# Fix the show_emergency_contacts method in TravelSafetyChatGUI class
# Remove the standalone show_emergency_contacts function and keep only the class method
# Remove this duplicate function
def show_emergency_contacts(location):
    """Get emergency contact numbers"""
    return {
        "Police": "100",
        "Ambulance": "108",
        "Fire": "101",
        "Tourist Police": "1363",
        "Embassy Helpline": "+91-XXXXXXXXXX"
    }

# Keep and update the class method
class TravelSafetyChatGUI:
    def update_weather(self):
        """Update weather information"""
        try:
            weather_info = get_weather(self.current_location)
            self.weather_label.config(text=weather_info)
        except Exception as e:
            self.weather_label.config(text="Weather information unavailable")
        finally:
            # Update weather every 5 minutes
            self.root.after(300000, self.update_weather)

    def __init__(self, root):
        self.root = root
        self.root.title("✈️ Travel Safety Assistant")
        self.root.geometry("1000x700")
        
        # Configure style
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Info.TLabel", font=("Helvetica", 10))
        style.configure("Custom.TButton", font=("Helvetica", 10), padding=5)
        style.configure("Weather.TLabel", font=("Helvetica", 9), foreground="#1976D2")
        
        # Add time display with better styling
        self.time_label = ttk.Label(root, text="", style="Info.TLabel")
        self.time_label.pack(pady=10)
        self.update_time()
        
        # Current location
        self.current_location = "India"
        
        # Create main frame with padding and relief
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Location frame with better styling
        self.location_frame = ttk.Frame(self.main_frame)
        self.location_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Weather label - Add this before location label
        self.weather_label = ttk.Label(self.location_frame, text="", style="Weather.TLabel")
        self.weather_label.pack(side=tk.RIGHT, padx=10)
        
        self.location_label = ttk.Label(self.location_frame, text="📍 Current Location:", style="Header.TLabel")
        self.location_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Styled entry
        self.location_entry = ttk.Entry(self.location_frame, font=("Helvetica", 10))
        self.location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.location_entry.insert(0, self.current_location)
        
        self.update_location_btn = ttk.Button(self.location_frame, text="Update Location", 
                                            style="Custom.TButton", command=self.update_location)
        self.update_location_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Add service buttons frame with better styling
        self.create_service_buttons()
        
        # Chat display with better styling
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame, 
            wrap=tk.WORD, 
            height=20,
            font=("Helvetica", 10),
            background="#f5f5f5",
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Input frame with better styling
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_entry = ttk.Entry(self.input_frame, font=("Helvetica", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.send_btn = ttk.Button(self.input_frame, text="Send Message", 
                                 style="Custom.TButton", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT)

    def create_service_buttons(self):
        """Create quick access service buttons with better styling"""
        self.service_frame = ttk.Frame(self.main_frame)
        self.service_frame.pack(fill=tk.X, pady=15)
        
        services = [
            ("🏥 Medical Services", self.show_medical_services),
            ("🏨 Find Hotels", self.show_hotels),
            ("🚨 Emergency Contacts", self.show_emergency_contacts),
            ("🚌 Transport", self.show_transport_options),
            ("💱 Currency Exchange", self.check_currency),
            ("🌡️ Weather Info", self.show_weather_details)
        ]
        
        # Create a sub-frame for better button organization
        buttons_frame = ttk.Frame(self.service_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Apply grid layout for buttons
        for i, (text, command) in enumerate(services):
            btn = ttk.Button(buttons_frame, text=text, command=command, style="Custom.TButton")
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            buttons_frame.grid_columnconfigure(i, weight=1)

    # Add this method to the TravelSafetyChatGUI class
    def show_transport_options(self):
        """Display nearby transportation options"""
        transport = get_transport_options(self.current_location)
        if transport:
            info = f"Transportation Options in {self.current_location}:\n\n"
            icons = {
                'bus_station': '🚌',
                'train_station': '🚂',
                'taxi_stand': '🚕',
                'airport': '✈️'
            }
            
            for transport_type, locations in transport.items():
                if locations:
                    pretty_name = transport_type.replace('_', ' ').title()
                    info += f"{icons.get(transport_type, '🚏')} {pretty_name}s:\n"
                    info += "\n".join([f"   • {loc.split(',')[0]}" for loc in locations])
                    info += "\n\n"
        else:
            info = f"No transportation information found for {self.current_location}"
        
        messagebox.showinfo("Transportation Options", info)

    def display_message(self, message):
        """Display message with timestamp and better formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if "You:" in message:
            prefix = "👤 You"
            color = "#007AFF"
        elif "Chatbot:" in message:
            prefix = "🤖 Assistant"
            color = "#2E7D32"
        elif "System:" in message:
            prefix = "ℹ️ System"
            color = "#6200EA"
        else:
            prefix = "📢"
            color = "#000000"
            
        self.chat_display.tag_config(timestamp, foreground=color)
        self.chat_display.insert(tk.END, f"[{timestamp}] {prefix}: ", timestamp)
        self.chat_display.insert(tk.END, f"{message.split(':', 1)[1].strip()}\n")
        self.chat_display.see(tk.END)

    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fixed datetime usage
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def update_location(self):
        self.current_location = self.location_entry.get()
        self.display_message(f"System: Location updated to {self.current_location}")
        self.update_weather()

    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.delete(1.0, tk.END)
        self.display_message("Chatbot: Chat cleared. How can I help you?")

    def display_message(self, message):
        """Display message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")  # Fixed datetime usage
        self.chat_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.chat_display.see(tk.END)

    def send_message(self):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return
            
        self.display_message(f"You: {user_input}")
        self.input_entry.delete(0, tk.END)
        
        response = generate_safety_advice(user_input, self.current_location)
        self.display_message(f"Chatbot: {response}")

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Chat", command=self.save_chat)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Local Time", command=self.show_local_time)
        tools_menu.add_command(label="Weather Forecast", command=self.show_weather_details)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Travel Tips", command=self.show_travel_tips)
        help_menu.add_command(label="Emergency Numbers", command=self.show_emergency_numbers)

    def save_chat(self):
        """Save chat history to file"""
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.chat_display.get(1.0, tk.END))
            messagebox.showinfo("Success", "Chat history saved successfully!")

    def show_local_time(self):
        """Show local time for current location"""
        local_time = get_local_time(self.current_location)
        if local_time:
            messagebox.showinfo("Local Time", f"Local time in {self.current_location}: {local_time}")
        else:
            messagebox.showwarning("Error", "Could not fetch local time")

    def check_currency(self):
        """Check currency exchange rate"""
        rate = get_currency_rate()
        self.display_message(f"System: Current USD to EUR rate: {rate}")

    def show_weather_details(self):
        """Show detailed weather information"""
        weather_info = get_weather(self.current_location)
        messagebox.showinfo("Weather Details", weather_info)

    def show_travel_tips(self):
        """Show general travel tips"""
        tips = location_safety_data.get(self.current_location, {}).get('general_advice', [])
        if tips:
            messagebox.showinfo("Travel Tips", "\n".join(tips))
        else:
            messagebox.showinfo("Travel Tips", "No specific tips available for this location")

    def show_emergency_numbers(self):
        """Show emergency numbers"""
        numbers = location_safety_data.get(self.current_location, {}).get('emergency_numbers', {})
        if numbers:
            info = "\n".join([f"{k}: {v}" for k, v in numbers.items()])
            messagebox.showinfo("Emergency Numbers", info)
        else:
            messagebox.showinfo("Emergency Numbers", "No emergency numbers available for this location")

    def create_service_buttons(self):
        """Create quick access service buttons"""
        self.service_frame = ttk.Frame(self.main_frame)
        self.service_frame.pack(fill=tk.X, pady=5)
        
        services = [
            ("🏥 Medical", self.show_medical_services),
            ("🏨 Hotels", self.show_hotels),
            ("🚨 Emergency", self.show_emergency_contacts),
            ("💱 Currency", self.check_currency),
            ("🌡️ Weather", self.show_weather_details)
        ]
        
        for text, command in services:
            btn = ttk.Button(self.service_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Chat", command=self.save_chat)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Local Time", command=self.show_local_time)
        tools_menu.add_command(label="Weather Forecast", command=self.show_weather_details)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Travel Tips", command=self.show_travel_tips)
        help_menu.add_command(label="Emergency Numbers", command=self.show_emergency_numbers)

    def show_medical_services(self):
        """Display nearby medical facilities"""
        hospitals = get_nearby_hospitals(self.current_location)
        info = "\n".join([f"🏥 {h['name']}\n   Contact: {h['contact']}" for h in hospitals])
        messagebox.showinfo("Medical Services", f"Nearby Medical Facilities in {self.current_location}:\n\n{info}")

    def show_hotels(self):
        """Display hotel recommendations"""
        hotels = get_hotels(self.current_location)
        info = "Hotel Recommendations:\n\n"
        for category, hotel_list in hotels.items():
            info += f"\n{category.upper()}:\n" + "\n".join([f"🏨 {h}" for h in hotel_list])
        messagebox.showinfo("Hotels", info)

    def show_emergency_contacts(self):
        """Display emergency contact numbers"""
        emergency_numbers = {
            "Police": "100",
            "Ambulance": "108",
            "Fire": "101",
            "Tourist Police": "1363",
            "Women Helpline": "1091",
            "Child Helpline": "1098",
            "Emergency Disaster": "108"
        }
        info = "\n".join([f"🚨 {k}: {v}" for k, v in emergency_numbers.items()])
        messagebox.showinfo("Emergency Contacts", f"Emergency Numbers for {self.current_location}:\n\n{info}")

# Add after get_hotels function
def get_transport_options(location):
    """Get nearby transportation options using OpenStreetMap data"""
    try:
        geolocator = Nominatim(user_agent="travel_safety_assistant")
        location_data = geolocator.geocode(location)
        
        if location_data:
            transport_types = ['bus_station', 'train_station', 'taxi_stand', 'airport']
            transport_options = {}
            
            for transport in transport_types:
                params = {
                    'q': f'{transport} in {location}',
                    'format': 'json',
                    'limit': 5,
                    'addressdetails': 1
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get('https://nominatim.openstreetmap.org/search', 
                                      params=params, 
                                      headers=headers)
                
                if response.status_code == 200:
                    results = response.json()
                    transport_options[transport] = [r["display_name"] for r in results]
            
            return transport_options
        return {}
    except Exception as e:
        print(f"Error fetching transport options: {e}")
        return {}

# Add to TravelSafetyChatGUI class methods
def show_transport_options(self):
    """Display nearby transportation options"""
    transport = get_transport_options(self.current_location)
    if transport:
        info = f"Transportation Options in {self.current_location}:\n\n"
        icons = {
            'bus_station': '🚌',
            'train_station': '🚂',
            'taxi_stand': '🚕',
            'airport': '✈️'
        }
        
        for transport_type, locations in transport.items():
            if locations:
                pretty_name = transport_type.replace('_', ' ').title()
                info += f"{icons.get(transport_type, '🚏')} {pretty_name}s:\n"
                info += "\n".join([f"   • {loc.split(',')[0]}" for loc in locations])
                info += "\n\n"
    else:
        info = f"No transportation information found for {self.current_location}"
    
    messagebox.showinfo("Transportation Options", info)

# Update the create_service_buttons method in TravelSafetyChatGUI class
def create_service_buttons(self):
    """Create quick access service buttons with better styling"""
    self.service_frame = ttk.Frame(self.main_frame)
    self.service_frame.pack(fill=tk.X, pady=15)
    
    services = [
        ("🏥 Medical Services", self.show_medical_services),
        ("🏨 Find Hotels", self.show_hotels),
        ("🚨 Emergency Contacts", self.show_emergency_contacts),
        ("🚌 Transport", self.show_transport_options),  # Add this line
        ("💱 Currency Exchange", self.check_currency),
        ("🌡️ Weather Info", self.show_weather_details)
    ]
    
    # Create a sub-frame for better button organization
    buttons_frame = ttk.Frame(self.service_frame)
    buttons_frame.pack(fill=tk.X)
    
    for i, (text, command) in enumerate(services):
        btn = ttk.Button(buttons_frame, text=text, command=command, style="Custom.TButton")
        btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        buttons_frame.grid_columnconfigure(i, weight=1)

    def display_message(self, message):
        """Display message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")  # Fixed datetime usage
        self.chat_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.chat_display.see(tk.END)

    def send_message(self):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return
            
        self.display_message(f"You: {user_input}")
        self.input_entry.delete(0, tk.END)
        
        response = generate_safety_advice(user_input, self.current_location)
        self.display_message(f"Chatbot: {response}")

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Chat", command=self.save_chat)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Local Time", command=self.show_local_time)
        tools_menu.add_command(label="Weather Forecast", command=self.show_weather_details)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Travel Tips", command=self.show_travel_tips)
        help_menu.add_command(label="Emergency Numbers", command=self.show_emergency_numbers)

    def show_medical_services(self):
        """Display nearby medical facilities"""
        hospitals = get_nearby_hospitals(self.current_location)
        info = "\n".join([f"🏥 {h['name']}\n   Contact: {h['contact']}" for h in hospitals])
        messagebox.showinfo("Medical Services", f"Nearby Medical Facilities in {self.current_location}:\n\n{info}")

    def show_hotels(self):
        """Display hotel recommendations"""
        hotels = get_hotels(self.current_location)
        info = "Hotel Recommendations:\n\n"
        for category, hotel_list in hotels.items():
            info += f"\n{category.upper()}:\n" + "\n".join([f"🏨 {h}" for h in hotel_list])
        messagebox.showinfo("Hotels", info)

    def show_emergency_contacts(self):
        """Display emergency contact numbers"""
        emergency_numbers = {
            "Police": "100",
            "Ambulance": "108",
            "Fire": "101",
            "Tourist Police": "1363",
            "Embassy Helpline": "+91-XXXXXXXXXX"
        }
        info = "\n".join([f"🚨 {k}: {v}" for k, v in emergency_numbers.items()])
        messagebox.showinfo("Emergency Contacts", f"Emergency Numbers for {self.current_location}:\n\n{info}")

def main():
    root = ThemedTk(theme="arc")
    app = TravelSafetyChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()