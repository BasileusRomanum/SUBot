import time
import re
import os
import logging
import json
from selenium import webdriver

SITE_ADDRESS = 'https://showup.tv'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

while True:
        try:
            driver = webdriver.Chrome()
            driver.get(SITE_ADDRESS)
            #Jakoś trzeba ominąć ostrzeżenie, że strona porno jest stroną porno.
            driver.find_element_by_link_text("Wchodzę").click()
            #Przeładowanie kodu strony, bo inaczej mamy kod tylko dla ostrzeżenia.
            #driver.refresh()

            #Wyszukiwanie ogólnej liczby widzów i transmisji (Kobiety i mężczyźni chyba razem)
            #Poprzez "in", bo z jakiegoś powodu zwykłe porównanie nie działa. Może różnice w kodowaniu stringów?
            #Kek. Nie. Splitowało inaczej jak myślałem. In zostaje. A kurwa nie zostaje, bo json leci do kosza. Jebana bulwa

            while True:
                driver.get(SITE_ADDRESS)
                driver.refresh()
                #Docelowo przepiszę kod na korzystanie z jakieś .db
                #Kod przepisany na jsona w ramach przewidywanej integracji z MongoDB

                with open('dane.json', 'r') as fileStart:
                    fileStart.seek(0)
                    results = json.load(fileStart)

                zeit = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                #Wyciągamy liczbę widzów
                viewersNumber = re.findall("i ([0-9]+[ ])\w+", driver.page_source)[0][:-1]
                #Wyciągamy liczbę transmisji
                transmissionsNumber = re.findall("<h4>([0-9]+[ ])\w+", driver.page_source)[0][:-1]
                #Wyciągamy listę z nickami modelek
                modelNameList = re.findall('<a href="/([^"]*)', driver.page_source)[8:-5]
                #Wyciągamy listę z liczbami widzów poszczególnych modelek. Są indeksowane 1:1 z listą wyżej.
                modelViewersList = re.findall('">([0-9]+)', driver.page_source)

                results['Transmisji'][zeit] = int(transmissionsNumber)
                results['Ogladajacych'][zeit] = int(viewersNumber)
                results['averageViewersNumber'][zeit] = round(int(viewersNumber)/int(transmissionsNumber))
            #Regexujemy listę nicków i liczbę widzów. Z racji tego, że indeksy obu odpowiadają sobie, to nie ma żadnego problemu.

            #Jeśli jest już, to dodajemy liczbę widzów do odpowiedniej babki
            #Jeśli nie ma, to dodajemy modelkę i liczbę widzów.
                for modelName in modelNameList:
                    try:
                        results[modelName][zeit] = modelViewersList[modelNameList.index(modelName)]
                    except KeyError:
                        logger.info(f"{time.asctime(time.localtime())} Adding {modelName} to the database")
                        results[modelName] = {zeit : int(modelViewersList[modelNameList.index(modelName)])}

                localTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                logger.info(f"{localTime} Waiting for the next cycle")

                with open('dane.json', 'w') as fileEnd:
                    json.dump(results, fileEnd)
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
