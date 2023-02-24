import argparse
from dissect.esedb import EseDB
import re

'''
    Recherche du nom de la colonne à partir de l'ID de l'attribut (Ex: 589983 => ATTq589983)
'''
def find_complete_record_name(complete_record_names, partial_record_name):
    for record_name in complete_record_names:
        
        if str(partial_record_name) == ''.join(re.findall(r'\d+', record_name)) :
            return record_name


def extract_columns_name(file_path):
    with open(file_path, "rb") as fh:
        db = EseDB(fh)
        datatable_col_names = []
        output = ''
        attributeID = 'ATTc131102'
        lDAPDisplayName = 'ATTm131532'
        datatable = db.table("datatable")
        msysobjects = db.table("MSysObjects")

        for record in msysobjects.records(): # Look for attribute ID (column) in the datatable
            if record.Name.startswith('ATT'):
                datatable_col_names.append(record.Name)       
        for record in datatable.records(): # Then, look the LDAP value corresponding to the attribute ID
            complete_record_name = find_complete_record_name(datatable_col_names, record.get(attributeID))
            if complete_record_name:
                output += f"{complete_record_name:<25} {record.get(lDAPDisplayName)} \n"
        return output

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Extract NTDS columns name understandable for humans.')
    parser.add_argument('-f', '--file', action="store", dest="ntds_file", required=True,
                      help='NTDS file to parse (ntds.dit)')
    parser.add_argument('-o', '--output', action="store", dest="out_file", required=False,
                      help='Output file')
    
    args = parser.parse_args()
    print("Searching datatable column name in your NTDS file...", end="")
    columns_name = extract_columns_name(args.ntds_file)
    if args.out_file:
        f = open(args.out_file, "w")
        f.write(columns_name)
        f.close()
    else:
        print(columns_name)
    print("done")
    