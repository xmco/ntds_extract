# <p align="center">NTDS Columns Name Extractor</p>
  
A simple script to extract the columns name and the corresponding LDAP display name of a NTDS datatable table.  

## 🛠️ Installation    
```python
pip install -r requirements.txt
```

## 🧑🏻‍💻 Usage
```python
python extract_ntds_columns_name.py -f "path/to/ntds.dit"
```

## 📝 Output
| Column name | LDAPDisplayName | 
| -------- | -------- | 
| ATTm590045    | sAMAccountName    |
| ATTm13    | description    |
| ATTq589920    | pwdLastSet    |
| ATTj589993    | logonCount    |
| ATTl131074    | whenCreated    |
| ATTq589876    | lastLogon    |
| ...    | ...    |

## 🛠️ Tech Stack
- [Dissect](https://github.com/fox-it/dissect.esedb)

    