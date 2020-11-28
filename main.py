import time
import re
import os
import Tkinter as tk
import tkMessageBox
from win10toast import ToastNotifier
from selenium import webdriver
from bs4 import BeautifulSoup

SITE_ADDRESS = 'https://showup.tv'

driver = webdriver.Chrome()
driver.get(SITE_ADDRESS)
#Jakoś trzeba ominąć ostrzeżenie, że strona porno jest stroną porno.
driver.find_element_by_link_text("Wchodzę").click()
#Przeładowanie kodu strony, bo inaczej mamy kod tylko dla ostrzeżenia.
driver.refresh()

#Wyszukiwanie ogólnej liczby widzów i transmisji (Kobiety i mężczyźni chyba razem)
#Poprzez "in", bo z jakiegoś powodu zwykłe porównanie nie działa. Może różnice w kodowaniu stringów?
#Kek. Nie. Splitowało inaczej jak myślałem. In zostaje. A kurwa nie zostaje, bo json leci do kosza. Jebana bulwa
modelIsPresent = False
while True:
    driver.refresh()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    obrobkaLoga = soup.prettify().split(" ")
    #Tutaj do dodania jest import i obróbka .csv z wynikami. Czyli splitlines() i potem w pętelce split(";") i wsio
    #.csv ma mieć strukturę 'Nick';ilość widzów;ilość widzów;ilość widzów(...).
    #Poza pierwszą linijką, która jest kontrolona i jednocześnie przechowuje czas pobrania danych ze strony.
    #Taka transpozycja ułatwi mi obróbkę tutaj, a transpozycję do klasycznego wyglądu, żeby to wyrzygać na wykres
    #zrobi się pandą w skrypcie, które będzie generował htmla z wykresem. Docelowo modyfikowalnym w czasie rzeczywistym.
    #Ale to już powinno być w JS, a nie pajtonku
    #Otwieramy .csv z nazwamia modelek i liczbą widzów. Potem dodajemy czas, kiedy pobrano wsio
    with open('dane.csv', 'r') as fileStart:
        results = [x.split(";") for x in fileStart.read().splitlines()]
    results[0].append(str(time.time()))

    for i in range(len(obrobkaLoga)):
        if "oglądających" in obrobkaLoga[i]:
            results[2].append(str(int(obrobkaLoga[i -1])))
        if "transmisji" in obrobkaLoga[i] and obrobkaLoga[i + 1] == "i":
            results[1].append(str(int(obrobkaLoga[i -1])))

#Arkusz będzie otwierany, wymazywany, zastępowany nową wersją i zamykany. Wszystko z with.
#Żeby ten skrypt nie świnkował i nie zajmował pliku cały czas.
#Kwi.
#Iterujemy przez obiekty w htmlu, które tyczą się pojedyńczych streamów
    for i in soup.find_all("li", class_="stream"):
        for j in str(i).splitlines():
            if "href" in j:
                modelName = j[(j.index("/") + 1):-2]
            if "stream__count__number" in j:
                modelViewersNumber = int(re.findall('[0-9]+', j)[0])
#Użycie tutaj numpy.array spowodowałoby niepotrzebny burdel, więc iterujemy szybko przez już zawarte Modelki
#Jeśli jest już, to dodajemy liczbę widzów do odpowiedniej babki
#Jeśli nie ma, to dodajemy modelkę i liczbę widzów.
        for k in range(len(results)):
            if modelName in results[k][0]:
                results[k].append(str(modelViewersNumber))
                modelIsPresent = True
                break

        if modelIsPresent:
            modelIsPresent = False
            pass
        else:
            results.append([str(modelName)])
            for l in range(len(results[0])-2):
                results[-1].append("0")
            results[-1].append(str(modelViewersNumber))
#Pamiętaj programisto młody, zawsze zeruj swe metody.
#Wiem, że to zmienne, ale zmienne się nie rymujo.
        modelName = ""
        modelViewersNumber = 0

#Na wszelki wypadek wyrównywana jest ilość danych o każdej modelce.
#Jeśli jej nie ma, to dodajemy zero na jej konto na końcu.
    for subListLength in range(len(results)):
        while len(results[0]) > len(results[subListLength]):
            results[subListLength].append('0')

    toSave = [(";".join(x) + "\n") for x in results]
    print(time.asctime(time.localtime())," Wir warten")

    with open('dane.csv', 'w') as fileEnd:
        for line in toSave:
            fileEnd.write(line)
    time.sleep(60)

driver.close
'''
if os.name == 'nt':
    tost = ToastNotifier()
#Dlaczego windowsowe tosty?
#Bo JP2GMD
#Generalnie to na chuj ten tost, bo docelowo skrypt ma działać prawie w nieskończoność.
#NO ALE
    tost.show_toast("Powiadomienie", "A PO DEBUGOWANIU CHODZILIŚMY NA KREMÓWKI")
else:
    root  tk.Tk()
    root.withdraw()
    tkMessageBox.showwarning('Tej, padło')
'''
