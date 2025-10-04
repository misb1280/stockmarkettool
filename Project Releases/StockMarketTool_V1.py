"""

----------------------------------------------------------------------------------

Creator : Michael Spano
Build Release Date : 10/3/2025
Filename : StockMarketTool_V1.py
Version : V1


API documentation link
-----------------------

https://www.alphavantage.co/documentation/#

----------------------------------------------


API key link
------------

To claim your free API key visit

https://www.alphavantage.co/support/#api-key

----------------------------------------------


----------------------------------------------------------------------------------

"""

# -------------------------------------------
#
# Module Importing
#
# -------------------------------------------

# Imports the requests, webbrowser, csv, datetime module and the date function as importeddate
# imports matplotlib's pyplot for line chart data visuals in the console and imports
# matplotlib.ticker FuncFormatter for some custom axis label additions
# Imports the sys module for its exit function for stopping the program later when the user wishes to quit

import requests

import webbrowser

import csv

from datetime import date as importeddate

from matplotlib import pyplot 

from matplotlib.ticker import FuncFormatter 

import sys

# -------------------------------------------
#
# API Key
# 
# To claim your free API key visit
# https://www.alphavantage.co/support/#api-key
#
# -------------------------------------------

# Slot for your API key goes here

apikey = ""

# -------------------------------------------
#
# Function Definitons
#
# -------------------------------------------

# Function for checking and converting numbers to floats for the overview function to ensure no errors come up from converting
def safeconversionfloat(number):
    try:
        return float(number)
    except (ValueError, TypeError):
        return 0.0 # Return 0.0 for any invalid or missing value


# Function to call the API and get the time series monthly information of a stock and returns the data to the main program
def timeseriesmonthly(symbol):
    usersymbol = symbol
    timeseriesmonthURL = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={usersymbol}&apikey={apikey}"
    timeseriesresults = requests.get(timeseriesmonthURL)
    timeseriesJSON = timeseriesresults.json()
    
    # If Time Series Monthly doesn't exist (an API call failing for instance) it'll use an empty dictionary to avoid errors
    monthlydata = timeseriesJSON.get("Monthly Time Series", {})
    
    # Gets the last 12 months of stock info and sorts the keys in the reverse order
    recentmonths = sorted(monthlydata.keys(), reverse=True)[:12]
    
    # Empty list to hold each months stock data
    monthlylist = []
    
    # For loop to loop through the most recent months that the user selects and gets the neccesary values
    for date in recentmonths:
        
        # Uses .get() for each months data and if its missing we use an empty dictionary so the program doesnt error
        dataentry = monthlydata.get(date, {})
        
        # Uses .get() for each value and sets it to 0 if the data is missing so it doesnt error
        monthlylist.append({
            "Date" : date,
            "Open" : float(dataentry.get("1. open",0)),
            "High" : float(dataentry.get("2. high",0)),
            "Low" : float(dataentry.get("3. low",0)),
            "Close" : float(dataentry.get("4. close",0))
            })
    
    # Returns the list of the monthly stock info dictionaries to the main program
    return monthlylist
     
       
# Function to call the API and get the time series daily information of a stock up to a week prior and returns the data to the main program
def timeseriesdaily(symbol):
    usersymbol = symbol
    timeseriesdailyURL = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={usersymbol}&apikey={apikey}"
    timeseriesdailyresults = requests.get(timeseriesdailyURL)
    timeseriesdailyJSON = timeseriesdailyresults.json()
    
    # If Time Series Daily doesn't exist (an API call failing for instance) it'll use an empty dictionary to avoid errors
    dailydata = timeseriesdailyJSON.get("Time Series (Daily)", {})
    
    # Gets the last 30 days of stock info and sorts the keys in the reverse order
    recentdays = sorted(dailydata.keys(), reverse=True)[:30]
    
    # Empty list to hold each days stock data
    dailylist = []
    
    # For loop to loop through the most recent days that the user selects and gets the neccesary values
    for date in recentdays:
        
        # Uses .get() for each days data and if its missing we use an empty dictionary so the program doesnt error
        entry = dailydata.get(date, {})
        
        # Uses .get() for each value and sets it to 0 if the data is missing so it doesnt error
        dailylist.append({
            "Date" : date,
            "Open" : float(entry.get("1. open",0)),
            "High" : float(entry.get("2. high",0)),
            "Low" : float(entry.get("3. low",0)),
            "Close" : float(entry.get("4. close",0))
            })
     
    # Returns the list of the daily stock info dictionaries to the main program
    return dailylist

    
