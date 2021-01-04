import time
import re
import os
import logging
from selenium import webdriver
from bs4 import BeautifulSoup

SITE_ADDRESS = 'https://showup.tv'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


while True:
        try:
            driver = webdriver.Chrome()
            driver.get(SITE_ADDRESS)
            #Jakoś trzeba ominąć ostrzeżenie, że strona porno jest stroną porno.
            driver.find_element_by_link_text("Wchodzę").click()
            #time.sleep(5)
            #driver.find_element_by_link_text("Zamknij").click()
            #Przeładowanie kodu strony, bo inaczej mamy kod tylko dla ostrzeżenia.
            driver.refresh()

            #Wyszukiwanie ogólnej liczby widzów i transmisji (Kobiety i mężczyźni chyba razem)
            #Poprzez "in", bo z jakiegoś powodu zwykłe porównanie nie działa. Może różnice w kodowaniu stringów?
            #Kek. Nie. Splitowało inaczej jak myślałem. In zostaje. A kurwa nie zostaje, bo json leci do kosza. Jebana bulwa
            modelIsPresent = False
            while True:
                driver.get(SITE_ADDRESS)
                driver.refresh()
                #Tutaj do dodania jest import i obróbka .csv z wynikami. Czyli splitlines() i potem w pętelce split(";") i wsio
                #.csv ma mieć strukturę 'Nick';ilość widzów;ilość widzów;ilość widzów(...).
                #Poza pierwszą linijką, która jest kontrolona i jednocześnie przechowuje czas pobrania danych ze strony.
                #Taka transpozycja ułatwi mi obróbkę tutaj, a transpozycję do klasycznego wyglądu, żeby to wyrzygać na wykres
                #zrobi się pandą w skrypcie, które będzie generował htmla z wykresem. Docelowo modyfikowalnym w czasie rzeczywistym.
                #Kek. Generalnie to powinienem to wrzucać od razu do bazy danych. Ale jestem leniwy. I nie wiem za bardzo jeszcze jak to zrobić.
                #Musiałbym pogrzebać w metodach dataframe.
                #Ale to już powinno być w JS, a nie pajtonku. HA, TAKI CHUJ. I TAK JEST W PYTHONIE
                #Otwieramy .csv z nazwamia modelek i liczbą widzów. Potem dodajemy czas, kiedy pobrano wsio
                with open('dane.csv', 'r') as fileStart:
                    results = [x.split(";") for x in fileStart.read().splitlines()]
                results[0].append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

                
                viewersNumber = re.findall("i ([0-9]+[ ])\w+", driver.page_source)[0][:-1]
                transmissionsNumber = re.findall("<h4>([0-9]+[ ])\w+", driver.page_source)[0][:-1]

                results[3].append(str(round(int(viewersNumber)/int(transmissionsNumber))))


            #Arkusz będzie otwierany, wymazywany, zastępowany nową wersją i zamykany. Wszystko z with.
            #Żeby ten skrypt nie świnkował i nie zajmował pliku cały czas.
            #Kwi.
            #Iterujemy przez obiekty w htmlu, które tyczą się pojedyńczych streamów
            #A gówno. Wyszukujemy wszystko regexem. Śmierć burżuazyjnej iteracji.
            #Regexujemy listę nicków i liczbę widzów. Z racji tego, że indeksy obu odpowiadają sobie, to nie ma żadnego problemu.
                modelNameList = re.findall('<a href="/([^"]*)', driver.page_source)[8:-5]
                modelViewersList = re.findall('">([0-9]+)', driver.page_source)
            #Jeśli jest już, to dodajemy liczbę widzów do odpowiedniej babki
            #Jeśli nie ma, to dodajemy modelkę i liczbę widzów.
                knownModelsList = [results[x][0] for x in range(len(results))]
                for modelName in modelNameList:
                    if modelName in knownModelsList:
                        logger.info(f"{time.asctime(time.localtime())} {modelName} has {modelViewersList[modelNameList.index(modelName)]} viewers")
                        results[knownModelsList.index(modelName)].append(modelViewersList[modelNameList.index(modelName)])
                    else:
                        logger.info(f"{time.asctime(time.localtime())} Adding {modelName} to the database")
                        toAdd = []
                        toAdd.append(modelName + '0'*(len(results[0]) - 2) + modelViewersList[modelNameList.index(modelName)])
                        results.insert(-1, (toAdd))
            #Pamiętaj programisto młody, zawsze zeruj swe metody.
            #Wiem, że to zmienne, ale zmienne się nie rymujo.
                    #modelName = ""
                    #modelViewersNumber = 0
                #Zbędne już
            #Na wszelki wypadek wyrównywana jest ilość danych o każdej modelce.
            #Znaczy, to nawet nie jest na wszelki wypadek. Inaczej dane są chuja warte, chyba, że wrzucałbym je jako słownik data:widzowie
            #Ale to by jebało mi potem import do dataframe pewnie. Nie je
            #Jeśli jej nie ma, to dodajemy zero na jej konto na końcu.
                for subListLength in range(len(results)):
                    while len(results[0]) > len(results[subListLength]):
                        results[subListLength].append('0')

                toSave = [(";".join(x) + "\n") for x in results]
                localTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                logger.info(f"{localTime} Waiting for the next cycle")

                with open('dane.csv', 'w') as fileEnd:
                    for line in toSave:
                        fileEnd.write(line)
                time.sleep(60*10)

            driver.close()
        except KeyboardInterrupt:
            driver.close()
            break
        except:
            driver.close()
            localTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            logger.info(f"{localTime} There was an error. Attempting to start anew")
            continue
