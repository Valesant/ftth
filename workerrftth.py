# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 17:43:28 2019

@author: avales
"""

# https://sites.google.com/a/chromium.org/chromedriver/downloads
# webdriver v75.0.3770.140
# chrome    v75.0.3770.142

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import time
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from fonctionsRPA import closingBrowser, check_exists_by_class_name, check_exists_by_css_selector, check_exists_by_link_text


class WorkerResolutionFTTH(QObject):
    finished = pyqtSignal()
    SendFTTH = pyqtSignal(str)

    def __init__(self, IDs):
        super(WorkerResolutionFTTH, self).__init__()
        self.ND = ''
        self.identifiants = IDs
        self.pagesweb = {}
        self.liensMonSI = {}

    @pyqtSlot()
    def main(self):
        t = time.time()
        browser = webdriver.Chrome()

        Listecas = self.ScanBAL(browser)
        print(Listecas)

        while Listecas == False or  Listecas == []:
            self.SendFTTH.emit("Aucun cas dans la BAL d'arrivée")
            self.pagesweb["Oceane Liste Ticket"] = browser.current_window_handle
            #browser.refresh()
            #browser.switch_to.frame("PopupOCEANE")
            #on clique sur les tickets en arrivée
            listeOnglets = browser.find_element_by_css_selector("#horizontalnavbarUL").find_elements_by_tag_name('li')
            for onglet in listeOnglets :
                if "Tickets en arrivée" in onglet.text : 
                    onglet.click()
                    break
            #Liste de tous les cas présent en BAL, reférencés FTTH
            if browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:][0].find_elements_by_tag_name("td")[0].text != 'Aucun résultat':
                Listecas = [cas.find_elements_by_tag_name("td")[5].text for cas in browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:] if 'FTTH' in cas.find_elements_by_tag_name("td")[6].text and cas.find_elements_by_tag_name("td")[8].text == '']
                print(Listecas)

        while 1:
            for cas in Listecas:
                phrase = '\n' + cas + ' FTTH :'
                self.SendFTTH.emit(phrase)
                self.ND = cas
                #Acquittement
                #Si le cas est présent en BAL
                if self.Aquitter(browser):
                    #Traitement
                    typeRendu, numeroTi, createur = self.OrchestraFTTH(browser)
                    print("type de problème :", typeRendu)
                    print(numeroTi)
                    print(createur)

                    #si il y a eu une erreur on finit le ticket
                    if not (typeRendu == False or typeRendu == "ERREUR"):
                        self.RenduTicketOceane(browser, typeRendu, numeroTi, createur)
                    else:
                        self.SendFTTH.emit('Cas non pris en compte, merci de vérifier')

                #Fin du programme
                print(time.time() - t)

                #on supprime les tabs ouverts inutiles
                browser.switch_to.window(self.pagesweb["Mon SI"])
                
                print("\nself.pages web : \n\n") 
                print(self.pagesweb)
                print("\nwindow_handles : \n\n")
                print(browser.window_handles)
                
                listePagesSuprimees = []
                #On supprime de la liste des pages web enregistrées
                for nom, addresse in self.pagesweb.items():
                    print(nom, addresse)
                    if nom != "Mon SI" and nom != "Oceane Acceuil" and nom != "Oceane Liste Ticket" and nom != "Orchestra":
                        print('pages supprimées : ', nom)
                        listePagesSuprimees.append(nom)
                        try : 
                            browser.switch_to.window(self.pagesweb[nom])
                            browser.close()
                        except : 
                            pass
                
                for nom in listePagesSuprimees:
                    del self.pagesweb[nom]
                
                #On supprime du window_handles
                for page in browser.window_handles : 
                    print(page)
                    if not(page in self.pagesweb.values()):
                            browser.switch_to.window(page)
                            try :
                                print('try to close...')
                                browser.close()
                            except : 
                                print('fail to close')
                                pass
                print("\nself.pages web : \n\n")
                print(self.pagesweb)
                print("\nwindow_handles : \n\n")
                print(browser.window_handles)

                browser.switch_to.window(self.pagesweb["Oceane Liste Ticket"])
                #rowser.refresh()
                browser.switch_to.frame("PopupOCEANE")
                #on clique sur les tickets en arrivée
                listeOnglets = browser.find_element_by_css_selector("#horizontalnavbarUL").find_elements_by_tag_name('li')
                for onglet in listeOnglets :
                    if "Tickets en arrivée" in onglet.text :
                        onglet.click()
                        break
       
                #Liste de tous les cas présent en BAL, reférencés FTTH
                if browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:][0].find_elements_by_tag_name("td")[0].text != 'Aucun résultat':
                    Listecas = [cas.find_elements_by_tag_name("td")[5].text for cas in browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:] if 'FTTH' in cas.find_elements_by_tag_name("td")[6].text and cas.find_elements_by_tag_name("td")[8].text == '']
                    print(Listecas)


        browser.quit()
        self.SendFTTH.emit('KILL')
        self.finished.emit()


    def MonSi(self, browser):
        browser.get("https://msi.sso.francetelecom.fr/monsi/index.html#si")
        # ID
        ID = self.identifiants[0]
        # PWD
        PWD = self.identifiants[1]
        browser.find_element_by_name("USER").send_keys(ID)
        browser.find_element_by_name("PASSWORD").send_keys(PWD)
        browser.find_element_by_id("linkValidForm").click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        
        listeOutils = browser.find_element_by_css_selector("body > div > div > div > main > div > div > div.view__body.page-applications.ng-scope > section > div > table > tbody").find_elements_by_tag_name('tr')
        for outil in listeOutils :
            if "ORCHESTRA" in (outil.text) : self.liensMonSI["ORCHESTRA"] = outil.find_elements_by_tag_name('td')[1]
            elif "ADELIA" in (outil.text) : self.liensMonSI["ADELIA"] = outil.find_elements_by_tag_name('td')[1]
            elif "OCEANE" in (outil.text) : self.liensMonSI["OCEANE"] = outil.find_elements_by_tag_name('td')[1]
            elif "BRASIL" in (outil.text) : self.liensMonSI["BRASIL"] = outil.find_elements_by_tag_name('td')[1]
           
        
        self.pagesweb["Mon SI"] = browser.current_window_handle

    def ScanBAL(self, browser):
        self.MonSi(browser)

        #Ouvrerture d'Oceane
        self.liensMonSI["OCEANE"].click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        self.pagesweb["Oceane Acceuil"] = browser.window_handles[-1]
        browser.switch_to.window(self.pagesweb["Oceane Acceuil"])
        browser.switch_to.frame("OCEANE")

        # on clique sur l'onglet liste ticket
        browser.find_element_by_css_selector("#menu_lbtn_I3_L1").click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)

        browser.switch_to.window(browser.window_handles[-1])
        browser.switch_to.frame("PopupOCEANE")
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)

        # si on est pas dans la BAL DWBSCA
        if (browser.find_element_by_css_selector("#banner-Alarm > div > div.footer > div.topbar > p > span.bold").text[:6] != "DWBSCA"):
            browser.switch_to.frame("PopupOCEANE")
            # On clique sur "..."
            browser.find_element_by_css_selector("#userGroup > span").click()
            browser.switch_to.frame("framegroupofgroupsetpopover")
            # on selectionne DWBSCA
            browser.find_element_by_css_selector("#orangeBal1 > img").click()
            # On revient sur la liste des tickets
            #à modifier
            browser.switch_to.window(browser.window_handles[2])
            browser.switch_to.frame("PopupOCEANE")

        #on clique sur les tickets en arrivée
        listeOnglets = browser.find_element_by_css_selector("#horizontalnavbarUL").find_elements_by_tag_name('li')
        for onglet in listeOnglets :
            if "Tickets en arrivée" in onglet.text : 
                onglet.click()
                break                                                    
            
        #on enregistre la page web dans le dictionnaire
        self.pagesweb["Oceane Liste Ticket"]=browser.current_window_handle

        #Liste de tous les cas FTTH présent en BAL
        Listecas=[]
        if browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:][0].find_elements_by_tag_name("td")[0].text != 'Aucun résultat':
                Listecas = [cas.find_elements_by_tag_name("td")[5].text for cas in browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:] if 'FTTH' in cas.find_elements_by_tag_name("td")[6].text and cas.find_elements_by_tag_name("td")[8].text == '']

        #si il n'y a pas de cas
        if Listecas == []:
            self.SendFTTH.emit("Aucun cas FTTH dans la BAL d'arrivée")
            return False
        else :
            return Listecas

    def Aquitter(self, browser):
        ListeTousCas = browser.find_element_by_css_selector("#dtTicketList").find_elements_by_tag_name("tr")[2:]
        print('cas qui va être traité : ', self.ND)
        try :
            cas =  [ i for i in ListeTousCas if i.find_elements_by_tag_name("td")[5].text == self.ND]
        except : 
            self.SendFTTH.emit("Aucun cas FTTH dans la BAL d'arrivée")
            return False
        
        try :
            #on acquitte notre cas
            cas[0].find_elements_by_tag_name("td")[2].find_element_by_tag_name("a").click()
            time.sleep(1)
            self.pagesweb["Oceane Ticket"]=browser.window_handles[-1]
            browser.switch_to.window(self.pagesweb["Oceane Ticket"])
            #print(self.pagesweb)
            return True
        except:
            #le ticket a été acquitté entre temps
            self.SendFTTH.emit("le ticket a été acquitté par un autre opérateur")
            return False
    def OrchestraFTTH(self, browser):
        print('Accès  Orchestra')
        browser.switch_to.window(self.pagesweb["Mon SI"])
        self.liensMonSI["ORCHESTRA"].click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        self.pagesweb["Orchestra"]=browser.window_handles[-1]
        browser.switch_to.window(self.pagesweb["Orchestra"])
        browser.find_element_by_css_selector("#clientNd").send_keys(self.ND)
        browser.find_element_by_css_selector("#loadParametersButton").click()

        browser.implicitly_wait(10)  # seconds
        time.sleep(3)

        #si Pas de DERCO
        if (browser.find_element_by_css_selector("#dercoLabel").text == "Aucun incident ou TP en cours ou récemment clôturé." or browser.find_element_by_css_selector("#dercoLabel").text == "Un incident ou TP a été récemment clos."):
            self.SendFTTH.emit('Pas de DERCO')
            # test DELC avec voisinage
            browser.find_element_by_css_selector("#tabService99 > div > a").click()
            browser.implicitly_wait(10)  # seconds
            time.sleep(1)
            TestDELC = [choix for choix in browser.find_elements_by_css_selector("#scenario > option") if choix.text == "Test DELC avec stabilité et voisinage"]
            TestDELC[0].click()
            browser.implicitly_wait(10)  # seconds
            time.sleep(1)
            browser.find_element_by_css_selector("#launchTestButton").click()

            wait = WebDriverWait(browser, 100)

            #on attend que l'interpreation du test soit visible
            self.SendFTTH.emit('En attente du test DELC avec voisinage...')
            wait.until(
                ec.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#detailLink",
                    )
                )
            )
            if check_exists_by_css_selector(browser, "#diagkoa > h1"):
                interpretation = browser.find_element_by_css_selector("#diagkoa > table:nth-child(2) > tbody > tr:nth-child(1) > td").text

            else :
                interpretation = browser.find_element_by_css_selector("#diagkoa > table:nth-child(1)").text.split('\n')[0][15:]
                #browser.find_element_by_css_selector("#diagkoa > table:nth-child(1)").text.split('\n')[0][15:]
            self.SendFTTH.emit(interpretation)


            if interpretation == "Suspicion d'un incident collectif sur le PON":

                isDERCO, nomEquipement, noChassis, noCarte, noPort, ListeND = self.Brasil(browser)
                if isDERCO:
                    browser.switch_to.window(self.pagesweb["Orchestra"])
                    # on affiche les details
                    browser.find_element_by_css_selector("#detailLink").click()
                    browser.switch_to.window(browser.window_handles[-1])

                    # on va dans PM
                    try :
                        browser.find_element_by_css_selector(
                            "#blockTabulations > li.off.tabTitle_DELC_PM"
                        ).click()

                        #on récupère la date de l'incident
                        dateAlarme = browser.find_element_by_css_selector("#row_0_delc_res_ftth_pm_ponlos_alarms_time_1").text
                    except :
                        dateAlarme = datetime.today().strftime("%d/%m/%Y")

                    #on créé un derco ADELIA & on regarde si il n'y a pas déjà des incidents en cours dans adelia
                    isDercoEnCours = self.adeliaCreationBrasil(browser, nomEquipement, dateAlarme, noChassis, noCarte, noPort)

                    #Si il n'y a pas de DERCO en cours  on créé un DERCO
                    if isDercoEnCours == False :                  
                        #TODO rétablir la création de Ticket Pere 
                        self.emit("le client a un seul voisin (même addresse même heure)")
                        self.emit("nom equipement : ")
                        self.emit(str(nomEquipement))
                        self.emit("dateAlarme :")
                        self.emit(str(dateAlarme))
                        self.emit("liste des ND des voisins : ")
                        self.emit(str(ListeND))    
                        numeroTP = False
                        self.emit("merci de créer le Ticket père manuellement")
                        
                        # self.oceaneCreationTP(browser, 'PONLOSS', dateAlarme, nomEquipement, ListeND)
                        # #on retourne sur Adelia recupérer le numero de TI Oceane qui vient d'être créé
                        # browser.switch_to.window(self.pagesweb["Adelia"])
                        # browser.refresh()
                        # numTP = browser.find_element_by_css_selector("#numTIOceane > table > tbody > tr > td:nth-child(2)").text
                        #return "CREATION DERCO", numTP, None
                        return False, None, None
                    #sinon on arrete le programme
                    else : return False, None, None

                else : return "PAS DE DERCO", None, None


            elif interpretation == "Ligne coupée domaine réseau" or interpretation == "Incident collectif sur la boucle locale optique récemment clos":
                # on affiche les details
                browser.find_element_by_css_selector("#detailLink").click()
                browser.switch_to.window(browser.window_handles[-1])

                # on va dans PM
                browser.find_element_by_css_selector(
                    "#blockTabulations > li.off.tabTitle_DELC_PM"
                ).click()

                # nom equipement
                nomEquipement = browser.find_element_by_css_selector(
                    "#row_1_delc_res_ftth_pm_neighbour_pm_name"
                ).text

                ListeVoisins = browser.find_element_by_css_selector(
                    "#delc_cat_ftth_pm_ont_alarms"
                ).find_elements_by_tag_name("tr")
                ListeInfosVoisins = []

                #si le voisin est une ligne vide ou s'il n'y a pas de voisins
                if len(ListeVoisins)<2 or ListeVoisins[1].find_elements_by_tag_name("td")[1].text =='':
                    return "PAS DE DERCO",None, None

                for voisin in ListeVoisins[1:]:
                    # on stocke la date du probleme le type d'alarme et l'adresse et le ND
                    ListeInfosVoisins.append(
                        [
                            datetime.strptime(voisin.find_elements_by_tag_name("td")[1].text,"%d/%m/%y %H:%M:%S"),
                            voisin.find_elements_by_tag_name("td")[3].text,
                            voisin.find_elements_by_tag_name("td")[8].text,
                            voisin.find_elements_by_tag_name("td")[9].text,
                        ]
                    )
                    #on récupère les infos de notre client
                    if voisin.find_elements_by_tag_name("td")[9].text == self.ND:
                    #if voisin.find_elements_by_tag_name("td")[9].text == ND:
                        # on récupère la date de notre ND et on créée l'intervale +-10secs
                        dateIncident = voisin.find_elements_by_tag_name("td")[1].text
                        date = datetime.strptime(
                            voisin.find_elements_by_tag_name("td")[1].text,
                            "%d/%m/%y %H:%M:%S",
                        )
                        borneSup = date + timedelta(seconds=10)
                        borneInf = date - timedelta(seconds=10)
                        addresse = voisin.find_elements_by_tag_name("td")[8].text
                        numDepartement = addresse.split(",")[-2][1:3]
                        typeAlarme = voisin.find_elements_by_tag_name("td")[3].text
                
                #On regarde si le client est dans la liste des cas PM
                try : 
                    addresse
                except NameError : 
                    self.emit("Le client n'est pas dans la liste PM merci de traiter de cas manuellement\n")
                    return False, None, None
                
                #on stocke tous les voisins (et le client) présent dans un intervalle de +-10s
                listeVoisinsReduite = []
                for voisin in ListeInfosVoisins:
                    if borneInf < voisin[0] and voisin[0] < borneSup and voisin[1] == typeAlarme:
                        listeVoisinsReduite.append(voisin)

                print("len(listeVoisinsReduite) : ", len(listeVoisinsReduite))
                #si on a le client et au moins deux voisins qui sont dans l'intervale +-10s
                if len(listeVoisinsReduite) >= 3:
                    ListeND = [row[3] for row in listeVoisinsReduite]
                    
                    #TODO rétablir la création de Ticket Pere 
                    self.emit("le client a au moins deux voisins qui sont dans l'intervale +-10s")
                    self.emit("nom equipement : ")
                    self.emit(str(nomEquipement))
                    self.emit("numDepartement : ")
                    self.emit(str(numDepartement))
                    self.emit("dateIncident :")
                    self.emit(str(dateIncident))
                    self.emit("liste des ND des voisins : ")
                    self.emit(str(ListeND))    
                    numeroTP = False
                    self.emit("merci de créer le Ticket père manuellement")
                    
                    #numeroTP = self.adeliaCreationTP(browser, listeVoisinsReduite, nomEquipement, numDepartement, dateIncident)
                    
                    #si pas de pb dans ADELIA on retourne les infos sinon on stoppe
                    if numeroTP != False :    
                        self.oceaneCreationTP(browser, 'PONLOSS', dateIncident, nomEquipement, ListeND)

                        #on retourne sur Adelia recupérer le numero de TI Oceane qui vient d'être créé
                        browser.switch_to.window(self.pagesweb["Adelia"])
                        browser.refresh()
                        numTP = browser.find_element_by_css_selector("#numTIOceane > table > tbody > tr > td:nth-child(2)").text
                        return "CREATION DERCO", numeroTP, None

                    else : return False, None, None

                #Si le client est seul
                elif len(listeVoisinsReduite) <= 1:
                    #traitement unitaire
                    return "PAS DE DERCO",None, None


                #s'il sont deux (client +1 voisin)
                else:
                    adresse1 = listeVoisinsReduite [0][1].split(",")
                    adresse2 = listeVoisinsReduite [1][1].split(",")
                    date1 = listeVoisinsReduite [0][0]
                    date2 = listeVoisinsReduite [1][0]

                    # on regarde si les dates correspondent et si les adresses sont les mêmes
                    if date1 == date2 and adresse1[-4:-1] == adresse2[-4:-1]:
                        ListeND = [row[3] for row in listeVoisinsReduite]
                    
                        #TODO rétablir la création de Ticket Pere 
                        self.emit("le client a un seul voisin (même addresse même heure)")
                        self.emit("nom equipement : ")
                        self.emit(str(nomEquipement))
                        self.emit("numDepartement : ")
                        self.emit(str(numDepartement))
                        self.emit("dateIncident :")
                        self.emit(str(dateIncident))
                        self.emit("liste des ND des voisins : ")
                        self.emit(str(ListeND))    
                        numeroTP = False
                        self.emit("merci de créer le Ticket père manuellement")
                        #Creation de DERCO & verification si DERCO n'est pas déjà existant
                        #numeroTP = self.adeliaCreationTP(browser, listeVoisinsReduite, nomEquipement, numDepartement, dateIncident)
                        
                        #si pas de pb dans ADELIA on retourne les infos sinon on stoppe
                        if numeroTP != False:
                            self.oceaneCreationTP(browser, 'PONLOSS', dateIncident, nomEquipement, listeVoisinsReduite)

                            #on retourne sur Adelia recupérer le numero de TI Oceane qui vient d'être créé
                            browser.switch_to.window(self.pagesweb["Adelia"])
                            browser.refresh()
                            numTP = browser.find_element_by_css_selector("#numTIOceane > table > tbody > tr > td:nth-child(2)").text
                            return "CREATION DERCO",numeroTP, None
                        else : return False, None, None

                    else:
                        #Test unitaire
                        return "PAS DE DERCO",None, None

            elif interpretation == 'Ligne coupée isolé client':
                #PAS DE DERCO
                return "PAS DE DERCO",None, None

            elif interpretation == 'Défaut non identifié - Session inactive':
                #SESSION INACTIVE
                return "SESSION INACTIVE",None, None

            elif interpretation == 'Défaut non identifié - Session active':
                #ACCES FTTH OK
                return "ACCES FTTH OK",None, None

            elif interpretation == 'Fonctionnement Accès FTTH OK - Session inactive - Accès au service VoIP KO':
                #SESSION INACTIVE
                return "SESSION INACTIVE",None, None

            elif interpretation == 'Fonctionnement Accès FTTH OK - Session active - Accès au service VoIP OK':
                #ACCES FTTH OK
                return "ACCES FTTH OK",None, None

            elif interpretation == 'Fonctionnement Accès FTTH OK - Session inactive':
                #SESSION INACTIVE
                return "SESSION INACTIVE",None, None

            elif interpretation == 'ONT éteint ou alimentation HS depuis moins de 3 jours':
                #LIEN ENTRE ONT ET LIVEBOX HS
                return "LIEN ENTRE ONT ET LIVEBOX HS",None, None

            elif interpretation == 'ONT intégré à la Livebox éteint ou alimentation HS depuis moins de 3 jours':
                #LIEN ENTRE ONT ET LIVEBOX HS
                return "LIEN ENTRE ONT ET LIVEBOX HS",None, None

            else:
                return False, None, None



        elif browser.find_element_by_css_selector("#dercoUrlsKO").text == '':
            self.SendFTTH.emit(browser.find_element_by_css_selector("#errors").text)
            return 'ERREUR', None, None

        #DERCO en cours
        else:
            self.SendFTTH.emit('DERCO en cours')
            ticketPere = (
                browser.find_element_by_css_selector("#dercoUrlsKO")
                .text[14:]
                .split(",")[-1]
            )
            message = "incident Adelia : " + ticketPere
            self.SendFTTH.emit(message)

            #check dans adelia
            numeroTi, typeTP, createur = self.adeliaRecupTP(browser, ticketPere)

            return typeTP, numeroTi, createur
            #self.RenduTicketOceane(browser, numeroTi, typeTP)
            #pass
            # Rattachement de session sur Adelia

    def descritpionDerangement(self, listeVoisinsReduite):
        phraseFinale = "####"
        for voisin in listeVoisinsReduite:
            phraseFinale = phraseFinale + str(voisin[-1]) + "_"
        return phraseFinale[:-1] + "#"


    def nomEquipement(self, nomEquipement, numDepartement):
        nb = []
        lettres = []
        for i in list(nomEquipement.split("-")[1]):
            if i.isdigit():
                nb.append(i)
            else:
                lettres.append(i)
        nb = str("".join(nb))
        lettres = str("".join(lettres))
        temp = (
            nomEquipement[2:5]
            + " "
            + numDepartement
            + "/"
            + lettres
            + " "
            + nb
            + "/"
        )
        if "-".join(nomEquipement.split("-")[2:])[:2] == "PT" or "-".join(nomEquipement.split("-")[2:])[:2] == "PM":
            temp += "-".join(nomEquipement.split("-")[2:])[:2] + " " + "-".join(nomEquipement.split("-")[2:])[2:]
        else:
            temp += "-".join(nomEquipement.split("-")[2:])

        return temp

    def adeliaCreationTP(self, browser, listeVoisinsReduite, nomEquipement, numDepartement, dateIncident):
        browser.switch_to.window(self.pagesweb["Mon SI"])
        self.liensMonSI["ADELIA"].click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        browser.switch_to.window(browser.window_handles[-1])
        #self.pagesweb["Adelia"]=browser.current_window_handle

        ActionChains(browser).move_to_element(
                browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(2) > td > form > table > tbody > tr:nth-child(1) > td:nth-child(2)")
                #).click()
        ).perform()

        browser.find_element_by_css_selector("#menu1 > li:nth-child(6)").click()

        date = datetime.strptime(dateIncident,"%d/%m/%y %H:%M:%S")
        date7j = date + timedelta(days=7)
        date7j = date7j.strftime("%d/%m/%Y")

        dateModifiee = dateIncident.split(" ")[0][:-2] +"20" + dateIncident.split(" ")[0][-2:]
        browser.find_element_by_css_selector("#dateDebut").clear()
        browser.find_element_by_css_selector("#dateDebut").send_keys(dateModifiee)
        browser.find_element_by_css_selector("#heureDebut").clear()
        browser.find_element_by_css_selector("#heureDebut").send_keys(dateIncident.split(" ")[1][:2])
        browser.find_element_by_css_selector("#minuteDebut").clear()
        browser.find_element_by_css_selector("#minuteDebut").send_keys(dateIncident.split(" ")[1][3:5])

        browser.find_element_by_css_selector("#dateFinPrevue").send_keys(date7j)
        browser.find_element_by_css_selector("#heureFinPrevue").send_keys(dateIncident.split(" ")[1][:2])
        browser.find_element_by_css_selector("#minuteFinPrevue").send_keys(dateIncident.split(" ")[1][3:5])

        browser.find_element_by_css_selector("#minuteFinPrevue").click()

        browser.find_element_by_css_selector(
            "#origineIncident > table > tbody > tr > td:nth-child(2) > font > select > option:nth-child(12)"
        ).click()
        browser.find_element_by_css_selector(
            "#sourceIncident > table > tbody > tr > td:nth-child(2) > font > select > option:nth-child(16)"
        ).click()
        browser.find_element_by_css_selector(
            "#descriptionIncident > table > tbody > tr > td:nth-child(2) > font > textarea"
        ).send_keys(self.descritpionDerangement(listeVoisinsReduite))
        browser.find_element_by_css_selector(
            "#nomEq > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(1) > td > font > input[type=text]"
        ).send_keys(self.nomEquipement(nomEquipement, numDepartement))
        browser.find_element_by_css_selector(
            "#natureImpact > table > tbody > tr > td:nth-child(2) > font > select > option:nth-child(2)"
        ).click()

        #valider
        browser.find_element_by_css_selector(
            "#tabContinuer > a:nth-child(2)"
        ).click()
        time.sleep(1)
       #si Derco en cours sur cet appareil
        if browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(3) > td > center > form > table:nth-child(36) > tbody > tr > td").text != '':
            self.SendFTTH.emit("Erreur dans ADELIA merci de verifier")
            return False
        else :
            #on clique sur créer TI
            browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(3) > td > center > form > table:nth-child(37) > tbody > tr:nth-child(3) > td:nth-child(3) > table > tbody > tr:nth-child(9) > td:nth-child(2) > font > a").click()
            return True

    def adeliaCreationBrasil(self, browser, nomEquipement, dateIncident, noChassis, noCarte, noPort):
        browser.switch_to.window(self.pagesweb["Mon SI"])
        self.liensMonSI["ADELIA"].click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        browser.switch_to.window(browser.window_handles[-1])
        self.pagesweb["Adelia"]=browser.current_window_handle

        ActionChains(browser).move_to_element(
                browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(2) > td > form > table > tbody > tr:nth-child(1) > td:nth-child(2)")
                #).click()
        ).perform()

        browser.find_element_by_css_selector("#menu1 > li:nth-child(6)").click()

        try :
            date = datetime.strptime(dateIncident,"%d/%m/%y %H:%M:%S")
        except :
            date = datetime.strptime(dateIncident,"%d/%m/%Y")

        date7j = date + timedelta(days=7)
        date7j = date7j.strftime("%d/%m/%Y")

        dateModifiee = dateIncident.split(" ")[0][:-2] +"20" + dateIncident.split(" ")[0][-2:]
        browser.find_element_by_css_selector("#dateDebut").clear()
        browser.find_element_by_css_selector("#dateDebut").send_keys(dateModifiee)
        browser.find_element_by_css_selector("#heureDebut").clear()
        browser.find_element_by_css_selector("#heureDebut").send_keys(dateIncident.split(" ")[1][:2])
        browser.find_element_by_css_selector("#minuteDebut").clear()
        browser.find_element_by_css_selector("#minuteDebut").send_keys(dateIncident.split(" ")[1][3:5])

        browser.find_element_by_css_selector("#dateFinPrevue").send_keys(date7j)
        browser.find_element_by_css_selector("#heureFinPrevue").clear()
        browser.find_element_by_css_selector("#heureFinPrevue").send_keys(dateIncident.split(" ")[1][:2])
        browser.find_element_by_css_selector("#minuteFinPrevue").clear()
        browser.find_element_by_css_selector("#minuteFinPrevue").send_keys(dateIncident.split(" ")[1][3:5])

        browser.find_element_by_css_selector("#minuteFinPrevue").click()

        browser.find_element_by_css_selector(
            "#origineIncident > table > tbody > tr > td:nth-child(2) > font > select > option:nth-child(4)"
        ).click()
        browser.find_element_by_css_selector(
            "#sourceIncident > table > tbody > tr > td:nth-child(2) > font > select > option:nth-child(16)"
        ).click()
        browser.find_element_by_css_selector(
            "#descriptionIncident > table > tbody > tr > td:nth-child(2) > font > textarea"
        ).send_keys("DERCO FTTH PONLOSS")
        browser.find_element_by_css_selector(
            "#nomEq > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(1) > td > font > input[type=text]"
        ).send_keys(nomEquipement)

        browser.find_element_by_css_selector("#numBaie > table > tbody > tr > td:nth-child(2) > font > input[type=text]").send_keys(noChassis)
        browser.find_element_by_css_selector("#numCarte > table > tbody > tr > td:nth-child(2) > font > input[type=text]").send_keys(noCarte)
        browser.find_element_by_css_selector("#numPort > table > tbody > tr > td:nth-child(2) > font > input[type=text]").send_keys(noPort)

        browser.find_element_by_css_selector(
            "#natureImpact > table > tbody > tr > td:nth-child(2) > font > select > option:nth-child(2)"
        ).click()

        #valider
        browser.find_element_by_css_selector(
            "#tabContinuer > a:nth-child(2)"
        ).click()
        time.sleep(1)

        #si Derco en cours sur cet appareil
        if browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(3) > td > center > form > table:nth-child(36) > tbody > tr > td").text != '':
            self.SendFTTH.emit("Doublon de DERCO potentiel dans ADELIA merci de verifier")
            return True
        else :
            #on clique sur créer TI
            browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(3) > td > center > form > table:nth-child(37) > tbody > tr:nth-child(3) > td:nth-child(3) > table > tbody > tr:nth-child(9) > td:nth-child(2) > font > a").click()
            return False

    def adeliaRecupTP(self, browser, ticketPere):
        browser.switch_to.window(self.pagesweb["Mon SI"])
        self.liensMonSI["ADELIA"].click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        browser.switch_to.window(browser.window_handles[-1])
        self.pagesweb["adeliaRecupTP"]=browser.current_window_handle

        time.sleep(1)
        #accès au ticket
        browser.find_element_by_css_selector("body > center > table > tbody > tr:nth-child(3) > td > center > form > table > tbody > tr:nth-child(4) > td:nth-child(1) > font > input[type=radio]").click()
        time.sleep(1)
        browser.find_element_by_css_selector("#disruptionId > input[type=text]").send_keys(
            ticketPere
        )
        browser.find_element_by_css_selector(
            "body > center > table > tbody > tr:nth-child(3) > td > center > form > table > tbody > tr:nth-child(18) > td > a > font > strong"
        ).click()
        browser.find_element_by_css_selector(
            "body > center > table > tbody > tr:nth-child(3) > td > center > form > table > tbody > tr:nth-child(19) > td > table > tbody > tr:nth-child(3) > td:nth-child(4) > a > img"
        ).click()

        #recuperation des infos
        typeDerangement = browser.find_element_by_css_selector(
            "body > center > table > tbody > tr:nth-child(3) > td > center > form > table:nth-child(37) > tbody > tr:nth-child(3) > td:nth-child(2) > table > tbody > tr > td:nth-child(2) > table:nth-child(2) > tbody > tr > td:nth-child(2) > font"
        ).text
        if typeDerangement == "Incd":
            if check_exists_by_css_selector(browser, "#numTIOceane > table > tbody > tr > td:nth-child(2) > font"):
                numero = browser.find_element_by_css_selector("#numTIOceane > table > tbody > tr > td:nth-child(2) > font").text
            else :
                self.SendFTTH.emit("Numéro de TI non présent dans ADELIA merci de verifier manuellement")
                numero = ''
                typeDerangement = False

        elif typeDerangement == "TP":
            numero = browser.find_element_by_css_selector(
                "#numTP > table > tbody > tr > td:nth-child(2) > font"
            ).text

        createur = browser.find_element_by_css_selector("#idOperateur > table > tbody > tr > td:nth-child(2)").text
        if "afd" in createur.lower() : createur = "afd"
        else : createur = "externe"

        browser.switch_to.window(browser.window_handles[0])
        return numero, typeDerangement, createur


    def oceaneCreationTP(self, browser, typeTP, date, nomEquipement, listeND):
        time.sleep(1)
        browser.switch_to.window(browser.window_handles[-1])
        self.pagesweb["oceaneCreationTP"]=browser.current_window_handle
        browser.switch_to.frame("OCEANE")
        #enregistrer ressource et créer ticket
        browser.find_element_by_css_selector("#PB_ENR_CRETIC").click()
        #Impact client
        browser.find_element_by_css_selector("#IDTIMPCLISYS > option:nth-child(6)").click()
        #technicien responsable
        choix=[i for i in browser.find_element_by_css_selector("#IDTUTLPEC").find_elements_by_tag_name('option') if i.get_attribute('value') == browser.find_element_by_css_selector("#IDTUTL").get_attribute('value')]
        choix[0].click()
        #Priorite de traitement : P2
        browser.find_element_by_css_selector("#STRIDTPRI > option:nth-child(3)").click()
        #DRI dans DRC
        DRI = browser.find_element_by_css_selector("#ETRVALUEDISPLAYED").get_attribute('value')
        browser.find_element_by_css_selector("#ATRVALUEDISPLAYED").send_keys(DRI)
        #Ticket : père
        browser.find_element_by_css_selector("#DDLTICKET > option:nth-child(2)").click()

        #date de retablisement
        date = browser.find_element_by_css_selector("#INITIALPLANNEDRESTORATIONDATEDate").get_attribute('value')
        heure = browser.find_element_by_css_selector("#INITIALPLANNEDRESTORATIONDATEDropDownHours").get_attribute('value')
        minute = browser.find_element_by_css_selector("#INITIALPLANNEDRESTORATIONDATEDropDownMins").get_attribute('value')

        browser.find_element_by_css_selector("#CONFIRMEDPLANNEDRESTORATIONDATEDate").send_keys(date)

        #enregistrer
        browser.find_element_by_css_selector("#ENRTIC").click()
        #ajout commetaire
        browser.find_element_by_css_selector("#btnAddComment").click()

        #browser.switch_to.default_content()
        #browser.switch_to.frame("OCEANE")
        #browser.switch_to.frame("frameCommonPopover")
        #on va dans la liste des commentaires
        #browser.find_element_by_css_selector("#lblCmtHelpBtn").click()
        browser.switch_to.frame("frameCommonPopover")
        #on va dans la liste des commentaires
        browser.find_element_by_css_selector("#lblCmtHelpBtn").click()
        browser.switch_to.frame("frameCommonPopover")
        ListeCommentaires = browser.find_element_by_css_selector("#dtStanDes").find_elements_by_tag_name("tr")


        if typeTP == 'BLO':
            Commentaire = ListeCommentaires[7].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[6].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            #on accède au code source du commentaire
            browser.switch_to.default_content()
            browser.switch_to.frame("OCEANE")
            browser.switch_to.frame("frameCommonPopover")
            browser.find_element_by_css_selector("#cke_29").click()

            #on modifie le commentaire
            texte=browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").get_attribute('value')

            message = texte[:140] + date + texte[140:176] + nomEquipement + texte[176:206] + str(len(listeND)) + texte[206:235] + ('_').join(listeND) +'_'+ texte[-12:]
            browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").clear()
            browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").send_keys(message)
            browser.find_element_by_css_selector("#cke_29").click()

            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

            #on revient sur le iframe de base
            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))

        elif typeTP == 'PONLOSS':
            Commentaire = ListeCommentaires[7].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[7].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            #on accède au code source du commentaire
            browser.switch_to.default_content()
            browser.switch_to.frame("OCEANE")
            browser.switch_to.frame("frameCommonPopover")
            browser.find_element_by_css_selector("#cke_29").click()

            #on modifie le commentaire
            texte=browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").get_attribute('value')

            message = texte[:140] + date + texte[140:176] + nomEquipement + texte[176:206] + str(len(listeND)) + texte[206:235] + ('_').join(listeND) +'_'+ texte[-12:]
            browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").clear()
            browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").send_keys(message)
            browser.find_element_by_css_selector("#cke_29").click()

            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

            #on revient sur le iframe de base
            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))

        browser.switch_to.frame("OCEANE")
        browser.find_element_by_css_selector("#menu_lbtn_I5_L1").click()
        browser.find_element_by_css_selector("#TRFRESP_X").click()
        browser.find_element_by_css_selector("#TEXT_IDENTIFIANTEDS").send_keys("SNOSU8")
        browser.find_element_by_css_selector("#ENRTICQUIT").click()

    def RessourceConcernee(self, typeTP, createur):
        if (typeTP == "Incd" or typeTP == "TP") and createur == 'afd':
            return "TICKET FILS DECLIC"

        elif (typeTP == "Incd" or typeTP == "TP") and createur =='externe':
            return "TICKET FILS N1/N2"

        elif typeTP == "SESSION INACTIVE":
            return "SESSION KO"

        elif typeTP == "ACCES FTTH OK":
            return "ACCES INTERNET OK"

        elif typeTP =="LIEN ENTRE ONT ET LIVEBOX HS":
            return "LIAISON LOCALE KO"

        elif typeTP == "CREATION DERCO":
            return "TICKET PERE DELCIC"

        elif typeTP == "PAS DE DERCO":
            return "LIAISON OPTIQUE KO"
    """
    #TODO
    if typeTP ==
        return"CONFIGURATION KO"

    if typeTP ==
        return "QUALITE"
    """

    def RenduTicketOceane(self, browser, typeTP, numeroTi, createur):
        if str(type(numeroTi))[8:16]== "NoneType": numeroTi=""
        if str(type(createur))[8:16]== "NoneType": createur=""

        browser.switch_to.window(self.pagesweb["Oceane Ticket"])

        #on clique sur les caractéristiques
        browser.switch_to.default_content()
        browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))
        browser.find_element_by_css_selector("#menu_hlnk_I4_L1").click()
        browser.find_element_by_css_selector("#menu_lbtn_I4_5_L2").click()

        #on rajoute un Produit associé et Ressource concernée
        browser.find_element_by_css_selector("#forassoproduct").send_keys("FTTH")

        RessConcernee = self.RessourceConcernee(typeTP, createur)
        browser.find_element_by_css_selector("#forconcernresource").send_keys(RessConcernee)

        #on ajoute un commentaire
        browser.find_element_by_css_selector("#menu_lbtn_I2_L1").click()
        #browser.switch_to.frame("PopupOCEANE")
        time.sleep(1)
        browser.find_element_by_css_selector("#btnAddComment").click()
        browser.switch_to.frame("frameCommonPopover")
        #on va dans la liste des commentaires
        browser.find_element_by_css_selector("#lblCmtHelpBtn").click()
        browser.switch_to.frame("frameCommonPopover")
        ListeCommentaires = browser.find_element_by_css_selector("#dtStanDes").find_elements_by_tag_name("tr")

        if typeTP == "PAS DE DERCO":
            Commentaire = ListeCommentaires[1].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[1].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))
            browser.switch_to.frame(browser.find_element_by_css_selector("#frameCommonPopover"))
            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

        elif typeTP == "ACCES FTTH OK":
            Commentaire = ListeCommentaires[2].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[2].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))
            browser.switch_to.frame(browser.find_element_by_css_selector("#frameCommonPopover"))
            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

        elif typeTP == "SESSION INACTIVE":
            Commentaire = ListeCommentaires[3].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[3].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))
            browser.switch_to.frame(browser.find_element_by_css_selector("#frameCommonPopover"))
            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

        elif typeTP == 'Incd' or typeTP == 'TP':
            Commentaire = ListeCommentaires[4].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[4].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            #on accède au code source du commentaire
            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))
            browser.switch_to.frame(browser.find_element_by_css_selector("#frameCommonPopover"))
            browser.find_element_by_css_selector("#cke_29").click()

            #on modifie le commentaire
            aa=browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").get_attribute('value')
            debut = aa[:aa.index("XXXX")]
            idx = aa.index("XXXX")+9
            fin = aa[idx:]
            message = debut + numeroTi+ fin
            browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").clear()
            browser.find_element_by_xpath("//*[@id='cke_1_contents']/textarea").send_keys(message)
            browser.find_element_by_css_selector("#cke_29").click()

            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

            #on revient sur le iframe de base
            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))

            if typeTP == 'Incd':
                #relations
                browser.find_element_by_css_selector("#menu_hlnk_I7_L1").click()
                #père / fils
                browser.find_element_by_css_selector("#menu_lbtn_I7_1_L2").click()

                browser.switch_to.default_content()
                browser.switch_to.frame("PopupOCEANE")

                browser.find_element_by_css_selector("#ATTACH_PERE").click()
                time.sleep(1)
                browser.find_element_by_css_selector("#btnDYes").click()

                browser.find_element_by_css_selector("#ticNum").send_keys(numeroTi)
                #browser.find_element_by_css_selector("#ENRTICQUIT").click()

                browser.find_element_by_css_selector("#SEARCHTICMASTER").click()

        elif typeTP == "LIEN ENTRE ONT ET LIVEBOX HS":
            Commentaire = ListeCommentaires[5].find_elements_by_css_selector("td")[2].text
            ListeCommentaires[5].find_elements_by_css_selector("td")[0].find_element_by_tag_name("a").click()

            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_css_selector("body > iframe.startPageBody"))
            browser.switch_to.frame(browser.find_element_by_css_selector("#frameCommonPopover"))
            #on enregistre le commentaire
            browser.find_element_by_css_selector("#btnSaveCmt").click()

        #enregistrer et quitter
        browser.switch_to.default_content()
        browser.switch_to.frame("PopupOCEANE")
        browser.find_element_by_css_selector("#ENRTICQUIT").click()

        self.SendFTTH.emit("Processus terminé, en attente de confirmation dans votre BAL technicien")



    def Brasil(self, browser):
        browser.switch_to.window(self.pagesweb["Mon SI"])
        self.liensMonSI["BRASIL"].click()
        browser.implicitly_wait(10)  # seconds
        time.sleep(1)
        self.pagesweb["Brasil"]=browser.window_handles[-1]
        browser.switch_to.window(self.pagesweb["Brasil"])

        browser.find_element_by_css_selector("body > table:nth-child(12) > tbody > tr.bg_entete > td:nth-child(6) > div > a").click()
        browser.find_element_by_css_selector("body > table:nth-child(14) > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(3) > td").click()
        browser.find_element_by_css_selector("body > table:nth-child(16) > tbody > tr > td:nth-child(3) > table > tbody > tr:nth-child(4) > td > form > table > tbody > tr:nth-child(1) > td:nth-child(2) > input").send_keys(self.ND)
        browser.find_element_by_css_selector("#thirdButton").click()
        browser.implicitly_wait(10)
        time.sleep(2)
        browser.find_element_by_css_selector("#customer > table > tbody > tr:nth-child(1) > td > table > tbody > tr > td:nth-child(3) > div > a").click()

        noChassis = browser.find_element_by_css_selector("#graphique > table:nth-child(2) > tbody > tr > td:nth-child(3) > table > tbody > tr:nth-child(3) > td > font > a:nth-child(1)").text
        noCarte = browser.find_element_by_css_selector("#graphique > table:nth-child(2) > tbody > tr > td:nth-child(3) > table > tbody > tr:nth-child(3) > td > font > a:nth-child(2)").text
        noPort = browser.find_element_by_css_selector("#graphique > table:nth-child(2) > tbody > tr > td:nth-child(3) > table > tbody > tr:nth-child(3) > td").text[-1]
        nomEquipement = browser.find_element_by_css_selector("#graphique > table:nth-child(3) > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(2) > td > font > a").text

        browser.find_element_by_css_selector("#graphique > table:nth-child(2) > tbody > tr > td:nth-child(3) > table > tbody > tr:nth-child(3) > td > font > a:nth-child(2)").click()
        browser.find_element_by_css_selector("#general > table > tbody > tr:nth-child(1) > td > table > tbody > tr > td:nth-child(4)").click()
        browser.find_element_by_css_selector("#customer > table:nth-child(1) > tbody > tr > td > table > tbody > tr > td:nth-child(4)").click()

        #TODO ligne trop longue à s'executer, trouver un autre moyen 
        print('Recherche des voisins du PORT...')
        ListeVoisins = [voisin.find_elements_by_tag_name("td")[12].text for voisin in browser.find_element_by_css_selector("#resourceList").find_elements_by_tag_name("tr")[1:] if voisin.find_elements_by_tag_name("td")[1].text == noPort and voisin.find_elements_by_tag_name("td")[12].text != self.ND]
        print('Fin de la recherche des voisins du PORT')
        for voisin in ListeVoisins[:3]:
            self.SendFTTH.emit('Test DELC des voisins')
            browser.switch_to.window(self.pagesweb["Orchestra"])
            browser.find_element_by_css_selector("#clientNd").clear()
            browser.find_element_by_css_selector("#clientNd").send_keys(voisin)
            browser.find_element_by_css_selector("#loadParametersButton").click()
            time.sleep(3)
            #DELC
            browser.find_element_by_css_selector("#tabService99 > div > a").click()
            browser.implicitly_wait(10)  # seconds
            time.sleep(1)

            TestDELC=[]
            TestDELC = [choix for choix in browser.find_elements_by_css_selector("#scenario > option") if choix.text == "Test DELC avec stabilité et voisinage"]
            print(TestDELC)
            TestDELC[0].click()
            browser.implicitly_wait(10)  # seconds
            time.sleep(1)
            browser.find_element_by_css_selector("#launchTestButton").click()

            wait = WebDriverWait(browser, 100)

            #TODO BUG N4ARRIVE PAS A DETECTER QUAND PLUSIEURS INTERPRETATIONS
            #on attend que l'interpreation du test soit visible
            wait.until(
                ec.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#diagkoa > table:nth-child(1) > tbody > tr:nth-child(1) > td",
                    )
                )
            )

            interpretation = browser.find_element_by_css_selector(
                "#diagkoa > table:nth-child(1) > tbody > tr:nth-child(1) > td"
            ).text
            self.SendFTTH.emit(interpretation)
            if interpretation != "Suspicion d'un incident collectif sur le PON" and interpretation != "Test Delc impossible":
                #PAS DERCO
                return False, nomEquipement, noChassis, noCarte, noPort, ListeVoisins
        #DERCO
        return True, nomEquipement, noChassis, noCarte, noPort, ListeVoisins





    def closingBrowser(self, browser) :
        browser.switch_to.parent_frame()
        browser.find_element_by_css_selector(".encadre2 > div:nth-child(4) > span:nth-child(6) > a:nth-child(1) > img:nth-child(1)").click()
        browser.switch_to.window(browser.window_handles[-1])
        browser.implicitly_wait(10) # seconds
        time.sleep(1)
        browser.find_element_by_css_selector("img.curseur:nth-child(1)").click()
        browser.quit()
