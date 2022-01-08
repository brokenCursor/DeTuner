# DeTuner - tool for unpacking iOS backups

DeTuner is a tool designed for easy extraction of data from local iTunes backups of iOS devices (iPhone/iPad/iPod)

# Features
- Supports iOS versions starting from iOS 9
- Extraction of both encrypted and non-encrypted backups
- View information about device and backup
- Auto-formatting certain data for better readability
- Available in English and Russian

# Supports extraction of:
- Call History
- Calendar
- Camera Roll
- Contacts
- Notes
- SMS & iMessage (with attachments)
- Voice Memos
- Voicemail Messages

# Installation
## Requirements
1. Python >= 3.10
2. PyQT5
3. sqlite3
4. biplist
5. plistlib 
6. pycryptodome (optional, used for faster PBKDF2 hashing)

## Instation process
1. Clone repository
2. Install dependencies manually or
   
   ``` 
   pip install -r requirements.txt 
   ```
3. Run
   ``` 
   cd src 
   python ./DeMainUI.py 
   ```

# How To Use
1. Obtain a supported iTunes backup
2. Select it from backup screen or add from another location
3. Select required extraction options
4. Start extraction
5. If required, enter password used to create selected backup 
6. Wait for the end of the extraction process
   
## TODO
- Add settings and about menus
- Add Camera Roll album reconstruction
- Add phone number detecting formatting in Contacts
- Add combined SMS & iMessage chat support (they are separate as of right now)
- Add automatic installation
- Add and test Linux support (currently not tested, use on your own risk!)
  
## Credits
Device icons from [ipsw.me](https://ipsw.me)

Basic backup decryption implementation from [jsharkey13/iphone_backup_decrypt](https://github.com/jsharkey13/iphone_backup_decrypt)