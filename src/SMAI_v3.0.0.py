"""

----------------------------------------------------------------------------------

Creator : Michael Spano
Version Release Date : 03/04/2026
Filename : SMAI_v3.0.0.py
Version : v3.0.0


Alpha Vantage API documentation link
------------------------------------

https://www.alphavantage.co/documentation/#

----------------------------------------------


Alpha Vantage API key link
--------------------------

To claim your free Alpha Vantage API key visit:

https://www.alphavantage.co/support/#api-key

----------------------------------------------


GROQCloud API documentation link
--------------------------------

https://console.groq.com/docs/overview

----------------------------------------------


GROQCloud API key link
----------------------

To claim your free GROQ API key visit:

https://console.groq.com/keys


----------------------------------------------

----------------------------------------------------------------------------------

"""

# -------------------------------------------
#
# Module Importing
#
# -------------------------------------------

# Imports the requests module for API calls
import requests

# Imports the csv module for exporting stock data to CSV files
import csv

# Imports the os module for file path checking and reading and writing the API key text files
import os

# Imports the sys module for its exit function
import sys

# Imports the threading module to run API calls in the background without freezing the GUI
import threading

# Imports the datetime module for use in CSV and PNG file naming
from datetime import date as importeddate

# Imports customtkinter for the modern dark themed GUI
import customtkinter as ctk

# Imports tkinter for the Treeview table widget and messagebox
import tkinter as tk
from tkinter import ttk, messagebox

# Imports matplotlib for the line chart
from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Imports the Groq module for AI powered investment advice
from groq import Groq

# -------------------------------------------
#
# CustomTkinter Appearance Settings
#
# -------------------------------------------

# Sets the appearance mode to dark and the color theme to blue
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -------------------------------------------
#
# API Key + API Key Function
#
# -------------------------------------------

# Function to load an API key from a specified file if it exists, if not it asks the user
# to enter their API key and saves it to the specified file for future use
def load_api_key(filename, service_name):

    # Checks if the specified API key file already exists
    if os.path.exists(filename):

        # Opens and reads the saved API key from the file and strips any whitespace
        with open(filename, "r") as f:
            return f.read().strip()

    # If the file does not exist, asks the user to enter their API key for the first time
    else:
        key = ctk.CTkInputDialog(text=f"Enter your {service_name} API key:", title=f"{service_name} API Key").get_input()
        if key:
            with open(filename, "w") as f:
                f.write(key.strip())
        return key.strip() if key else ""

# -------------------------------------------
#
# AI Behavior Prompt for AI Function
#
# -------------------------------------------

# System prompt tells Groq how to behave and what role to take
system_promptGROQ = "You are an expert Wall Street analyst with deep knowledge of financial markets, stocks, and investment strategies. When provided with stock data, give a concise professional investment analysis and recommendation in around 8 to 10 sentences. When asked follow up questions, answer them as thoroughly as needed to fully address the question, using the stock data provided as context. Use all provided data points in your analysis and avoid over-relying on any single metric like beta. Never invent or speculate on specific price targets unless the data explicitly provides them."

# -------------------------------------------
#
# Function Definitions
#
# -------------------------------------------

# Function for checking and converting numbers to floats
def safeconversionfloat(number):
    try:
        return float(number)
    except (ValueError, TypeError):
        return 0.0


# Function to call the API and get monthly time series data
def timeseriesmonthly(symbol, apikey):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={apikey}"
    results = requests.get(url)
    data = results.json().get("Monthly Time Series", {})
    recentmonths = sorted(data.keys(), reverse=True)[:12]
    monthlylist = []
    for date in recentmonths:
        entry = data.get(date, {})
        monthlylist.append({
            "Date": date,
            "Open": float(entry.get("1. open", 0)),
            "High": float(entry.get("2. high", 0)),
            "Low": float(entry.get("3. low", 0)),
            "Close": float(entry.get("4. close", 0))
        })
    return monthlylist


# Function to call the API and get daily time series data
def timeseriesdaily(symbol, apikey):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}"
    results = requests.get(url)
    data = results.json().get("Time Series (Daily)", {})
    recentdays = sorted(data.keys(), reverse=True)[:30]
    dailylist = []
    for date in recentdays:
        entry = data.get(date, {})
        dailylist.append({
            "Date": date,
            "Open": float(entry.get("1. open", 0)),
            "High": float(entry.get("2. high", 0)),
            "Low": float(entry.get("3. low", 0)),
            "Close": float(entry.get("4. close", 0))
        })
    return dailylist


