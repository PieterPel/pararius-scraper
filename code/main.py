
import methods
import openpyxl
import pickle
import os

cities = ["Rotterdam", "Amsterdam"]

for city in cities:

    # Open the workbook
    os.chdir("..")
    wb = openpyxl.load_workbook("output/pararius.xlsx")

    # Extract the urls of the city
    urls = methods.get_all_listing_urls(city.lower())

    # Extract the scraped dictionary of the city
    scraped_dict = methods.get_scraped_dict(urls)

    # Put all the listings in a sheet
    ws_all = wb[city + " All"]
    methods.put_dictionary_in_sheet(methods.order, methods.var_display_dict, scraped_dict, ws_all)

    # Put the filtered listings in a sheet
    ws_filtered = wb[city + " Filtered"]
    filtered_dict = {key: value for key, value in scraped_dict.items() if methods.filter_listings(key, value, city)}
    methods.put_dictionary_in_sheet(methods.order, methods.var_display_dict, filtered_dict, ws_filtered)

    # Save dictionaries using pickle
    with open(f'output/pickles/{city}_all.pkl', 'wb') as fp:
        pickle.dump(scraped_dict, fp)

    with open(f'output/pickles/{city}_filtered.pkl', 'wb') as fp:
        pickle.dump(filtered_dict, fp)

    # Save workbook
    wb.save('output/pararius.xlsx')



