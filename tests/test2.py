import requests
import json
from urllib.request import urlretrieve

def jDump(file, j):
    with open(file, mode='w', encoding='utf-8') as f:
        json.dump(j, f, indent=1, sort_keys=True, ensure_ascii=False)  

def getFileLength(url):
    r = requests.head(url)
    return r.headers['Content-Length']





def downloadShed(url):
    try:
        st_shed = json_data['st_shed']
    except:
        print("[DownloadShed] error in st_shed")
        st_shed = 0;
    
    urlretrieve(url, "data\\shedules\\xls\\%s.xls"%st_shed)
    print("[DownloadShed] Shedule downloaded!")

def checkNewShed():
    print("====================")
    try:
        st_shed = get_st_shed()
    except:
        st_shed = 0;
    
    if st_shed > 0:
        str_var = "_%s_"%(st_shed+1)
    else:
        print("[GetNewShed] st_shed == 0")
        st_shed = 0;
        str_var = "_%s_"%(st_shed+1)
        
    s = "https://www.mirea.ru/upload/medialibrary/14c/it-1k.-16_17-osen%s.xls"%str_var
    print("Url: %s"%s)
    try:
        l = getFileLength(s)
        print("New shedule detected")
        print("New filesize: %s"%l)
        
        st_shed += 1;
        set_st_shed(st_shed);      
        print("New st_shed: %s"%(st_shed))

        downloadShed(s);
        print("%s.xls"%st_shed)
        
        parseFileToJson("%s"%st_shed)
        print("====================")
        return (True, url)
    except:
        print("Using old shedule")
        print("====================")
        return (False, False)

print(checkNewShed())