# Function to call the API and get the overview information of a stock
def overview(symbol, apikey):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={apikey}"
    results = requests.get(url)
    data = results.json()
    overviewdict = {
        "Symbol": data["Symbol"],
        "Asset Type": data.get("AssetType", "N/A"),
        "Name": data["Name"],
        "Description": data.get("Description", "N/A"),
        "Exchange": data.get("Exchange", "N/A"),
        "Currency": data.get("Currency", "N/A"),
        "Country": data.get("Country", "N/A"),
        "Sector": data.get("Sector", "N/A"),
        "Industry": data.get("Industry", "N/A"),
        "Address": data.get("Address", "N/A"),
        "Official Site": data.get("OfficialSite", "N/A"),
        "Beta": safeconversionfloat(data.get("Beta")),
        "Analyst Rating Strong Buy": safeconversionfloat(data.get("AnalystRatingStrongBuy")),
        "Analyst Rating Buy": safeconversionfloat(data.get("AnalystRatingBuy")),
        "Analyst Rating Hold": safeconversionfloat(data.get("AnalystRatingHold")),
        "Analyst Rating Sell": safeconversionfloat(data.get("AnalystRatingSell")),
        "Analyst Rating Strong Sell": safeconversionfloat(data.get("AnalystRatingStrongSell"))
    }
    return overviewdict


# Function to give investment advice based on market condition and analyst ratings
def investment_advice(overview_data, market_status):
    strong_buy = overview_data["Analyst Rating Strong Buy"]
    buy = overview_data["Analyst Rating Buy"]
    hold = overview_data["Analyst Rating Hold"]
    sell = overview_data["Analyst Rating Sell"]
    strong_sell = overview_data["Analyst Rating Strong Sell"]
    total_score = strong_buy + buy + hold + sell + strong_sell
    if total_score > 0:
        positive_score = (strong_buy * 2 + buy) / total_score
        negative_score = (sell + strong_sell * 2) / total_score
    else:
        positive_score = 0
        negative_score = 0
    if market_status == "Increased":
        if positive_score > 0.6:
            return "✅ Buy: Strong professional analyst support in a rising market."
        else:
            return "❌ Avoid: Analysts are not positive in a rising market."
    elif market_status == "Stable":
        if positive_score > 0.5:
            return "✅ Buy: Average professional analyst support in a stable market."
        else:
            return "❌ Avoid: Analysts are not positive in a stable market."
    elif market_status == "Decreased":
        if positive_score > 0.5 and negative_score < 0.5:
            return "✅ Buy: Strong analyst sentiment score in a weak market."
        else:
            return "❌ Avoid: Analysts are negative in a weak market."
    else:
        return "❌ Avoid: Analysts are mixed, be cautious and monitor stock closely."


