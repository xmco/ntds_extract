import argparse
from dissect.esedb import EseDB
import csv
from datetime import datetime

LAPS_REF = {
    'LAPS_ADMPWD_REF': 'ms-Mcs-AdmPwd', # LAPS password
    'LAPS_ADMPWDEXP_REF': 'ms-Mcs-AdmPwdExpirationTime' # LAPS password expiration time
}

def search_laps_attr(ntds_path):
    laps_attr = {}
    ldap_display_name_attr = "ATTm131532" #lDAPDisplayName
    msds_int_id = "ATTj591540" #msDS-IntId
    laps_admpwd_id = None
    laps_admpwdexpirationtime_id = None
    print("Search for LAPS (legacy) installation", end="...", flush=True)
    with open(ntds_path, "rb") as fh:
        db = EseDB(fh)
        datatable = db.table("datatable")
        for record in datatable.records():        
            # search LAPS
            if record.get(ldap_display_name_attr) is not None: 
                if LAPS_REF['LAPS_ADMPWD_REF'] in record.get(ldap_display_name_attr):
                    laps_admpwd_id = record.get(msds_int_id)
                if LAPS_REF['LAPS_ADMPWDEXP_REF'] in record.get(ldap_display_name_attr):
                    laps_admpwdexpirationtime_id = record.get(msds_int_id)
        print("done")
        if laps_admpwd_id:
            print('LAPS install (legacy) detected!')
            laps_attr['laps_admpwd'] = 'ATTf'+ str(laps_admpwd_id)
            laps_attr['laps_admpwdexpirationtime'] = 'ATTq'+ str(laps_admpwdexpirationtime_id)
        return laps_attr

def extract_field(file_path, laps_admpwd, laps_admpwdexpirationtime):
    output = []
    print("Extracting LAPS (legacy) values from your NTDS file", end="...", flush=True)
    with open(file_path, "rb") as fh:
        db = EseDB(fh)
        datatable = db.table("datatable")
        line_number = 1
        for record in datatable.records():
            line = []
            if record.get(laps_admpwd):
                line.append(record.get("ATTm590045")) #sAMAccountName
                line.append(record.get(laps_admpwd).decode("utf-8"))
                line.append(fileTimeToDateTime(record.get(laps_admpwdexpirationtime)))
            if len(line) > 0:
                output.append(line) 
        print("done")   
        return output

def fileTimeToDateTime(t):
    if t == None:
        return ""
    t -= 116444736000000000
    t //= 10000000

    # Bug - setting access time beyond Jan. 2038 
    # https://bugs.python.org/issue13471
    if t == 910692730085:
        return ""
    if t < 0:
        return ""
    else:
        try:
            dt = datetime.fromtimestamp(t)
        except:
            print("****** BUG ****** : %d" % t)
            return t
        return dt.strftime("%Y-%m-%d %H:%M")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract NTDS LAPS (legacy) passwords.')
    parser.add_argument('-f', '--file', action="store", dest="ntds_file", required=True,
                      help='NTDS file to parse (ntds.dit)')
    parser.add_argument('-o', '--output', action="store", dest="out_file", required=True,
                      help='CSV output file')
    
    args = parser.parse_args()
    
    laps_attributes = search_laps_attr(args.ntds_file)
    if laps_attributes == {}:
        print("Error : No LAPS (legacy) install found")
        exit(1)
    
    fields = extract_field(args.ntds_file, laps_attributes['laps_admpwd'], laps_attributes['laps_admpwdexpirationtime'])

    headers = ["sAMAccountName",LAPS_REF['LAPS_ADMPWD_REF'], LAPS_REF['LAPS_ADMPWDEXP_REF']]
    
    # write output to a CSV file
    print(f"Writing data in {args.out_file}", end="...", flush=True)
    with open(args.out_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers) 
        writer.writerows(fields) # write data
    print("done")