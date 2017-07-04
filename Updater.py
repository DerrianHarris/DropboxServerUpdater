import Config
import os
import zipfile
import dropbox
import tqdm

modpack_path = Config.modpack_path
filename = Config.filename
loding_bar_units = Config.default_unit
mbs_rate = Config.upload_rate


def dropbox_login():
    d = dropbox.Dropbox(Config.access_token)
    return d


def zip(src, dst, zipname):
    zipname = zipname + ".zip"
    zf = zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print('zipping %s as %s' %
                  (os.path.join(dirname, filename), arcname))
            zf.write(absname, arcname)
    zf.close()
    return zipname


def kb_mb_gb_conversion(size, kb_mb_gb="mb"):
    if(kb_mb_gb == "kb"):
        return size / 1024
    elif(kb_mb_gb == "mb"):
        return size / 1024 / 1024
    elif(kb_mb_gb == "gb"):
        return size / 1024 / 1024 / 1024
    else:
        print("Cannot use size: " + kb_mb_gb + "\nUsing kb as default")
        return size

print("Changing directory to: " + modpack_path +
      "\nZipping the file: " + filename)
os.chdir(modpack_path)

if (os.path.exists(modpack_path + filename) != True):
    print(filename + " does not exist! Check the spelling....")
    quit()

zipname = zip(modpack_path + filename, modpack_path, filename)
zippath = modpack_path + zipname
print(zipname + " has been created at loaction: " + modpack_path)

print("Logging into dropbox.....")
d = dropbox_login()
print("Dropbox logged in....")

dest_path = "/" + zipname
print("Searching dropbox for the file: " + zipname)
found = False
for file in d.files_list_folder('').entries:
    if(file.name.lower() == zipname.lower()):
        print("File found...")
        print("Deleting older file…")
        d.files_delete(dest_path)
        print("Older file deleted")
        found = True

if(found == False):
    print("No file with the name \"" + zipname + "\" found in dropbox....")

print("Attempting to upload the new files...")
# open the file and upload it


with open(zippath, "rb") as f:
    file_size = os.path.getsize(zippath)
    CHUNK_SIZE = mbs_rate * 1024 * 1024
    overwrite = dropbox.files.WriteMode('overwrite', None)
    if file_size <= CHUNK_SIZE:
        d.files_upload(f.read(), dest_path, overwrite)
    else:

        # print(overwrite.is_overwrite())
        upload_session_start_result = d.files_upload_session_start(
            f.read(CHUNK_SIZE))
        cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                   offset=f.tell())
        commit = dropbox.files.CommitInfo(path=dest_path)
        with tqdm.tqdm(total=kb_mb_gb_conversion(file_size, loding_bar_units)) as pbar:
            while f.tell() < file_size:
                if ((file_size - f.tell()) <= CHUNK_SIZE):
                    d.files_upload_session_finish(f.read(CHUNK_SIZE),
                                                  cursor,
                                                  commit)
                else:
                    d.files_upload_session_append(f.read(CHUNK_SIZE),
                                                  cursor.session_id,
                                                  cursor.offset)
                    cursor.offset = f.tell()
                pbar.update(kb_mb_gb_conversion(CHUNK_SIZE, loding_bar_units))
print("Files uploaded....")
link = d.sharing_create_shared_link(dest_path).url.replace("?dl=0", "?dl=1")
print("Here is the link: " + "\n" + link)
input("Press Enter to continue...")
