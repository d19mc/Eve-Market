# Module Import
import requests
from colorama import Fore, Back, Style, init
import string
import urllib.request # To check internet connection
# Variable Import
from locationids import LOCATIONIDS
from systemids import SYSTEMIDS
from typeids import TYPEIDS

def check_connection():
    # Check Internet connection
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        print("\n    " + Back.RED + " No Internet Connection " + Back.RESET, end='')
        return False

# Func to get key from value in dictionary
def get_key(dict, val):
    for x in dict:
        for key, value in x.items():
             if val == value:
                 return key
    return None


# Returns object name from type_id
def translate_id(type, id):

    id = str(id)

    if type == "location":
        for location in LOCATIONIDS:
            try:
                return location[id]
            except KeyError:
                continue
        return "Unsupported Location: Check In-Game"

    elif type == "system":
        for system in SYSTEMIDS:
            try:
                return system[id]
            except KeyError:
                continue
        return "Unsupported System: Check In-Game"

    elif type == "obj":
        for obj in TYPEIDS:
            try:
                return obj[id]
            except KeyError:
                continue
        return "Unsupported Object: Check In-Game"

    else:
        raise Exception("incorrectTypeError")


# Gets the data for specific region
def get_market_data(region, object):

    market_data = []
    api_types = ["latest", "dev", "v1", "legacy"]
    region_id = get_key(LOCATIONIDS, region)
    object_id = get_key(TYPEIDS, object)

    # Request order list from specific region
    # Try request from different file if one fails
    for i in range(3):

        try:

            # Checks every page in api and breaks loop if page is empty
            for page in range( 1 , 2147483648 ):

                r = requests.get(url = f"https://esi.evetech.net/{api_types[i]}/markets/{region_id}/orders/?datasource=tranquility&order_type=all&page={page}&type_id={object_id}")

                # Report Error if page is non-existent
                if r.status_code == 200:

                    # Break loop if no data found on next page
                    if r.json() == []:
                        break

                    else:
                        market_data.extend(r.json())
                        continue

                elif r.status_code == 404:
                    raise Exception("Page Not Found")

                else:
                    print("Error Occured.")

        except Exception:
            continue

        else:
            break

    return market_data


# Replaces the IDs in the requested json with human-recognizable names
def format_market_data(gibberish):

    for x in range(len(gibberish)):

        # Replaces location_ids and system_ids with corrosponding names
        gibberish[x]['location_id'] = translate_id("location", gibberish[x]['location_id'])
        gibberish[x]['system_id'] = translate_id("system", gibberish[x]['system_id'])

    return gibberish


# Display the input data in a neat manner
def display_market_data(item, data):

    # Template for clean output
    sell_template =  "{5:13}  {0:13}  {1:16}  {3:12}  {4:75}  {2:10}  "
    buy_template =   "{0:13}  {2:13}  {1:16}  {4:12}  {5:75}  {3:10}  "

    # Request ASCII text art for title
    r = requests.get(f"http://artii.herokuapp.com/make?text={item}")

    if r.status_code == 200:
        ascii_art = r.text
        print("\n" + ascii_art)
    else:
        # Print this in the unlikely event that the website is down
        print("\n" + Style.BRIGHT + item + Style.RESET_ALL)

    # Display Sell Orders
    print("\n" + Back.GREEN + "SELL ORDERS" + Back.RESET)
    print(Back.GREEN + sell_template.format("QUANTITY REM.", "PRICE", "ORDER ID", "SYSTEM", "LOCATION", "QUANTITY TOT.") + Back.RESET)

    for order in range(len(data)):
        if data[order]['is_buy_order'] == False:
            try:
                # Apply template for tidy printing
                print(Back.GREEN + sell_template.format(str(data[order]['volume_remain']), f"Ƶ {data[order]['price']}", str(data[order]['order_id']), data[order]['system_id'], data[order]['location_id'], str(data[order]['volume_total'])) + Back.RESET)
            except:
                pass

    # Display Buy Orders
    print("\n" + Back.RED + "BUY ORDERS" + Back.RESET)
    print(Back.RED + buy_template.format("QUANTITY", "PRICE", "RANGE", "ORDER ID", "SYSTEM", "LOCATION") + Back.RESET)

    for order in range(len(data)):
        if data[order]['is_buy_order'] == True:
            try:
                # Apply template for tidy printing
                print(Back.RED + buy_template.format(str(data[order]['volume_remain']), f"Ƶ {data[order]['price']}", str(data[order]['range']), str(data[order]['order_id']), data[order]['system_id'], data[order]['location_id']) + Back.RESET)
            except:
                pass


