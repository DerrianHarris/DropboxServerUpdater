import zipfile

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