# Function to call the API and get the Overview information of a stock and contains all of it in a dictionary and returns it to the main program 
def overview(symbol):
    usersymbol = symbol
    overviewURL =  f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={usersymbol}&apikey={apikey}"
    overviewresults = requests.get(overviewURL)
    overviewJSON = overviewresults.json()
    
    # Stores the overview information into a dictionary 
    overviewdict = {
        
        # If a stock doesn't have any of these values it uses a N/A in their place so the program doesn't crash
        # Doesn't use .get on the symbol and name so the program does not sucessfully run through if you input an
        # incorrect stock symbol on the stock input prompt
        "Symbol" : overviewJSON["Symbol"],
        "Asset Type" : overviewJSON.get("AssetType", "N/A"),
        "Name" : overviewJSON["Name"],
        "Description" : overviewJSON.get("Description", "N/A"),
        "Exchange" : overviewJSON.get("Exchange", "N/A"),
        "Currency" : overviewJSON.get("Currency", "N/A"),
        "Country" : overviewJSON.get("Country", "N/A"),
        "Sector" : overviewJSON.get("Sector", "N/A"),
        "Industry" : overviewJSON.get("Industry", "N/A"),
        "Address" : overviewJSON.get("Address", "N/A"),
        "Official Site" : overviewJSON.get("OfficialSite", "N/A"),
        
        # Converts each value to a float using the safeconversionfloat (which will return a 0.0 if the value can't be converted)
        "Beta" : safeconversionfloat(overviewJSON.get("Beta")),
        "Analyst Rating Strong Buy" : safeconversionfloat(overviewJSON.get("AnalystRatingStrongBuy")),
        "Analyst Rating Buy" : safeconversionfloat(overviewJSON.get("AnalystRatingBuy")),
        "Analyst Rating Hold" : safeconversionfloat(overviewJSON.get("AnalystRatingHold")),
        "Analyst Rating Sell" : safeconversionfloat(overviewJSON.get("AnalystRatingSell")),
        "Analyst Rating Strong Sell" : safeconversionfloat(overviewJSON.get("AnalystRatingStrongSell"))
        }
    
    # Returns the overview information dictionary to the main program
    return overviewdict


# Function to give investment advice based on the market condition and values from the company's overview
def investment_advice(overview,market_status):
    
    # Professional Analyst Stock Ratings
    strong_buy = overview["Analyst Rating Strong Buy"]
    buy = overview["Analyst Rating Buy"]
    hold = overview["Analyst Rating Hold"]
    sell = overview["Analyst Rating Sell"]
    strong_sell = overview["Analyst Rating Strong Sell"]
    
    # Total analyst ratings
    total_score = strong_buy + buy + hold + sell + strong_sell
    
    # Analyst sentiment scores uses if statement to check if the total score is more than 0 so the program doesnt crash when we preform divison
    if total_score > 0:
        
        # Counts strong buy and sell as 2 points while buy and sell are 1 point
        positive_score = (strong_buy * 2 + buy) / total_score
        negative_score = (sell + strong_sell * 2) / total_score
    
    # If the total score is not greater than 0 then we set positive and negative score to 0 which should never happen
    else:
        positive_score = 0
        negative_score = 0
        
    
    # Stock advice conditional that uses the professional analyst's opinions and returns the buy or avoid choice to the main program
    if market_status == "Increased":  
        if positive_score > 0.6:
            return "✅ Buy: Strong professional analysts support in a rising market."
        else:
            return "❌ Avoid: Analysts are not positive in a rising market."
    
    elif market_status == "Stable":
        if positive_score > 0.5:
            return "✅ Buy: Average professional analysts support in a stable market."
        else:
            return "❌ Avoid: Analysts are not positive in a stable market."
        
    elif market_status == "Decreased":
        if positive_score > 0.5 and negative_score < 0.5:
            return "✅ Buy: Strong analyst sentiment score in a weak market."
        else:
            return "❌ Avoid: Analysts are negative in a weak market."
     
    else:
        return "❌ Avoid: Analysts are mixed, be cautious and monitor stock closely."
  
    