def compare_market_data(region_list):

    item = region_list[0]
    region_data = {}
    region_prices = {}

    # Gives each region, market data for specified item.
    for x in range(1, len(region_list)):
        region_data[region_list[x]] = format_market_data(get_market_data(region_list[x], item))

    # Gathers lowest, average and highest price for item in each region.
    for region in region_data.keys():

        # Reset variables for each region
        region_prices[region] = {}
        sell_prices = []
        buy_prices = []

        for data in region_data[region]:

            # Selling prices
            if data['is_buy_order'] == False:

                sell_prices.append(data['price'])

            # Buying prices
            if data['is_buy_order'] == True:

                buy_prices.append(data['price'])

        try:

            # Variables declared seperate from dictionary for clarity in code.

            sell_lowest = min(sell_prices)
            sell_average = round(sum(sell_prices) / len(sell_prices), 2)
            sell_highest = max(sell_prices)

            buy_lowest = min(buy_prices)
            buy_average = round(sum(buy_prices) / len(buy_prices), 2)
            buy_highest = max(buy_prices)

            # Declare variables above as values for the keys below in 'region_prices[region]' dictionary

            region_prices[region]['sell'] = {}

            region_prices[region]['sell']['lowest'] = sell_lowest
            region_prices[region]['sell']['average'] = sell_average
            region_prices[region]['sell']['highest'] = sell_highest

            region_prices[region]['buy'] = {}

            region_prices[region]['buy']['lowest'] = buy_lowest
            region_prices[region]['buy']['average'] = buy_average
            region_prices[region]['buy']['highest'] = buy_highest

        except ValueError:

            # Run when there are no orders for this item in the region

            region_prices[region]['sell'] = {}

            region_prices[region]['sell']['lowest'] = 0
            region_prices[region]['sell']['average'] = 0
            region_prices[region]['sell']['highest'] = 0

            region_prices[region]['buy'] = {}

            region_prices[region]['buy']['lowest'] = 0
            region_prices[region]['buy']['average'] = 0
            region_prices[region]['buy']['highest'] = 0

    # Gather the amount of orders in each region

    amount_of_sell_orders = {}
    amount_of_buy_orders = {}

    for region in region_data.keys():

        amount_of_sell_orders[region] = 0
        amount_of_buy_orders[region] = 0

        for order in region_data[region]:

            if order['is_buy_order'] == False:
                amount_of_sell_orders[region] += 1

            if order['is_buy_order'] == True:
                amount_of_buy_orders[region] += 1

    # Request ASCII text art for title
    r = requests.get(f"http://artii.herokuapp.com/make?text={item}")

    if r.status_code == 200:
        ascii_art = r.text
        print("\n" + ascii_art)
    else:
        # Print this in the unlikely event that the website is down
        print("\n" + Style.BRIGHT + item + Style.RESET_ALL)

    # Template for clean output
    template = "{0:18}  {1:18}  {2:18}  {3:18}  {4:18}"

    # Selling Orders
    print("\n" + Back.GREEN + "SELL ORDERS" + Back.RESET)
    print(Back.GREEN + template.format("REGION", "LOW. PRICE", "AVG. PRICE", "HI. PRICE", "NO. SELL ORDERS") + Back.RESET)

    for region in region_data.keys():
        print(Back.GREEN + template.format(region, "Ƶ " + str(region_prices[region]['sell']['lowest']), "Ƶ " + str(region_prices[region]['sell']['average']), "Ƶ " + str(region_prices[region]['sell']['highest']), str(amount_of_sell_orders[region])) + Back.RESET)

    # Buying Orders
    print("\n" + Back.RED + "BUY ORDERS" + Back.RESET)
    print(Back.RED + template.format("REGION", "LOW. PRICE", "AVG. PRICE", "HI. PRICE", "NO. BUY ORDERS") + Back.RESET)

    for region in region_data.keys():
        print(Back.RED + template.format(region, "Ƶ " + str(region_prices[region]['buy']['lowest']), "Ƶ " + str(region_prices[region]['buy']['average']), "Ƶ " + str(region_prices[region]['buy']['highest']), str(amount_of_buy_orders[region])) + Back.RESET)


# MAIN PROGRAM STARTS HERE
print("""
     ______           __  __            _        _
    |  ____|         |  \/  |          | |      | |
    | |____   _____  | \  / | __ _ _ __| | _____| |_
    |  __\ \ / / _ \ | |\/| |/ _` | '__| |/ / _ \ __|
    | |___\ V /  __/ | |  | | (_| | |  |   <  __/ |_
    |______\_/ \___| |_|  |_|\__,_|_|  |_|\_\___|\__| v1.0.1

    Made By: Dev Palastine (Eve Name)
""")

init() # Initialize colorama to enable stylizing.

