import re, os, requests, urllib

def download(uri, destfilename):
    if not os.path.exists(destfilename):
        print ("Downloading from {} to {}...".format(uri, destfilename))
        
        try:
            r = requests.get(uri, stream=True)
            
            with open(destfilename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        
        except:
            print ("Error downloading file.")
            return False