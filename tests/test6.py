import requests
url = 'https://www.mirea.ru/upload/medialibrary/5fb/it-1k.-16_17-osen.xls'
r = requests.head(url)
print(r.headers['Last-Modified'])