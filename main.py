import time
import re
import os
import logging
import mysql.connector
from selenium import webdriver
from bs4 import BeautifulSoup

SITE_ADDRESS = 'https://showup.tv'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
'''
mydb = mysql.connector.connect(
        host='sql7.freesqldatabase.com',
        user='sql7385402',
        password='fLGXMRLKyp')
'''

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
                #Ale to już powinno być w JS, a nie pajtonku. HA, TAKI CHUJ. I TAK JEST W PYTHONIE
                #Otwieramy .csv z nazwamia modelek i liczbą widzów. Potem dodajemy czas, kiedy pobrano wsio
                #Docelowo przepiszę kod na korzystanie z jakieś .db
                with open('dane.csv', 'r') as fileStart:
                    results = [x.split(";") for x in fileStart.read().splitlines()]
                results[0].append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

                #Wyciągamy liczbę widzów
                viewersNumber = re.findall("i ([0-9]+[ ])\w+", driver.page_source)[0][:-1]
                #Wyciągamy liczbę transmisji
                transmissionsNumber = re.findall("<h4>([0-9]+[ ])\w+", driver.page_source)[0][:-1]
                #Wyciągamy listę z nickami modelek
                modelNameList = re.findall('<a href="/([^"]*)', driver.page_source)[8:-5]
                #Wyciągamy listę z liczbami widzów poszczególnych modelek. Są indeksowane 1:1 z listą wyżej.
                modelViewersList = re.findall('">([0-9]+)', driver.page_source)

                results[1].append(str(transmissionsNumber))
                results[2].append(str(viewersNumber))
                results[3].append(str(round(int(viewersNumber)/int(transmissionsNumber))))


            #Arkusz będzie otwierany, wymazywany, zastępowany nową wersją i zamykany. Wszystko z with.
            #Żeby ten skrypt nie świnkował i nie zajmował pliku cały czas.
            #Kwi.
            #Iterujemy przez obiekty w htmlu, które tyczą się pojedyńczych streamów
            #A gówno. Wyszukujemy wszystko regexem. Śmierć burżuazyjnej iteracji.
            #Regexujemy listę nicków i liczbę widzów. Z racji tego, że indeksy obu odpowiadają sobie, to nie ma żadnego problemu.

            #Jeśli jest już, to dodajemy liczbę widzów do odpowiedniej babki
            #Jeśli nie ma, to dodajemy modelkę i liczbę widzów.
                knownModelsList = [results[x][0] for x in range(len(results))]
                for modelName in modelNameList:
                    if modelName in knownModelsList:
                        #logger.info(f"{time.asctime(time.localtime())} {modelName} has {modelViewersList[modelNameList.index(modelName)]} viewers")
                        results[knownModelsList.index(modelName)].append(modelViewersList[modelNameList.index(modelName)])
                    else:
                        logger.info(f"{time.asctime(time.localtime())} Adding {modelName} to the database")
                        toAdd = []
                        toAdd.append(modelName)
                        [toAdd.append('0') for x in range((len(results[0]) - 2))]
                        toAdd.append(modelViewersList[modelNameList.index(modelName)])
                        results.insert(-1, (toAdd))
            #Na wszelki wypadek wyrównywana jest ilość danych o każdej modelce.
            #Znaczy, to nawet nie jest na wszelki wypadek. Inaczej dane są chuja warte, chyba, że wrzucałbym je jako słownik data:widzowie
            #Ale to by jebało mi potem import do dataframe pewnie. Nie je
            #Jeśli jej nie ma, to dodajemy zero na jej konto na końcu.
                for subListLength in range(len(results)):
                    while len(results[0]) > len(results[subListLength]):
                        results[subListLength].append('0')
#Sklejanie arrayów do zrzucenia do pliku. I kasowanie ostatniego \n, bo potem .csv interpretuje to jako pustą linię i inne rzeczy się jebiom.

                modelNameSet = [results[x][0] for x in range(len(results))][3:]
                for modelNumber in range(len(modelNameSet)):
                    if len(results[modelNumber]) != len(results[0]):
                        #kontrola czy dany subarray ma odpowiednią długość po powyższym. Jeśli nie, to pozbywamy się najnowszego zera.
                        #Powinno pomóc na z dupy za długiego ostatniego subarraya.
                        print(len(results[modelNumber]), len(results[0]))
                        if len(results[modelNumber]) == 0:
                            results[modelNumber].pop()
                            logging.info("Found empty subarray")
                        elif len(results[modelNumber]) > len(results[0]):
                            tmpModelArrayReersed = results[modelNumber]
                            tmpModelArrayReersed.reverse()
                            results[modelNumber].pop(tmpModelArrayReersed.index('0')-len(results[modelNumber])+1)
                            logger.info(f"Array of {results[modelNumber][0]} has been found too long.")
                        else:
                            logger.info("Something unexpected happenend. Moving on.")
                    else:
                        pass

                #Sklejamy arraya 2d do str do zapisu.
                toSave = [(";".join(x) + "\n") for x in results][:-2]

                localTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                logger.info(f"{localTime} Waiting for the next cycle")

                with open('dane.csv', 'w') as fileEnd:
                    for line in toSave:
                        fileEnd.write(line)
                time.sleep(60*10)

            driver.close()
        except KeyboardInterrupt:
            logger.info("Continue Y/N")
            answer = input("> ")
            if answer == "Y":
                pass
            else:
                quit()
            driver.close()
            break
        except BaseException as error:
            logger.info(f" {error} has been encountered. Trying to restart")
        except:
            driver.close()
            localTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            logger.info(f"{localTime} There was an error. Attempting to start anew")
            continue
