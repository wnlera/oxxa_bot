import re



'I н. Проц. програм. пр асс.Алпатов А.Н.\nII н. Проц. програм.  пр #ИВЦ-8\nГ-226#'



r = re.compile(r"\d+\-\d+")
searchResult = re.match(r, "4-15 н. ПРОГРАММИРОВАНИЕ")
if searchResult != None:
    rng = [int(x) for x in searchResult.group(0).split('-')]
    print([x for x in range(rng[0], rng[1]+1)])
