def getShedUrl():
    try:
        url = 'https://www.mirea.ru/education/schedule-main/schedule/#tabs'
        page = urlopen(url)
        soup = BeautifulSoup(page.read(), "lxml")  # , from_encoding="utf-8")

        root = soup.find(True, attrs={"id": 'tab-content'})
        children = root.find_all(True, class_="uk-active", attrs={"aria-hidden": False})[0]

        paras = children.find_all(True, class_="uk-accordion-content")
        insts = children.find_all(True, class_="uk-accordion-title")
        # print(insts[2])
        xls = paras[2].find_all(True, class_="xls")[0].attrs['href']
        return xls
    except:
        print("MEOW")