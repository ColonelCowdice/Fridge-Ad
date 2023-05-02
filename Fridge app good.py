import tkinter as tk
import requests
import time
from newsapi import NewsApiClient
from PIL import Image, ImageTk
import os
import webbrowser
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Create a global variable to store the city entered by the user
city = ""

# Initialize the News API client with our API key
newsapi = NewsApiClient(api_key="")


# Function to get the top 10 news headlines for a given city
def get_news(app, city):
    # Define the search parameters for the news API
    search_params = {
        "q": city,
        "language": "en",
        "country": "us"
    }

    # Use the News API to get the top headlines for the specified city
    news_data = newsapi.get_top_headlines(q=search_params["q"], language=search_params["language"],
                                          country=search_params["country"])

    # Extract the titles of the top 10 articles
    news = [article["title"] for article in news_data["articles"]]

    # Combine the titles into a single string separated by two newlines
    return "\n\n".join(news[:10])


# Function to get weather data for a given city and update the GUI
def get_weather(app):
    global city
    # Make the city variable globalv so we can access it outside this function

    # Define a function to generate a random RGB color
    def random_color():
        return '#{:02x}{:02x}{:02x}'.format(*map(lambda x: random.randint(0, 255), range(3)))

    # Get the city entered by the user from the textfield
    city = textfield.get()

    # Use the OpenWeatherMap API to get the 5-day weather forecast for the specified city
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid=547e4e1e7c99ee57e3ed55b51a3085a2&units=metric"
    response = requests.get(url)
    data = response.json()

    # Extract the temperatures and dates from the API response
    temps = [item['main']['temp'] for item in data['list']]
    dates = [item['dt_txt'] for item in data['list']]

    # Create a range of x-values for the plot
    x = [i for i in range(len(dates))]

    # Define the x-tick labels for the plot
    x_ticks = [dates[i] for i in range(0, len(dates), 8)]

    # Create a new figure with a single subplot
    fig = plt.Figure(figsize=(8, 6), dpi=100)
    plot1 = fig.add_subplot(111)

    # Plot the temperature data with green dashed lines and blue circle markers
    plot1.plot(x, temps, color='green', linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue',
               markersize=12)

    # Set the x-tick values and labels for the plot
    plot1.set_xticklabels(x_ticks, rotation=45)

    # Set the y-axis limits for the plot
    plot1.set_ylim(min(temps)-1, max(temps)+1)

    # Set the x-axis limits for the plot
    plot1.set_xlim(0, len(dates))

    # Set the x- and y-axis labels and title for the plot
    plot1.set_xlabel('Date')
    plot1.set_ylabel('Temperature (°C)')
    plot1.set_title('Temperature forecast for ' + city)

    # Create a new Tkinter canvas for the plot and add it to the app window
    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)

    # Save the plot as a PNG file
    fig.savefig('graph.png')

    # Open the saved plot as a PIL image
    try:
        graph_image = Image.open('graph.png')
    except FileNotFoundError:
        print('Cannot find graph.png')

    # Convert the PIL image to a Tkinter PhotoImage and display it in a label widget
    tk_image = ImageTk.PhotoImage(graph_image)
    label = tk.Label(app, image=tk_image)
    label.pack()

    # Extract various weather data from the API response
    condition = data["list"][0]["weather"][0]["main"]
    temperature = int(data["list"][0]["main"]["temp"])
    humidity = data["list"][0]["main"]["humidity"]
    wind = data["list"][0]["wind"]["speed"]
    sunrise = time.strftime("%I:%M:%S %p", time.gmtime(data["city"]["sunrise"] + data["city"]["timezone"] - 18000))
    sunset = time.strftime("%I:%M:%S %p", time.gmtime(data["city"]["sunset"] + data["city"]["timezone"] - 18000))

    # Format the weather data into strings for display in the GUI
    display_info = f"{condition}\n{temperature} °C"
    display_data = f"\nHumidity: {humidity}%\nWind Speed: {wind} km/h\nSunrise: {sunrise}\nSunset: {sunset}"

    # Update the labels in the GUI with the weather data
    label1.config(text=display_info)
    label2.config(text=display_data)

    # Get the top news headlines for the specified city
    news = get_news(app, city)

    # Update the news label in the GUI with the top news headlines
    news_label.config(text=news)
    news_canvas.configure(scrollregion=news_canvas.bbox("all"), height=news_canvas.winfo_height())

    # Generate a new random color and set it as the background color for various widgets in the GUI
    new_color = random_color()
    app.config(bg=new_color)
    textfield.config(bg=new_color)
    label1.config(bg=new_color)
    label2.config(bg=new_color)
    news_frame.config(bg=new_color)
    news_canvas.config(bg=new_color)
    news_frame_inside_canvas.config(bg=new_color)
    news_label.config(bg=new_color)
    ad_label.config(bg=new_color)

    # Display a new random ad image in the GUI
    display_ad()


# Create the main application window
app = tk.Tk()
app.title("Weather App")
app.geometry("800x600")

# Create the GUI components
textfield = tk.Entry(app)
textfield.pack()

button = tk.Button(app, text="Get Weather", command=lambda: get_weather(app))
button.pack()

label1 = tk.Label(app, text="", font=("Arial", 20))
label1.pack()

label2 = tk.Label(app, text="", font=("Arial", 14))
label2.pack()

news_frame = tk.Frame(app)
news_frame.pack()

news_canvas = tk.Canvas(news_frame)
news_canvas.pack(side='left', fill='both', expand=True)

scrollbar = tk.Scrollbar(news_frame, orient='vertical', command=news_canvas.yview)
scrollbar.pack(side='right', fill='y')

news_frame_inside_canvas = tk.Frame(news_canvas)
news_canvas.create_window((0, 0), window=news_frame_inside_canvas, anchor='nw')

news_label = tk.Label(news_frame_inside_canvas, text="", font=("Arial", 12), wraplength=600, justify='left')
news_label.pack()

news_canvas.configure(yscrollcommand=scrollbar.set)
news_canvas.bind('<Configure>', lambda e: news_canvas.configure(scrollregion=news_canvas.bbox('all')))

ad_label = tk.Label(app, text="", font=("Arial", 16))
ad_label.pack()

# Function to display a random ad image
def display_ad():
    # Clear the previous ad image
    ad_label.config(image=None)

    # List of ad images
    ads = [
        "ad1.png",
        "ad2.png",
        "ad3.png"
    ]

    # Choose a random ad image from the list
    ad_image_path = random.choice(ads)

    # Open the ad image using PIL
    ad_image = Image.open(ad_image_path)

    # Resize the ad image to fit the label
    ad_image = ad_image.resize((200, 200))

    # Convert the PIL image to a Tkinter PhotoImage
    ad_photo = ImageTk.PhotoImage(ad_image)

    # Display the ad image in the label
    ad_label.config(image=ad_photo)
    ad_label.image = ad_photo


# Run the display_ad function to show the initial ad image
display_ad()

# Run the main event loop
app.mainloop()