while True:

    if check_connection() == False:
        input()
        break

    # User enters command here to operate program
    query = input("\nmarket>> ")

    if check_connection() == False:
        input()
        break

    # Check Internet connection
    try:
        urllib.request.urlopen('http://google.com')
    except:
        print("    " + Back.RED + " No Internet Connection " + Back.RESET, end='')
        input()
        break

    # Provide a list of commands
    if query == "help":
        print("""

{2}SYSTEM{1}

This command exits the application.
{0}exit{1}

This command clears the clutter within the terminal window.
{0}clear{1}


{2}MARKET{1}

This command collects Eve Market data for the given item within the given region and neatly displays it.
{0}search [item_name] | [region_name]{1}

This command collects Eve Market data for the given item in all given regions (at least 2) and compares the data between the regions with a neat visual representation.
Note: This may take up to a minute depending on the amount of regions given
{0}compare [item_name] | [region_name1] | [region_name2] | ... | [region_nameX]{1}

""".format(Fore.YELLOW, Fore.RESET, Fore.CYAN))


    # Clear the Console
    elif query == "clear":

        print('\x1b[2J')
        print("""
      ______           __  __            _        _
     |  ____|         |  \/  |          | |      | |
     | |____   _____  | \  / | __ _ _ __| | _____| |_
     |  __\ \ / / _ \ | |\/| |/ _` | '__| |/ / _ \ __|
     | |___\ V /  __/ | |  | | (_| | |  |   <  __/ |_
     |______\_/ \___| |_|  |_|\__,_|_|  |_|\_\___|\__|
        """)

    # Exit the Application
    elif query == "exit":
        break

    # search the Eve Market data for given item within given region.
    elif "search " in query:

        query = query.replace("search ", "").split(" | ")

        # Check if 'query' comprises valid inputs
        try:

            # To add support for items such as railguns and due to nums like 200mm.

            spaced_item = query[0].split(" ")

            for word in range(len(spaced_item)):

                if spaced_item[word] == "ii":
                    spaced_item[word] = spaced_item[word].upper()
                    continue

                for n in list(string.digits):

                    if n in spaced_item[word]:
                        spaced_item[word] = spaced_item[word].lower()
                        break
                    else:
                        spaced_item[word] = spaced_item[word].title()

            query[0] = " ".join(spaced_item)

            # Check if 'query[0]' is 'plex' because .title() won't work since plex is .upper() in-game.
            if query[0].lower() == "plex":
                query[0] = "PLEX"

            # Allow Null-Sec systems to be inputted at a .lower() level in console.
            for n in list(string.digits):
                if n in query[1]:
                    query[1] = query[1].upper()
                    break
                else:
                    query[1] = query[1].title()

            if get_key(LOCATIONIDS, query[1]) == None or get_key(TYPEIDS, query[0]) == None:
                print(Fore.RED + "Invalid Item or Region" + Fore.RESET)
                continue

        except:
            print(Fore.YELLOW + "Command Format: search [item_name] | [region_name]" + Fore.RESET)

        else:
            display_market_data(query[0], format_market_data(get_market_data(query[1], query[0])))

    elif "compare " in query:

        invalid_region = False
        query = query.replace("compare ","").split(" | ")

        # Check if 'query' comprises valid inputs
        try:

            # To add support for items such as railguns and due to nums like 200mm.

            spaced_item = query[0].split(" ")

            for word in range(len(spaced_item)):

                if spaced_item[word] == "ii":
                    spaced_item[word] = spaced_item[word].upper()
                    continue

                for n in list(string.digits):

                    if n in spaced_item[word]:
                        spaced_item[word] = spaced_item[word].lower()
                        break
                    else:
                        spaced_item[word] = spaced_item[word].title()

            query[0] = " ".join(spaced_item)

            # Check if 'query[0]' is 'plex' because .title() won't work since plex is .upper() in-game.
            if query[0].lower() == "plex":
                query[0] = "PLEX"


            # Allow Null-Sec systems to be inputted at a .lower() level in console.
            for region in range(1, len(query)):
                for n in list(string.digits):
                    if n in query[region]:
                        query[region] = query[region].upper()
                        break
                    else:
                        query[region] = query[region].title()

            if get_key(TYPEIDS, query[0]) == None:
                print(Fore.RED + "Invalid Item" + Fore.RESET)
                continue

            for x in range(1, len(query)):
                if get_key(LOCATIONIDS, query[x]) == None:
                    print(Fore.RED + f"Invalid Region: {query[x]}" + Fore.RESET)
                    invalid_region = True

            if invalid_region == True:
                invalid_region = False
                continue

        except:
            print(Fore.YELLOW + "Command Format: compare [item_name] | [region_name1] | [region_name2] | ... | [region_nameX]" + Fore.RESET)

        else:
            compare_market_data(query)

    else:
        if query == "":
            continue
        print(Fore.RED + "Invalid Command : type 'help' for manual" + Fore.RESET)
