import numpy as np
import requests
from collections import OrderedDict
import matplotlib.pyplot as plt
import json

# url = "https://kommun.jensnylander.com/api/municipalities?limit=20&offset=0"

headers = {
    "accept": "application/json",
    "x-api-key": "YOUR_API_KEY"
}

# response = requests.get(url, headers=headers)


status_code = 200
limit = 2#20
n = 0
max_municipalities = 4
municipalities = OrderedDict()
vendors = OrderedDict()

while status_code == 200:
    url = (f"https://kommun.jensnylander.com/api/municipalities?" +
           f"limit={limit}&offset={n*limit}")
    response = requests.get(url, headers=headers)
    status_code = response.status_code

    if len(response.json()['result']) > 0:
        for i, municipality in enumerate(response.json()['result']):
            print(f"{(n*limit) + i + 1}. {municipality['name']}")
            if municipality['municipalityId'] in municipalities:
                print(f"Duplicate ID: {municipality['municipalityId']}")
                input(f"Duplicate ID: {municipality['municipalityId']}")
            municipalities[municipality['municipalityId']] = municipality

            mun_id = municipality['municipalityId']

            m = 0

            while True:
                vender_url = (f"https://kommun.jensnylander.com/api/" +
                              f"municipalities/{mun_id}/vendors?{limit}&" +
                              f"offset={m*limit}")
                vendor_response = requests.get(vender_url, headers=headers)
                # print(f"vendor_response: {vendor_response}")

                if len(vendor_response.json()['result']) > 0:
                    for j, vendor in enumerate(vendor_response.json()['result']):

                        # vendor_reg_num = int(vendor['vendorCompanyRegistrationNumber'])
                        vendor_reg_num = vendor['vendorCompanyRegistrationNumber']
                        if vendor_reg_num in vendors:
                            vendors[vendor_reg_num]['municipalities'].append(mun_id)
                        else:
                            # print(f"vendor['vendorCompanyRegistrationNumber']: " +
                            #       f"{type(vendor['vendorCompanyRegistrationNumber'])}")
                            vendors[vendor_reg_num] = vendor
                            # print(f"vendor['vendorCompanyRegistrationNumber']: " +
                            #       f"{vendors[vendor_reg_num]}")
                            vendors[vendor_reg_num]['municipalities'] = [mun_id]

                        # print(f"\t{(m*limit) + j + 1}. {vendor['vendorName']}" +
                        #       f" -- {len(vendors[vendor_reg_num]['municipalities'])}")
                else:
                    break

                m += 1

        # print(f"status_code: {status_code}: len: {len(response.json()['result'])}")
        # print(f"response: {response.json()['metadata']}")
    else:
        break

    n += 1

    if n * limit >= max_municipalities:
        break

# JSON dump all municipalities and vendors to individual files
with open('municipalities.json', 'w') as file:
    json.dump(municipalities, file, indent=4)

with open('vendors.json', 'w') as file:
    json.dump(vendors, file, indent=4)


# Create a bar graph of the number of municipalities per vendor, where the
# x-axis represents the number of municipalities and the y-axis represents the
# number of vendors with that number of municipalities
num_mun = [len(vendor['municipalities']) for vendor in vendors.values()]
unique_num_mun = np.unique(num_mun)
print(f"unique_num_mun: {unique_num_mun}")
num_vendors = [num_mun.count(num) for num in unique_num_mun]

plt.bar(unique_num_mun, num_vendors)
plt.xlabel('Number of Municipalities')
plt.ylabel('Number of Vendors')
plt.title('Number of Municipalities per Vendor')
plt.show()