# Function for saving output to CSV files for use in Microsoft Excel, It has the rows for the date, open, high, low close
# and lists the stock symbol and company name in the file as well as the name of the company in the filename itself
def CSVsave(data,filename,symbol,companyname):
    with open(filename, mode='w', newline='') as csvfile:
        fieldnames = ["Date", "Open", "High", "Low", "Close"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        csvfile.write(f"Company Name: {companyname}\n\n")
        csvfile.write(f"Stock Symbol: {symbol}\n\n")
       
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print("\n=======================================================================")        
    print(f"\nData for {companyname} (Stock Symbol: {symbol}) saved to {filename} 💾📁.")
    print("\n=======================================================================")
    
    
# Defines a function for plotting the stock data from the monthly and daily time series using the matplotlib and pyplot and the 
# matplotlib.ticker function formatter 
def stockdataplotter(xaxislabels,yaxislabels,companyname,figuresize,monthlyordaily,figurefilename):
    
    # Defines a function that will format the y-axis labels with the $ in front of them
    def dollar(x,pos):
        return f"${x:.0f}"
    
    # Uses the dollar function to create a formatter
    formatter = FuncFormatter(dollar)
    
    # Creates a figure with the figuresize
    pyplot.figure(figsize = figuresize)
    
    # Plots the line chart with the linestyle and the line color and marker at each point
    pyplot.plot(xaxislabels,yaxislabels,linestyle = "--", marker = "o", color = "red")
    
    # Sets the title of the chart, using the company name
    pyplot.title(f"{companyname} {monthlyordaily} Close Line Chart")
    
    # Sets the label for the x-axis and y axis
    pyplot.xlabel("Dates")
    pyplot.ylabel("Closing Price")
    
    # Rotates the x-axis labels (dates) for better readability to be tilted towards the left 45 degrees
    pyplot.xticks(rotation = 45)
    
    # Applies the dollar sign formatter to the y-axis
    pyplot.gca().yaxis.set_major_formatter(formatter)  
    
    # Turns on gridlines in the background for better readability of the chart
    pyplot.grid(True)
    
    # Adjusts the layout to prevent overlap of labels and titles
    pyplot.tight_layout()
    
    # Saves the plot image to the users downloads folder and prints a file saved message
    pyplot.savefig(figurefilename)
    print("\n=======================================================================") 
    print(f"\nPlot image for {companyname} saved as {figurefilename}🖼️.")
    print("\n=======================================================================")
    
    # Displays the line chart and prints a message
    print(f"\nBelow is the {monthlyordaily} Line Chart for {companyname}📈.")
    print("\n=======================================================================")
    pyplot.show()
    
# -------------------------------------------    
#
# Main Program
#
# -------------------------------------------   

# Filename Version Number variable so the CSV and PNG files dont get overwritten each time
filenummonth = 0
filenumday = 0

# Grabs todays date for use in the PNG and CSV filenaming later
todaydate = importeddate.today()

# Prints the welcome message
print("\n=======================================================================")
print("\n📈 Welcome to the Stock Market Tool!")
print("\n=======================================================================")
print("\nThis program lets you:\n")
print(" • Look up information about the monthly history of the stock price.")
print(" • Look up information about the daily history of the stock price.")
print(" • Export the daily or monthly stock price info to a CSV file.")
print(" • Shows the close price info as a line chart and saves to a PNG file.")
print(" • Look up overview information about the company.")
print(" • Recieve investment advice.")
print("\n=======================================================================")

# -------------------------------------------    
#
# Stock Symbol Ask
#
# -------------------------------------------

# Puts the whole program into a while loop so the user if wanted later down can change the stock they want to view 
# without having to re run the program
while True:
    
    # Starts a while loop to ask for a stock symbol until it is confirmed to be valid
    while True:
        
        # Asks the user to confirm if they know the stock symbol
        stocksymbolquestion = input("\n\nDo you know the stock symbol for the company you would like to view?\n\nIf \'YES\' ✅ press (1), if \'NO\' ❌ press (2):").strip()
        
        # If the user selects: 1
        # Continues on in the program to the next phase
        if stocksymbolquestion == "1":
            break
        
        # If the user selects: 2
        # Opens a webpage listing stock symbols to help them find one
        elif stocksymbolquestion == "2":
            myurl = "https://stockanalysis.com/stocks/"
            print("\nHere is a list of the company's stock symbols 📋.")
            webbrowser.open_new(myurl)
            break
        
        # Any other input, Display an invalid input message and make the user try again
        else:
            print("Your input was invalid, please try again.")

# -------------------------------------------    
#
# User Stock Symbol Input and Validation
#
# -------------------------------------------

    # Starts a while loop to ask for a stock symbol until it is confirmed to be valid
    while True:
        
        #Asks the user to enter a stock symbol, strips both leading and trailing spaces and, converts to uppercase to match how the symbols are listed in the API
        userstockchoice = input("\n\nPlease enter a valid stock symbol: ").strip().upper()
        
        # Checks to see if the stock symbol is valid and if so breaks out of the loop
        try: 
            overview_data = overview(userstockchoice)
            usersymbolchecktest = overview_data["Symbol"]
            companynamechecktest = overview_data["Name"]
            print(f"\n{userstockchoice} is a valid stock symbol for the company with the name {companynamechecktest}✅.")
            break
        
        # If the symbol is not found it will display an error message and prompt the user to try again
        except KeyError:
            print(f"\n{userstockchoice} is not a valid stock symbol ❌. Please try again.")

# -------------------------------------------    
#
# Main Menu Options
#
# -------------------------------------------

    # Starts a while loop to ask the user to either choose one of the options or quit the program
    while True:
        
        # Prints out the users choices and the chosen stock symbol
        print("\n=======================================================================") 
        print(f"\nYou are looking at {companynamechecktest} with the symbol {usersymbolchecktest}.")         
        print("\n📋 Please choose an option.")
        print("\n=======================================================================")
        print("1. View stock data, save to CSV, and view line chart display.")
        print("2. View company information.")
        print("3. Get investment advice.")
        print("4. Change the stock you'd like to view.")
        print("q. To quit.")
        
        # Asks the user to choice a corresponding number or the q letter with the listed choices
        userchoices = input("\nChoose an option (1–4) or 'q' to quit: ").strip()
        
# -------------------------------------------
#
# Stock Data (Monthly & Daily) (User Choice 1)
#
# -------------------------------------------     
        
        # If the user chooses (1): to view stock data and save to a CSV file
        if userchoices == "1":
            
                while True:
                    
                    # Asks user if they want to see daily or monthly stock data
                    monthlyordailychoice = input("\nView (1) Monthly Stock Data (12 months prior)\n\nOR\n\nView (2) Daily Stock Data (30 days prior): ").strip()
                   
                   # If the user chooses monthly data
                    if monthlyordailychoice == "1":
                        
                        # Gets the past 12 months of stock information and returns it to the main program
                        monthlydatainfo = timeseriesmonthly(userstockchoice)
                        
                        # Prints the company name header
                        print("\n-------------------")
                        print(f"\n{companynamechecktest}")
                        print("\n-------------------")
                          
                        # Loop through each month's stock data and print with the header
                        for month in monthlydatainfo:
                            print("\n-------------------")
                            print(f"Date:   {month['Date']}")
                            print(f"Open:   ${month['Open']:.2f}")
                            print(f"High:   ${month['High']:.2f}")
                            print(f"Low:    ${month['Low']:.2f}")
                            print(f"Close:  ${month['Close']:.2f}")
                            print("-------------------")
                    
                        # Initializes empty lists for storing the monthly dates and monthlycloses
                        monthlydatesforchart = []
                        monthlyclosesforchart = []
                        
                        # Loop through each month's close and date and append it to the respective list
                        for month in monthlydatainfo:
                            
                            # Appends dates and each close value
                            monthlydatesforchart.append(month["Date"])
                            monthlyclosesforchart.append(month["Close"])
                            
                        # Reverses the lists to get them in order from oldest to newest
                        monthlydatesforchart.reverse()
                        monthlyclosesforchart.reverse()
                        
                        # Sets the graph size
                        chartsize = (5.5,3)
                        
                        # Variable for naming the chart if its either monthly or daily
                        MONTHorDAILY = "Monthly"
                        
                        # Adds number to version counter
                        filenummonth += 1
                        
                        # File name for the monthly line chart
                        chartfilename = f"MonthlyLineChartFor{companynamechecktest}{todaydate}VERSION{filenummonth}.png"
                        
                        # Calls the stock data plotter function
                        stockdataplotter(monthlydatesforchart,monthlyclosesforchart,companynamechecktest,chartsize,MONTHorDAILY,chartfilename)
                        
                        # Exporting of file to a CSV File 
                        filename = f"MonthlyDataInfoFor{companynamechecktest}{todaydate}VERSION{filenummonth}.csv"
                        CSVsave(monthlydatainfo,filename,userstockchoice,companynamechecktest)
                        
                        # Exits the loop
                        break


                    # If the user chooses daily data        
                    elif monthlyordailychoice == "2":
                        
                        # Gets the past 30 days of stock information and returns it to the main program
                        dailydatainfo = timeseriesdaily(userstockchoice)
                        
                        # Prints the company name header
                        print("\n-------------------")
                        print(f"\n{companynamechecktest}")
                        print("\n-------------------")
                        
                        # Loop through each day's stock data and print with the header
                        for day in dailydatainfo:
                            print("\n-------------------")
                            print(f"Date:   {day['Date']}")
                            print(f"Open:   ${day['Open']:.2f}")
                            print(f"High:   ${day['High']:.2f}")
                            print(f"Low:    ${day['Low']:.2f}")
                            print(f"Close:  ${day['Close']:.2f}")
                            print("-------------------")
                            
                        # Initializes empty lists for storing the daily dates and daily closes
                        dailydatesforchart = []
                        dailyclosesforchart = []
                            
                        # Loop through each day's close and date and append it to the respective list
                        for day in dailydatainfo:
                            
                            # Appends dates and each close value
                            dailydatesforchart.append(day["Date"])
                            dailyclosesforchart.append(day["Close"])
                            
                        # Reverses the lists to get them in order from oldest to newest
                        dailydatesforchart.reverse()
                        dailyclosesforchart.reverse()
                        
                        # Sets the graph size
                        chartsize = (14,6)
                        
                        # Variable for naming the chart if its either monthly or daily
                        MONTHorDAILY = "Daily"
                        
                        # Adds number to version counter
                        filenumday += 1
                        
                        # File name for the daily line chart
                        chartfilename = f"DailyLineChartFor{companynamechecktest}{todaydate}VERSION{filenumday}.png"
                        
                        # Calls the stock data plotter function
                        stockdataplotter(dailydatesforchart,dailyclosesforchart,companynamechecktest,chartsize,MONTHorDAILY,chartfilename) 
                        
                        # Exporting of file to a CSV File 
                        filename = f"DailyDataInfoFor{companynamechecktest}{todaydate}VERSION{filenumday}.csv"
                        CSVsave(dailydatainfo,filename,userstockchoice,companynamechecktest)
                        
                        # Exits the loop
                        break
            
                    # If the user inputs anything other than 1 for monthly data and 2 for daily data they will recieve this invalid input message
                    # and be prompted to enter their input again
                    else:
                        print("Your input was invalid. Please try again.")

                        
# -------------------------------------------
#
# Stock Overview  (User Choice 2)
#
# -------------------------------------------    

        # If the user chooses (2): to view the companies information
        elif userchoices == "2":
            
            # Gets the stored Stock Overview Information 
            stock_data = overview_data
          
            # Prints the Stock Information header for the overview choice
            print("\n\nStock Information📈")
            print("--------------------")

            # Prints out the stock overview informaton
            print("Symbol:", stock_data["Symbol"])
            print("\nName:", stock_data["Name"])
            print("\nAsset Type:", stock_data["Asset Type"])
            print("\nWebsite:", stock_data["Official Site"])
            print("\nDescription:", stock_data["Description"])
            print("\nExchange:", stock_data["Exchange"])
            print("\nCurrency:", stock_data["Currency"])
            print("\nCountry:", stock_data["Country"])
            print("\nAddress:", stock_data["Address"].title())
            print("\nSector:", stock_data["Sector"].title())
            print("\nIndustry:", stock_data["Industry"].title())
        
# -------------------------------------------
#
# Investment Advice (User Choice 3)
#
# ------------------------------------------- 

        # If the user chooses (3): to get investment advice
        elif userchoices == "3":
            
            # Define the valid options for stock market status in a tuple
            stockmarketconditionsoptions = ('Decreased', 'Stable', 'Increased')
            
            # Prompt the user until they enter a valid market status
            while True:
                
                # Ask for input and normalize the format
                market_status = input("\nPlease enter the current stock market condition (Decreased, Stable, or Increased): ").title().strip()
                
                # Check if the user's input is valid
                if market_status in stockmarketconditionsoptions:
                    break # Exit the loop if valid
                
                else:
                    # Inform the user that their input is invalid and prompt them again
                    print(f"❌ '{market_status}' is not a valid option.")
                    print("Please choose from: Decreased, Stable, Increased.\n")

            
            # Gets the stored Stock Overview Information
            stock_data = overview_data
            
            # Gets the advice from the investment_advice function which takes the overview data and the market status as arguments 
            advice = investment_advice(stock_data,market_status)

            # Prints headers for the investment advice
            print("\n-----------------------------------------------------------------------")
            print(f"\n💡 Investment Advice for company named {companynamechecktest}:")
            print("\n-----------------------------------------------------------------------")
            
            # Prints the string with the investment advice that was returned from the investment_advice function
            print(advice)
       
# -------------------------------------------
#
# Changing Stock (User Choice 4)
#
# -------------------------------------------    
        
        # If the user chooses (4): to change their stock choice
        elif userchoices == "4":
            
            # Prints a reverting message to let the user know they will be back at the stock pick menu
            print("\nReverting back to stock selection menu.")
            
            # Breaks out of the loop to return you to the stock selection
            break
            
        
# -------------------------------------------
#
# Quitting Program (User Choice q)
#
# -------------------------------------------         
       
        # If the user chooses (q): to quit the program
        elif userchoices.lower() == "q":
            
            # Prints a goodbye message
            print("\nThank you for using this stock market program! Goodbye👋.")
            
            # Ends the program completely using the exit function from the sys module
            # Instead of using a break as using a break would just take it back to the main menu instead of quitting
            sys.exit()
        
# -------------------------------------------
#
# Invalid Input Message
#
# -------------------------------------------     

        # If the users choice is invalid and not 1,2,3,4, or q prints out an invalid input message
        else:
            print("Sorry your input was invalid, please enter 1,2,3,4, or q to quit.")
            
            
