import xml.etree.ElementTree as ET
import json
import time

# Parse function reading from a path
def parseXML(url):
    tree = ET.parse(url)
    return tree

# Helper function to parse a string amount into integer
def toMoney(amount):
    amount_in_cents = int(amount)
    return amount_in_cents


def main():
    # Gets parsed xml
    xmlParsed = parseXML('./OTA_AirSeatMapRS.xml')
    OTA_root = xmlParsed.getroot()
    output = []
    # This is the what allow us to get subtrees in the xml
    # without this .iter, .find, .findall are not able to find elements
    namespace = "{http://www.opentravel.org/OTA/2003/05/common/}"

    start = time.time()

    # Iterate over "RowInfo" because that's the element holding
    # all the info we need for this challenge
    for row in OTA_root.iter(namespace + 'RowInfo'):
        # CabinType is the Cabin class
        row_class = row.get('CabinType')

        # iterate over all the seat info elements
        # this will get us the "id" and holds all the other info we need
        for seat_info in row.findall(namespace + 'SeatInfo'):
            seat = {}
            seat_service_info = seat_info.find(namespace + 'Service')
            seat_summary = seat_info.find(namespace + 'Summary')
            seat["id"] = seat_summary.get('SeatNumber')
            seat_availability = seat_summary.get('AvailableInd')

            # because xml holds string types
            # let's check for the string "False" to check
            # if the seat is available
            if seat_availability == "false":
                seat["is_available"] = False
                seat_status = seat_info.find(namespace + 'Status')

                # Some elements doesn't have "Status"
                # let's check the type in order to keep the format across all items
                if seat_status is not None:
                    seat["status"] = seat_status.text
                else:
                    seat["status"] = 'Not Available'
            else:
                seat["is_available"] = True
                seat["status"] = 'Available'

            seat["carbinClass"] = row_class

            # Some elements don't have "ServiceInfo"
            # Which holds our prices and taxes
            # Let's check type in order to keep the format across all items
            if seat_service_info is not None:
                amount = seat_service_info.find(namespace + 'Fee')
                taxes = amount.find(namespace + 'Taxes')
                seat["price"] = toMoney(amount.get('Amount'))
                seat["taxes"] = toMoney(taxes.get('Amount'))
            else:
                seat["price"] = "NA"
                seat["taxes"] = "NA"
            

            for feature in seat_info.findall(namespace + 'Features'):
                feature_description = feature.get('extension')
                if "features" not in seat:
                    seat["features"] = {}

                # We care about the features element that doesn't have the property extension
                # if it doesn't this is our seat type (Window, etc)
                if feature_description is not None:
                    seat["features"][feature_description] = feature.text
                else:
                    seat["type"] = feature.text
            output.append(seat)
    
    # Write json output to out.json file
    with open('output.json', 'w') as outfile:
        json.dump(output, outfile)

    end = time.time()

    print "Script ran in " + str(end - start) + " seconds."
if __name__ == "__main__":
    main()