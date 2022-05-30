from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
class GDrive:
    def __init__(self):
        self.__gauth = GoogleAuth()
        self.__gauth.LocalWebserverAuth()
        self.__files = []

    def get_gauth(self):
        return self.__gauth

    def add_file(self, id):
        self.__files.append(id)

    def delete_file(self):
        for id in self.__files:
            drive = GoogleDrive(self.__gauth)
            file1 = drive.CreateFile({'id': id})
            file1.Trash()  # Move file to trash.
            file1.UnTrash()  # Move file out of trash.
            file1.Delete()  # Permanently delete the file.

    def upload(self, filename, download = 1):
        drive = GoogleDrive(self.__gauth)
        file1 = drive.CreateFile({'title': filename})
        file1.SetContentFile(os.path.join(r'C:\Users\1\PycharmProjects\InvestmentBot', filename))
        file1.Upload()
        if download == 1: self.add_file(file1['id'])
        permission = file1.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'})

        url = file1['alternateLink']  # Display the sharable link.
        return url