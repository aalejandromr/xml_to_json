import xml.etree.ElementTree as ET
import json

def parseXML(url):
    tree = ET.parse(url)
    return tree

def toMoney(amount):
    amount_in_cents = int(amount)
    return amount_in_cents


def main():
    xmlParsed = parseXML('./OTA_AirSeatMapRS.xml')
    OTA_root = xmlParsed.getroot()
    output = []
    namespace = "{http://www.opentravel.org/OTA/2003/05/common/}"
    for row in OTA_root.iter(namespace + 'RowInfo'):
        row_class = row.get('CabinType')
        for seat_info in row.findall(namespace + 'SeatInfo'):
            seat = {}
            seat_service_info = seat_info.find(namespace + 'Service')
            seat_summary = seat_info.find(namespace + 'Summary')
            seat["id"] = seat_summary.get('SeatNumber')
            seat_availability = seat_summary.get('AvailableInd')

            if seat_availability == "false":
                seat["is_available"] = False
                seat_status = seat_info.find(namespace + 'Status')
                if seat_status is not None:
                    seat["status"] = seat_status.text
                else:
                    seat["status"] = 'Not Available'
            else:
                seat["is_available"] = True
                seat["status"] = 'Available'

            seat["carbinClass"] = row_class
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

                if feature_description is not None:
                    seat["features"][feature_description] = feature.text
                else:
                    seat["type"] = feature.text
            output.append(seat)
    with open('output.json', 'w') as outfile:
        json.dump(output, outfile)

if __name__ == "__main__":
    main()