# Function to save stock data to a CSV file
def CSVsave(data, filename, symbol, companyname):
    with open(filename, mode='w', newline='') as csvfile:
        fieldnames = ["Date", "Open", "High", "Low", "Close"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvfile.write(f"Company Name: {companyname}\n\n")
        csvfile.write(f"Stock Symbol: {symbol}\n\n")
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# Function to get AI powered investment advice from the Groq API
def ai_investment_advice(overview_data, current_price, groqapikey):
    client = Groq(api_key=groqapikey)
    prompt = f"""
    Company : {overview_data["Name"]}
    Current Stock Price : ${current_price:.2f}
    Sector: {overview_data['Sector'].title()}
    Industry: {overview_data['Industry'].title()}
    Beta: {overview_data['Beta']}
    Analyst Strong Buy Ratings: {overview_data['Analyst Rating Strong Buy']}
    Analyst Buy Ratings: {overview_data['Analyst Rating Buy']}
    Analyst Hold Ratings: {overview_data['Analyst Rating Hold']}
    Analyst Sell Ratings: {overview_data['Analyst Rating Sell']}
    Analyst Strong Sell Ratings: {overview_data['Analyst Rating Strong Sell']}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_promptGROQ},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# -------------------------------------------
#
# Main Application Class
#
# -------------------------------------------

class SMAIApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("SMAI — Stock Market Analysis & Investing Tool")
        self.geometry("1280x720")
        self.minsize(1280, 720)

        # Load API keys on launch
        self.apikey = load_api_key("AlphaVantageAPIKey.txt", "Alpha Vantage")
        self.groqapikey = load_api_key("GroqAPIKey.txt", "Groq")

        # App state variables
        self.overview_data = None
        self.stock_symbol = None
        self.company_name = None
        self.current_stock_data = None
        self.current_data_type = None
        self.chart_canvas = None
        self.todaydate = importeddate.today()
        self.filenummonth = 0
        self.filenumday = 0
        self.ai_conversation = []

        # Show the home screen first
        self.show_home_screen()

    # -------------------------------------------
    #
    # Home Screen
    #
    # -------------------------------------------

    def show_home_screen(self):

        # Clears any existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Main home frame
        self.home_frame = ctk.CTkFrame(self, fg_color="#0f0f1a")
        self.home_frame.pack(fill="both", expand=True)

        # Centers the content vertically and horizontally
        self.home_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.home_frame.grid_columnconfigure(0, weight=1)

        # Tries to load and display the SMAI logo
        try:
            from PIL import Image
            import io

            # Downloads the logo directly from the GitHub repo raw URL
            logo_url = "https://raw.githubusercontent.com/misb1280/stockmarkettool/refs/heads/main/docs/SMAI_Logo_Dark.png"
            logo_response = requests.get(logo_url)

            # Opens the image from the downloaded bytes in memory
            logo_image = ctk.CTkImage(
                Image.open(io.BytesIO(logo_response.content)),
                size=(720, 480)
            )
            logo_label = ctk.CTkLabel(self.home_frame, image=logo_image, text="")
            logo_label.grid(row=0, column=0, pady=(60, 10))
        except:
            # If the logo cant be loaded just show the text title
            pass

        # SMAI title label
        title_label = ctk.CTkLabel(
            self.home_frame,
            text="SMAI",
            font=ctk.CTkFont(size=52, weight="bold"),
            text_color="#6060ff"
        )
        title_label.grid(row=1, column=0, pady=(10, 5))

        # Subtitle label
        subtitle_label = ctk.CTkLabel(
            self.home_frame,
            text="Stock Market Analysis & Investing Tool",
            font=ctk.CTkFont(size=16),
            text_color="#4040a0"
        )
        subtitle_label.grid(row=2, column=0, pady=(0, 40))

        # Stock symbol search frame
        search_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        search_frame.grid(row=3, column=0, pady=10)

        # Stock symbol entry label
        entry_label = ctk.CTkLabel(
            search_frame,
            text="Enter a stock symbol to get started",
            font=ctk.CTkFont(size=14),
            text_color="#6060a0"
        )
        entry_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Stock symbol entry box
        self.home_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="e.g. NVDA, AAPL, TSLA",
            width=280,
            height=44,
            font=ctk.CTkFont(size=14),
            fg_color="#1a1a2e",
            border_color="#303060",
            text_color="#a0a0ff"
        )
        self.home_entry.grid(row=1, column=0, padx=(0, 10))

        # Pressing enter also triggers the search
        self.home_entry.bind("<Return>", lambda event: self.home_search())

        # Search button
        search_button = ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=120,
            height=44,
            font=ctk.CTkFont(size=14),
            fg_color="#4040c0",
            hover_color="#5050d0",
            command=self.home_search
        )
        search_button.grid(row=1, column=1)

        # Status label for showing loading or error messages
        self.home_status = ctk.CTkLabel(
            self.home_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#ff4444"
        )
        self.home_status.grid(row=4, column=0, pady=10)

        # Disclaimer label at the bottom
        disclaimer_label = ctk.CTkLabel(
            self.home_frame,
            text="⚠️ For educational and informational purposes only. Not financial advice.",
            font=ctk.CTkFont(size=11),
            text_color="#303060"
        )
        disclaimer_label.grid(row=5, column=0, pady=(0, 20))

    # -------------------------------------------
    #
    # Home Screen Search
    #
    # -------------------------------------------

    def home_search(self):

        # Gets the stock symbol from the entry box and converts to uppercase
        symbol = self.home_entry.get().strip().upper()

        # Checks if the entry is empty
        if not symbol:
            self.home_status.configure(text="Please enter a stock symbol.", text_color="#ff4444")
            return

        # Shows loading message while fetching data
        self.home_status.configure(text="⏳ Loading stock data...", text_color="#6060ff")
        self.update()

        # Runs the API call in a thread so the GUI doesnt freeze
        def fetch():
            try:
                data = overview(symbol, self.apikey)
                self.overview_data = data
                self.stock_symbol = data["Symbol"]
                self.company_name = data["Name"]
                self.after(0, self.show_main_interface)
            except KeyError:
                self.after(0, lambda: self.home_status.configure(
                    text=f"❌ '{symbol}' is not a valid stock symbol. Please try again.",
                    text_color="#ff4444"
                ))

        threading.Thread(target=fetch, daemon=True).start()

    # -------------------------------------------
    #
    # Main Interface
    #
    # -------------------------------------------

    def show_main_interface(self):

        # Clears the home screen
        for widget in self.winfo_children():
            widget.destroy()

        # Main container frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#0a0a14")
        self.main_frame.pack(fill="both", expand=True)

        # Top bar with logo text and search bar
        self.build_topbar()

        # Tab view for the main content
        self.build_tabs()

    # -------------------------------------------
    #
    # Top Bar
    #
    # -------------------------------------------

    def build_topbar(self):

        # Top bar frame
        topbar = ctk.CTkFrame(self.main_frame, fg_color="#0d0d1f", height=60, corner_radius=0)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        # SMAI logo text on the left
        logo_text = ctk.CTkLabel(
            topbar,
            text="📈 SMAI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6060ff"
        )
        logo_text.pack(side="left", padx=20)

        # Currently viewing label
        self.viewing_label = ctk.CTkLabel(
            topbar,
            text=f"Viewing: {self.company_name} ({self.stock_symbol})",
            font=ctk.CTkFont(size=13),
            text_color="#4040a0"
        )
        self.viewing_label.pack(side="left", padx=10)

        # Change stock button on the right
        change_button = ctk.CTkButton(
            topbar,
            text="🔄 Change Stock",
            width=140,
            height=34,
            font=ctk.CTkFont(size=13),
            fg_color="#1a1a3a",
            hover_color="#2a2a4a",
            command=self.show_home_screen
        )
        change_button.pack(side="right", padx=20)

    # -------------------------------------------
    #
    # Tab View
    #
    # -------------------------------------------

    def build_tabs(self):

        # Tab view widget
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            fg_color="#0f0f1a",
            segmented_button_fg_color="#0d0d1f",
            segmented_button_selected_color="#3030a0",
            segmented_button_selected_hover_color="#4040b0",
            segmented_button_unselected_color="#0d0d1f",
            segmented_button_unselected_hover_color="#1a1a2e",
            text_color="#6060a0",
            text_color_disabled="#303060"
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Adds all five tabs
        self.tabview.add("📊 Stock Data")
        self.tabview.add("🏢 Overview")
        self.tabview.add("💡 Investment Advice")
        self.tabview.add("🤖 AI Advice")
        self.tabview.add("📈 Chart")

        # Builds the content for each tab
        self.build_stock_data_tab()
        self.build_overview_tab()
        self.build_advice_tab()
        self.build_ai_tab()
        self.build_chart_tab()

    # -------------------------------------------
    #
    # Refresh Tabs After Stock Change
    #
    # -------------------------------------------

    def refresh_tabs(self):

        # Destroys and rebuilds the tab view for the new stock
        self.tabview.destroy()
        self.build_tabs()

    # -------------------------------------------
    #
    # Stock Data Tab
    #
    # -------------------------------------------

    def build_stock_data_tab(self):

        tab = self.tabview.tab("📊 Stock Data")

        # Controls frame at the top of the tab
        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(10, 5), padx=10)

        # Data range label
        range_label = ctk.CTkLabel(
            controls_frame,
            text="DATA RANGE",
            font=ctk.CTkFont(size=11),
            text_color="#4040a0"
        )
        range_label.pack(side="left", padx=(0, 10))

        # Dropdown for monthly or daily selection
        self.data_range_var = ctk.StringVar(value="Monthly (12 months)")
        range_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.data_range_var,
            values=["Monthly (12 months)", "Daily (30 days)"],
            width=200,
            fg_color="#1a1a2e",
            button_color="#303060",
            button_hover_color="#4040a0",
            dropdown_fg_color="#1a1a2e",
            text_color="#a0a0ff"
        )
        range_dropdown.pack(side="left", padx=(0, 10))

        # Load data button
        load_button = ctk.CTkButton(
            controls_frame,
            text="Load Data",
            width=110,
            height=34,
            fg_color="#4040c0",
            hover_color="#5050d0",
            command=self.load_stock_data
        )
        load_button.pack(side="left", padx=(0, 10))

        # Export to CSV button
        self.export_button = ctk.CTkButton(
            controls_frame,
            text="💾 Export CSV",
            width=120,
            height=34,
            fg_color="#1a3a1a",
            hover_color="#2a4a2a",
            text_color="#40c040",
            command=self.export_csv,
            state="disabled"
        )
        self.export_button.pack(side="left")

        # Status label for loading messages
        self.stock_status = ctk.CTkLabel(
            tab,
            text="Select a data range and click Load Data.",
            font=ctk.CTkFont(size=12),
            text_color="#4040a0"
        )
        self.stock_status.pack(pady=5)

        # Treeview table frame
        table_frame = ctk.CTkFrame(tab, fg_color="#0d0d1f")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Treeview style configuration for dark theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
            background="#0f0f1a",
            foreground="#a0a0d0",
            fieldbackground="#0f0f1a",
            rowheight=28,
            font=("Courier New", 12)
        )
        style.configure("Dark.Treeview.Heading",
            background="#1a1a3a",
            foreground="#6060c0",
            font=("Courier New", 12, "bold"),
            relief="flat"
        )
        style.map("Dark.Treeview",
            background=[("selected", "#2a2a4a")],
            foreground=[("selected", "#a0a0ff")]
        )

        # Treeview widget for displaying stock data in a table
        self.stock_tree = ttk.Treeview(
            table_frame,
            columns=("Date", "Open", "High", "Low", "Close"),
            show="headings",
            style="Dark.Treeview"
        )

        # Sets the column headings and widths
        for col in ("Date", "Open", "High", "Low", "Close"):
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=150, anchor="center")

        # Scrollbar for the treeview
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.stock_tree.pack(fill="both", expand=True)

    # -------------------------------------------
    #
    # Load Stock Data
    #
    # -------------------------------------------

    def load_stock_data(self):

        # Shows loading status
        self.stock_status.configure(text="⏳ Loading stock data...", text_color="#6060ff")
        self.update()

        # Gets the selected data range
        selected = self.data_range_var.get()

        # Runs the API call in a thread
        def fetch():
            try:
                if "Monthly" in selected:
                    data = timeseriesmonthly(self.stock_symbol, self.apikey)
                    self.current_data_type = "Monthly"
                else:
                    data = timeseriesdaily(self.stock_symbol, self.apikey)
                    self.current_data_type = "Daily"

                # Stores the data for CSV export and chart use
                self.current_stock_data = data

                # Updates the UI on the main thread
                self.after(0, lambda: self.populate_stock_table(data))
            except Exception as e:
                self.after(0, lambda: self.stock_status.configure(
                    text=f"❌ Error loading data: {str(e)}", text_color="#ff4444"
                ))

        threading.Thread(target=fetch, daemon=True).start()

    # -------------------------------------------
    #
    # Populate Stock Data Table
    #
    # -------------------------------------------

    def populate_stock_table(self, data):

        # Clears any existing rows in the table
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)

        # Inserts each row of stock data into the table
        for entry in data:
            self.stock_tree.insert("", "end", values=(
                entry["Date"],
                f"${entry['Open']:.2f}",
                f"${entry['High']:.2f}",
                f"${entry['Low']:.2f}",
                f"${entry['Close']:.2f}"
            ))

        # Updates the status label and enables the export button
        self.stock_status.configure(
            text=f"✅ {self.current_data_type} data loaded for {self.company_name}.",
            text_color="#40c040"
        )
        self.export_button.configure(state="normal")

    # -------------------------------------------
    #
    # Export CSV
    #
    # -------------------------------------------

    def export_csv(self):

        # Checks if there is data to export
        if not self.current_stock_data:
            messagebox.showwarning("No Data", "Please load stock data before exporting.")
            return

        # Increments the file number counter based on data type
        if self.current_data_type == "Monthly":
            self.filenummonth += 1
            filename = f"{self.current_data_type}DataInfoFor{self.company_name}{self.todaydate}VERSION{self.filenummonth}.csv"
        else:
            self.filenumday += 1
            filename = f"{self.current_data_type}DataInfoFor{self.company_name}{self.todaydate}VERSION{self.filenumday}.csv"

        # Saves the data to a CSV file
        CSVsave(self.current_stock_data, filename, self.stock_symbol, self.company_name)
        messagebox.showinfo("Export Successful", f"Data saved to {filename}")

    # -------------------------------------------
    #
    # Overview Tab
    #
    # -------------------------------------------

    def build_overview_tab(self):

        tab = self.tabview.tab("🏢 Overview")

        # Scrollable frame for overview content
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="#0f0f1a")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Gets the overview data
        data = self.overview_data

        # Overview fields to display
        fields = [
            ("Symbol", data.get("Symbol", "N/A")),
            ("Name", data.get("Name", "N/A")),
            ("Asset Type", data.get("Asset Type", "N/A")),
            ("Exchange", data.get("Exchange", "N/A")),
            ("Currency", data.get("Currency", "N/A")),
            ("Country", data.get("Country", "N/A")),
            ("Sector", data.get("Sector", "N/A").title()),
            ("Industry", data.get("Industry", "N/A").title()),
            ("Address", data.get("Address", "N/A").title()),
            ("Official Site", data.get("Official Site", "N/A")),
            ("Beta", str(data.get("Beta", "N/A"))),
            ("Analyst Strong Buy", str(int(data.get("Analyst Rating Strong Buy", 0)))),
            ("Analyst Buy", str(int(data.get("Analyst Rating Buy", 0)))),
            ("Analyst Hold", str(int(data.get("Analyst Rating Hold", 0)))),
            ("Analyst Sell", str(int(data.get("Analyst Rating Sell", 0)))),
            ("Analyst Strong Sell", str(int(data.get("Analyst Rating Strong Sell", 0)))),
        ]

        # Displays each field as a label pair
        for label, value in fields:
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="#1a1a2e", corner_radius=6)
            row_frame.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#6060c0",
                width=160,
                anchor="w"
            ).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color="#a0a0d0",
                anchor="w",
                wraplength=600
            ).pack(side="left", padx=12, pady=8, fill="x", expand=True)

        # Description section at the bottom
        desc_label = ctk.CTkLabel(
            scroll_frame,
            text="DESCRIPTION",
            font=ctk.CTkFont(size=11),
            text_color="#4040a0"
        )
        desc_label.pack(anchor="w", padx=5, pady=(15, 5))

        desc_frame = ctk.CTkFrame(scroll_frame, fg_color="#1a1a2e", corner_radius=6)
        desc_frame.pack(fill="x", pady=3)
        ctk.CTkLabel(
            desc_frame,
            text=data.get("Description", "N/A"),
            font=ctk.CTkFont(size=12),
            text_color="#a0a0d0",
            wraplength=750,
            justify="left"
        ).pack(padx=12, pady=10, anchor="w")

    # -------------------------------------------
    #
    # Investment Advice Tab
    #
    # -------------------------------------------

    def build_advice_tab(self):

        tab = self.tabview.tab("💡 Investment Advice")

        # Controls frame
        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=15)

        # Market condition label
        market_label = ctk.CTkLabel(
            controls_frame,
            text="CURRENT MARKET CONDITION",
            font=ctk.CTkFont(size=11),
            text_color="#4040a0"
        )
        market_label.pack(side="left", padx=(0, 10))

        # Market condition dropdown
        self.market_var = ctk.StringVar(value="Stable")
        market_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.market_var,
            values=["Increased", "Stable", "Decreased"],
            width=180,
            fg_color="#1a1a2e",
            button_color="#303060",
            button_hover_color="#4040a0",
            dropdown_fg_color="#1a1a2e",
            text_color="#a0a0ff"
        )
        market_dropdown.pack(side="left", padx=(0, 10))

        # Get advice button
        advice_button = ctk.CTkButton(
            controls_frame,
            text="Get Advice",
            width=120,
            height=34,
            fg_color="#4040c0",
            hover_color="#5050d0",
            command=self.get_investment_advice
        )
        advice_button.pack(side="left")

        # Advice result frame
        result_frame = ctk.CTkFrame(tab, fg_color="#1a1a2e", corner_radius=8)
        result_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Advice result label
        self.advice_result = ctk.CTkLabel(
            result_frame,
            text="Select a market condition and click Get Advice.",
            font=ctk.CTkFont(size=15),
            text_color="#4040a0",
            wraplength=700
        )
        self.advice_result.pack(expand=True)

        # Disclaimer label
        disclaimer = ctk.CTkLabel(
            tab,
            text="⚠️ For educational purposes only. Not professional financial advice.",
            font=ctk.CTkFont(size=11),
            text_color="#303060"
        )
        disclaimer.pack(pady=(0, 10))

    # -------------------------------------------
    #
    # Get Investment Advice
    #
    # -------------------------------------------

    def get_investment_advice(self):

        # Gets the selected market condition and advice from the function
        market_status = self.market_var.get()
        advice = investment_advice(self.overview_data, market_status)

        # Determines color based on buy or avoid
        color = "#40c040" if "✅" in advice else "#ff4444"
        self.advice_result.configure(text=advice, text_color=color, font=ctk.CTkFont(size=18, weight="bold"))

    # -------------------------------------------
    #
    # AI Advice Tab
    #
    # -------------------------------------------

    def build_ai_tab(self):

        tab = self.tabview.tab("🤖 AI Advice")

        # Get AI advice button at top
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        ai_button = ctk.CTkButton(
            top_frame,
            text="🤖 Generate AI Investment Analysis",
            height=40,
            fg_color="#4040c0",
            hover_color="#5050d0",
            font=ctk.CTkFont(size=14),
            command=self.get_ai_advice
        )
        ai_button.pack(side="left")

        self.ai_status = ctk.CTkLabel(
            top_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#6060ff"
        )
        self.ai_status.pack(side="left", padx=15)

        # Scrollable text area for AI responses
        self.ai_textbox = ctk.CTkTextbox(
            tab,
            fg_color="#0d0d1f",
            text_color="#a0a0d0",
            font=ctk.CTkFont(family="Courier New", size=13),
            wrap="word",
            state="disabled"
        )
        self.ai_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Follow up question frame at the bottom
        followup_frame = ctk.CTkFrame(tab, fg_color="#0d0d1f", corner_radius=8)
        followup_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Follow up entry box
        self.followup_entry = ctk.CTkEntry(
            followup_frame,
            placeholder_text="Ask a follow up question...",
            height=40,
            fg_color="#1a1a2e",
            border_color="#303060",
            text_color="#a0a0ff",
            font=ctk.CTkFont(size=13)
        )
        self.followup_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.followup_entry.bind("<Return>", lambda event: self.send_followup())

        # Send button for follow up question
        send_button = ctk.CTkButton(
            followup_frame,
            text="Send",
            width=90,
            height=40,
            fg_color="#4040c0",
            hover_color="#5050d0",
            command=self.send_followup
        )
        send_button.pack(side="right", padx=10, pady=10)

        # Disclaimer label
        disclaimer = ctk.CTkLabel(
            tab,
            text="⚠️ For educational purposes only. Not professional financial advice.",
            font=ctk.CTkFont(size=11),
            text_color="#303060"
        )
        disclaimer.pack(pady=(0, 5))

    # -------------------------------------------
    #
    # Get AI Advice
    #
    # -------------------------------------------

    def get_ai_advice(self):

        # Shows loading status
        self.ai_status.configure(text="⏳ Generating AI analysis please wait...")
        self.update()

        # Runs the API call in a thread
        def fetch():
            try:
                # Gets the current price from the daily data
                daily = timeseriesdaily(self.stock_symbol, self.apikey)
                current_price = daily[0]["Close"]

                # Gets the AI advice
                advice = ai_investment_advice(self.overview_data, current_price, self.groqapikey)

                # Stores in conversation history
                self.ai_conversation = [
                    {"role": "system", "content": system_promptGROQ},
                    {"role": "user", "content": f"Company: {self.overview_data['Name']}, Price: ${current_price:.2f}"},
                    {"role": "assistant", "content": advice}
                ]

                # Updates the UI on the main thread
                self.after(0, lambda: self.append_ai_text(f"🤖 AI Investment Advice for {self.company_name}:\n\n{advice}\n\n"))
                self.after(0, lambda: self.ai_status.configure(text="✅ Analysis complete.", text_color="#40c040"))
            except Exception as e:
                self.after(0, lambda: self.ai_status.configure(
                    text=f"❌ Error: {str(e)}", text_color="#ff4444"
                ))

        threading.Thread(target=fetch, daemon=True).start()

    # -------------------------------------------
    #
    # Send Follow Up Question
    #
    # -------------------------------------------

    def send_followup(self):

        # Gets the question from the entry box
        question = self.followup_entry.get().strip()
        if not question:
            return

        # Clears the entry box
        self.followup_entry.delete(0, "end")

        # Shows loading status
        self.ai_status.configure(text="⏳ Generating response please wait...", text_color="#6060ff")
        self.append_ai_text(f"\n❓ You: {question}\n\n")

        # Runs the follow up in a thread
        def fetch():
            try:
                client = Groq(api_key=self.groqapikey)

                # Adds the follow up question to the conversation
                self.ai_conversation.append({"role": "user", "content": question})

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=self.ai_conversation
                )

                answer = response.choices[0].message.content

                # Adds the response to the conversation history
                self.ai_conversation.append({"role": "assistant", "content": answer})

                # Updates the UI on the main thread
                self.after(0, lambda: self.append_ai_text(f"🤖 AI: {answer}\n\n"))
                self.after(0, lambda: self.ai_status.configure(text="✅ Response received.", text_color="#40c040"))
            except Exception as e:
                self.after(0, lambda: self.ai_status.configure(
                    text=f"❌ Error: {str(e)}", text_color="#ff4444"
                ))

        threading.Thread(target=fetch, daemon=True).start()

    # -------------------------------------------
    #
    # Append Text to AI Textbox
    #
    # -------------------------------------------

    def append_ai_text(self, text):

        # Enables the textbox temporarily to insert text then disables it again
        self.ai_textbox.configure(state="normal")
        self.ai_textbox.insert("end", text)
        self.ai_textbox.see("end")
        self.ai_textbox.configure(state="disabled")

    # -------------------------------------------
    #
    # Chart Tab
    #
    # -------------------------------------------

    def build_chart_tab(self):

        tab = self.tabview.tab("📈 Chart")

        # Chart status label
        self.chart_status = ctk.CTkLabel(
            tab,
            text="Load stock data from the Stock Data tab to view the chart here.",
            font=ctk.CTkFont(size=13),
            text_color="#4040a0"
        )
        self.chart_status.pack(expand=True)

        # Buttons frame to hold refresh and save buttons side by side
        chart_buttons_frame = ctk.CTkFrame(tab, fg_color="transparent")
        chart_buttons_frame.pack(pady=10)

        # Refresh chart button
        refresh_button = ctk.CTkButton(
            chart_buttons_frame,
            text="🔄 Refresh Chart",
            width=160,
            height=36,
            fg_color="#4040c0",
            hover_color="#5050d0",
            command=self.update_chart
        )
        refresh_button.pack(side="left", padx=10)

        # Save chart button
        save_chart_button = ctk.CTkButton(
            chart_buttons_frame,
            text="💾 Save Chart",
            width=160,
            height=36,
            fg_color="#1a3a1a",
            hover_color="#2a4a2a",
            text_color="#40c040",
            command=self.save_chart
        )
        save_chart_button.pack(side="left", padx=10)
        
    # -------------------------------------------
    #
    # Update Chart
    #
    # -------------------------------------------

    def update_chart(self):

        # Checks if stock data has been loaded
        if not self.current_stock_data:
            messagebox.showwarning("No Data", "Please load stock data from the Stock Data tab first.")
            return

        tab = self.tabview.tab("📈 Chart")

        # Removes any existing chart
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        # Hides the status label
        self.chart_status.pack_forget()

        # Prepares the chart data in chronological order
        dates = [entry["Date"] for entry in reversed(self.current_stock_data)]
        closes = [entry["Close"] for entry in reversed(self.current_stock_data)]

        # Creates the matplotlib figure with dark theme
        fig, ax = pyplot.subplots(figsize=(10, 5), facecolor="#0f0f1a")
        ax.set_facecolor("#0d0d1f")
        ax.plot(dates, closes, linestyle="--", marker="o", color="#6060ff", linewidth=2, markersize=5)
        ax.set_title(f"{self.company_name} {self.current_data_type} Close Price", color="#a0a0d0", fontsize=13)
        ax.set_xlabel("Date", color="#6060a0")
        ax.set_ylabel("Closing Price ($)", color="#6060a0")
        ax.tick_params(colors="#6060a0", rotation=45)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.0f}"))
        ax.grid(True, color="#1a1a3a", linestyle="--", alpha=0.5)
        for spine in ax.spines.values():
            spine.set_edgecolor("#1a1a3a")
        fig.tight_layout()

        # Embeds the chart into the tab
        self.chart_canvas = FigureCanvasTkAgg(fig, master=tab)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


    def save_chart(self):
        
         # Checks if a chart has been loaded
        if not self.current_stock_data:
            messagebox.showwarning("No Chart", "Please load stock data and refresh the chart first.")
            return

        # Increments file counter and saves the chart
        if self.current_data_type == "Monthly":
            self.filenummonth += 1
            filename = f"MonthlyLineChartFor{self.company_name}{self.todaydate}VERSION{self.filenummonth}.png"
        else:
            self.filenumday += 1
            filename = f"DailyLineChartFor{self.company_name}{self.todaydate}VERSION{self.filenumday}.png"

        pyplot.savefig(filename)
        messagebox.showinfo("Chart Saved", f"Chart saved as {filename}")

# -------------------------------------------
#
# Run the Application
#
# -------------------------------------------

if __name__ == "__main__":
    app = SMAIApp()
    app.mainloop()
