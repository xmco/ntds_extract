import argparse
from dissect.esedb import EseDB
import csv


FIELDS = { # List of attributes to search
    'cn':'ATTm3', 
    'RDN': 'ATTm589825',
    'sAMAccountName':'ATTm590045',
    'logonCount':'ATTj589993',
    'primaryGroupID':'ATTj589922',
    'operatingSystem':'ATTm590187',
    'minPwdLength': 'ATTj589903', 
    'description':'ATTm13',
    'LDAPName': 'ATTm131532'
}


def extract_field(file_path):
    output = []
    with open(file_path, "rb") as fh:
        db = EseDB(fh)
        datatable = db.table("datatable")
        for record in datatable.records():
            line = []
            for field in FIELDS.values():
                line.append(record.get(field)) # eg. record.get('ATTm590045') => askywalker
            output.append(line)
        return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract NTDS fields.')
    parser.add_argument('-f', '--file', action="store", dest="ntds_file", required=True,
                      help='NTDS file to parse (ntds.dit)')
    parser.add_argument('-o', '--output', action="store", dest="out_file", required=True,
                      help='CSV output file')
    
    args = parser.parse_args()
    print("Extracting attribute values from your NTDS file...", end="")
    fields = extract_field(args.ntds_file)

    # get the headers from the keys and values of the FIELDS dictionary
    headers1 = list(FIELDS.keys())
    headers2 = list(FIELDS.values())
    # write output to a CSV file
    with open(args.out_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers1) # write headers LDAP Name
        writer.writerow(headers2) # write headers ATT name
        writer.writerows(fields) # write data
    print("Done")