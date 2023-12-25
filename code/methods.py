# Import packages
import requests
from bs4 import BeautifulSoup as bs


# Method that returns the number of pages of a base url
def get_number_of_pages(base_url):
    req = requests.get(base_url)
    soup = bs(req.text, "html.parser")

    # Maximum number of pages
    numpages_html = soup.find_all("li", {"class": "pagination__item"})
    numpages = get_number(numpages_html[-2].text)
    return numpages


# Method that returns that only returns the simple digits given a string
def get_number(string):
    allowed = [str(i) for i in range(10)]
    str_numbers = list(filter(lambda x: x in allowed, [*string]))
    joined = "".join(str_numbers)
    value = int(joined)
    return value


# Method that returns all the rental listings urls of a given city
def get_all_listing_urls(city):
    print("Beginning to extract the listing urls")

    numpages = get_number_of_pages(
        f"https://www.pararius.nl/huurwoningen/{city.lower()}"
    )

    listing_urls = []
    for i in range(1, numpages + 1):
        # Obtain link and soup of page
        page_url = f"https://www.pararius.nl/huurwoningen/{city.lower()}/page-{str(i)}"

        req = requests.get(page_url)
        s = bs(req.text, "html.parser")

        # Obtain links of listings on page
        listings_on_page_html = s.find_all(
            "a",
            {
                "class": "listing-search-item__link listing-search-item__link--title"
            },
        )
        listing_on_page_urls = [
            "https://www.pararius.nl" + link.get("href")
            for link in listings_on_page_html
        ]

        # Add listings of page to list
        listing_urls += listing_on_page_urls

    return listing_urls


# Method that returns a scraped dictionary given urls of listings
def get_scraped_dict(urls):
    print(
        """You can expect error messages: not all listings have all information,
          especially regarding the furnishing and number of bathrooms.
          """
    )

    # Dictionary that contains the variables that are found in the same way by Beautiful Soup, the last entry is a list containing the variables that are numbers
    simple_extractions = {
        "price": ["div", {"class": "listing-detail-summary__price"}],
        "area": [
            "li",
            {
                "class": "illustrated-features__item illustrated-features__item--surface-area"
            },
        ],
        "nrooms": [
            "li",
            {
                "class": "illustrated-features__item illustrated-features__item--number-of-rooms"
            },
        ],
        "nbedrooms": [
            "dd",
            {
                "class": "listing-features__description listing-features__description--number_of_bedrooms"
            },
        ],
        "nbathrooms": [
            "dd",
            {
                "class": "listing-features__description listing-features__description--number_of_bathrooms"
            },
        ],
        "furnished": [
            "li",
            {
                "class": "illustrated-features__item illustrated-features__item--interior"
            },
        ],
        "agent": ["a", {"class": "agent-summary__title-link"}],
        "status": [
            "dd",
            {
                "class": "listing-features__description listing-features__description--status"
            },
        ],
        "description": [
            "div",
            {"class": "listing-detail-description__content"},
        ],
        "numbers": ["price", "area", "nrooms", "nbedrooms", "nbathrooms"],
    }

    scraped_dict = {}

    for url in urls:
        listing_dict = {}

        try:
            # URL
            listing_dict["url"] = url

            # Code
            code = url.split("/")[-2]
            listing_dict["code"] = code

            # Obtain html
            req = requests.get(url)
            soup = bs(req.text, "html.parser")

            # Extract all simple elements
            for key, value in simple_extractions.items():
                if key == "numbers":
                    continue

                try:
                    item_html = soup.find(value[0], value[1])
                    if key in simple_extractions["numbers"]:
                        item = get_number(item_html.text)
                    else:
                        item = item_html.text
                    listing_dict[key] = item
                except:
                    listing_dict[key] = "NA"
                    print(
                        f"Something went wrong with listing {url} when extracting {key}"
                    )

            # Edit description
            listing_dict["description"] = listing_dict["description"].replace(
                "\n", " "
            )

            # Price per bedroom
            price_per_bedroom = round(
                listing_dict["price"] / listing_dict["nbedrooms"]
            )
            listing_dict["price_per_bedroom"] = price_per_bedroom

            # Neighbourhood
            # Zipcode
            location_html = soup.find(
                "div", {"class": "listing-detail-summary__location"}
            )
            location_split = location_html.text.split()
            zipcode = location_split[0] + location_split[1]
            neighborhood = " ".join(location_split[2:])
            neighborhood = neighborhood.replace("(", "").replace(")", "")
            listing_dict["zipcode"] = zipcode
            listing_dict["neighborhood"] = neighborhood

            # Street
            street_htmls = soup.find_all("a", {"class": "breadcrumbs__link"})
            street = street_htmls[-1].text
            listing_dict["street"] = street

            # Offered since
            since_html = soup.find(
                "dd",
                {
                    "class": "listing-features__description listing-features__description--offered_since"
                },
            )
            since_down_html = since_html.find(
                "span", {"class": "listing-features__main-description"}
            )
            since = since_down_html.text
            listing_dict["since"] = since

            # Added to parent dictionary
            scraped_dict[code] = listing_dict

        except Exception as e:
            print(f"something went wrong with {url}")
            print(e)

    return scraped_dict


# Method that puts a dictionary in a sheet
def put_dictionary_in_sheet(order, var_display_dict, scraped_dict, sheet):
    # Give the columns names
    for i in range(len(order)):
        var = order[i]
        sheet.cell(row=1, column=i + 1, value=var_display_dict[var])

    # Enter info of listings

    row_number = 2
    # Loop over all listings
    for _, dict in scraped_dict.items():
        # Loop over all info
        for i in range(len(order)):
            var = order[i]
            sheet.cell(row=row_number, column=i + 1, value=dict[var])

        row_number += 1


# Methods that filters the listings (can be changed as desired)
def filter_listings(_, listing_dict, city):
    if listing_dict["neighborhood"] in [
        "Tarwewijk",
        "Oosterflank",
        "Carnisse",
        "Zuidwijk",
        "Liskwartier",
        "Zestienhoven",
        "Bloemhof",
        "Lombardijen",
        "Hillegersberg",
        "Oud Charlois",
        "Groot IJsselmonde",
        "Oud IJsselmonde",
        "Zuidplein",
        "Het Lage Land",
        "Hillesluis",
        "Feijenoord",
        "Vreewijk",
    ]:
        return False
    elif listing_dict["price_per_bedroom"] > 750:
        if city == "Amsterdam" and listing_dict["price_per_bedroom"] < 900:
            return True
        else:
            return False
    else:
        return True


# Dictionary that convert the variables to column names
var_display_dict = {
    "price": "Price",
    "area": "Surface Area",
    "nrooms": "#Rooms",
    "nbedrooms": "#Bedrooms",
    "nbathrooms": "#Bathrooms",
    "furnished": "Furnished",
    "agent": "Agent",
    "status": "Status",
    "zipcode": "Zipcode",
    "neighborhood": "Neighborhood",
    "street": "Street",
    "since": "Available since",
    "url": "Link",
    "price_per_bedroom": "Price per bedroom",
}

# Order of the columns
order = [
    "price",
    "nbedrooms",
    "nrooms",
    "price_per_bedroom",
    "area",
    "neighborhood",
    "street",
    "zipcode",
    "since",
    "agent",
    "url",
]
