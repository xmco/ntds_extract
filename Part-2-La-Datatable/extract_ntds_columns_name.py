from dissect.esedb import EseDB
import binascii
import argparse
import re

'''
    Utility method to find a schema object in the datatable
    to get its DNT. The idea is to help finding objects having
    this DNT as objectCategory.
'''


def get_schema_object(ese_db, schemaGuid):
    slices = [
        slice(0, 8), slice(9, 13), slice(14, 18), slice(19, 23),
        slice(24, 36)
    ]
    sguid = binascii.unhexlify(schemaGuid[slices[0]])[::-1].hex()
    sguid += binascii.unhexlify(schemaGuid[slices[1]])[::-1].hex()
    sguid += binascii.unhexlify(schemaGuid[slices[2]])[::-1].hex()
    sguid += schemaGuid[slices[3]] + schemaGuid[slices[4]]

    datatable = ese_db.table("datatable")
    for row in datatable.records():
        if (
            # schemaIDGUID attribute
            (guid := row.get("ATTk589972")) and
            guid.hex() == sguid
        ):
            return row.get("DNT_col"), row
    return None, None


'''
    Recherche du nom de la colonne à partir de l'ID de l'attribut (Ex: 589983 => ATTq589983)
'''


def extract_columns_name(file_path):
    fd = open(file_path, "rb")
    db = EseDB(fd)
    # Get the ID of the object representing attribute objects
    #  by its schemaIDGUID (Attribute-Schema class)
    attribute_dnt, _ = get_schema_object(db, "bf967a80-0de6-11d0-a285-00aa003049e2")
    reg = re.compile(r'\d+')

    def find_complete_record_name(complete_record_names, partial_record_name):
        for record_name in complete_record_names:
            if str(partial_record_name) == ''.join(reg.findall(record_name)) :
                return record_name

    datatable_col_names = []
    output = ''
    attributeID = 'ATTc131102'
    lDAPDisplayName = 'ATTm131532'
    objectCategory = 'ATTb590606'
    datatable = db.table("datatable")
    msysobjects = db.table("MSysObjects")

    for record in msysobjects.records():  # Look for attribute ID (column) in the datatable
        if record.Name.startswith('ATT'):
            datatable_col_names.append(record.Name)
    for record in filter(
        lambda row: row.get(objectCategory) == attribute_dnt,
        datatable.records()
    ):  # Then, look the LDAP value corresponding to the attribute ID
        complete_record_name = find_complete_record_name(datatable_col_names, record.get(attributeID))
        if complete_record_name:
            output += f"{complete_record_name:<25} {record.get(lDAPDisplayName)} \n"
    fd.close()
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
