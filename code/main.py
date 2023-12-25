import methods
import openpyxl
import pickle
import os
import config
import sys

cities = ["Rotterdam", "Amsterdam"]

for city in cities:
    # Open the workbook
    os.chdir(config.folder_location)
    wb = openpyxl.load_workbook("output/pararius.xlsx")

    # Extract the urls of the city
    urls = methods.get_all_listing_urls(city.lower())

    # Load the extracted urls from the previous time
    with open(f"output/txt_files/{city}_urls.txt", "r") as f:
        old_urls = [line for line in f]

    # Save the new urls
    with open(f"output/txt_files/{city}_urls.txt", "w") as f:
        for url in urls:
            f.write(url + "\n")

    # Get the new urls
    new_urls = [url for url in urls if url not in old_urls]

    # Get the removed urls
    removed_urls = list(set(old_urls) - set(urls))

    # Extract the scraped dictionary of the city
    scraped_dict = methods.get_scraped_dict(new_urls)

    # Load the pickle that has the dictionary of the old urls
    with open(f"output/pickles/{city}_all.pkl", "rb") as fp:
        old_dict = pickle.load(fp)

    # Remove the removed urls
    for code, dict in old_dict.items():
        if dict["url"] in removed_urls:
            del old_dict[code]

    # Combine the scraped dictionaries
    scraped_dict.update(old_dict)

    # Put all the listings in a sheet
    ws_all = wb[city + " All"]
    methods.put_dictionary_in_sheet(
        methods.order, methods.var_display_dict, scraped_dict, ws_all
    )

    # Put the filtered listings in a sheet
    ws_filtered = wb[city + " Filtered"]
    filtered_dict = {
        key: value
        for key, value in scraped_dict.items()
        if methods.filter_listings(key, value, city)
    }
    methods.put_dictionary_in_sheet(
        methods.order, methods.var_display_dict, filtered_dict, ws_filtered
    )

    # Save dictionaries using pickle
    with open(f"output/pickles/{city}_all.pkl", "wb") as fp:
        pickle.dump(scraped_dict, fp)

    with open(f"output/pickles/{city}_filtered.pkl", "wb") as fp:
        pickle.dump(filtered_dict, fp)

    # Save workbook
    wb.save("output/pararius.xlsx")

sys.exit(0)
