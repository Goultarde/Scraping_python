# j'importe toutes les bibliothèque nécésaire au bon fonctionnment de mon code
import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime
import pandas as pd

# je crée une fonction qui va permettre de construire l'url qui va être scraper
def find_url(energy, brand, model, km_max, km_min, page, price_max, price_min, year_max, year_min):
    url = "https://www.lacentrale.fr/listing?energies={}&makesModelsCommercialNames={}%3A{}&mileageMax={}&mileageMin={}&options=&page={}&priceMax={}&priceMin={}&yearMax={}&yearMin={}".format(
        energy, brand, model, km_max, km_min, page, price_max, price_min, year_max, year_min)
    return requests.get(url)


# je crée une fonction qui scraper le site web souhaiter en utilisant l'url générer par la fonction find_url
def scrap_list():
    # je crée une table avec toute les énergies possibles
    table_energy = ["essence", "diesel", "electrique"]
    energy = input("entrée l'énergie souhaiter, essence/diesel/electrique : ")
    # Je ne permet à l'utilisateur de rentrer que des énergie existante
    while True:
        if energy not in table_energy:
            energy = input(
                "Cette valeur n'est pas valide, entrée l'énergie souhaiter, essence/diesel/electrique : ")
        else:
            break
    #  je convertie ensuite au format de l'url
    if energy == "essence":
        energy = "ess"
    elif energy == "diesel":
        energy = "dies"
    else:
        energy = "elec"
    brand = input("entrée la marque de la voiture : ").title()
    model = input("entrée le model de la voiture : ").title()
    while True:
        try:
            km_max_str = input("Entrez le nombre de kilomètres au compteur max de la voiture : ")
            if km_max_str[0] == "-" or not km_max_str.isnumeric():
                raise ValueError("Ce n'est pas un chiffre positif")
            km_max = int(km_max_str)
            if km_max < 0:
                raise ValueError("Le nombre de kilomètres au compteur ne peut pas être négatif.")
            elif km_max > 999999999:
                raise ValueError("Le nombre de kilomètres au compteur ne peut pas être supérieur à 999999999.")
            else:
                break
        except ValueError as error:
            print(f"{error}, Veuillez entrer un nombre de kilomètres au compteur valide : ")
    km_min = 0
    while True:
        try:
            price_max_str = input("entrée le prix max : ")
            if price_max_str[0] == "-" or not price_max_str.isnumeric():
                raise ValueError("Ce n'est pas un chiffre positif")
            price_max = int(price_max_str)
            if price_max > 300000:
                raise ValueError("le prix maximum ne peut pas être surpérieur à 300 000€")
            else:
                break
        except ValueError as error:
            print(f"{error}, entrer un prix max valide : ")
    price_min = 0
    acutal_year = datetime.datetime.now().year
    while True:
        try:
            year_max = int(input("Entrez l'année max : "))
            year_min = int(input("Entrez l'année min : "))
            if year_max < year_min or year_max > acutal_year or year_max < 1900 or year_min < 1900:
                print(f"L'année doit être comprise entre 1900 et {acutal_year}. Veuillez entrer des années valides.")
                continue
            break
        except ValueError:
            print("Veuillez entrer des années valides.")

    year_max = int(year_max)
    year_min = int(year_min)
    page = 1
    # html_resquest = requests.get(url)

    data = [["brand", "model", "motor", "year",
             "mileage", "fuel", "price"]]

    while page < 11:

        # url = "https://www.lacentrale.fr/listing?energies=ess&makesModelsCommercialNames=FORD%3AMUSTANG&mileageMax=50000&mileageMin=1&options=&page=0&priceMax=93300&priceMin=27100&yearMax=2023&yearMin=2000"
        # html_resquest = requests.get(url)
        # si la requète renvoie 200, cela veut dire qu'elle a réussi donc on peut continuer la suite du programme.
        html_resquest = find_url(energy, brand, model, km_max,
                                 km_min, page, price_max, price_min, year_max, year_min)

        if html_resquest.status_code == 200:
            # html.parser va permetre de lire et d'analyser des données html, en l'occurence celle de notre page web.
            soup = BeautifulSoup(html_resquest.text, "html.parser")

            # On crée uen boucle for qui va chercher toute les balises div ayant pour class "SearchCardContainer"

            for card in soup.find_all('div', "Vehiculecard_Vehiculecard_cardBody"):
                # On récupère le text des baliste h3 des class SearchCardContainer, qui correspond donc au nom des véhicules.
                name_vehicle = card.h3.text
                # On récupère les sous titre de la voiture
                car_motor = card.find(
                    'div', 'Vehiculecard_Vehiculecard_subTitle').text
                year_card = card.find('')
                year_card_km_model_car_energy = card.find_all(
                    'div', 'Text_Text_text Vehiculecard_Vehiculecard_characteristicsItems Text_Text_body2')
                year_card = year_card_km_model_car_energy[0].text
                km = year_card_km_model_car_energy[1].text
                model_car = year_card_km_model_car_energy[2].text
                energy_car = year_card_km_model_car_energy[3].text

                # all = "year_card,km,model_car,energy : "
                # for element in year_card_km_model_car_energy:
                #    all+=f"{element.text}, "
                # garanty =
                price = card.find(
                    'span', 'Vehiculecard_Vehiculecard_price').text
                integer_price = re.findall("\d+", price)
                integer_km = re.findall("\d+", km)
                km_int = ""
                price_int = ""
                for elem in integer_price:
                    price_int += elem
                for elem in integer_km:
                    km_int += elem
                km_int = int(km_int)
                price_int = int(price_int)

                print(f"nom du véhicule : {name_vehicle}\nsous titre du véhicule : {car_motor}\nage de la voiture : {year_card}\nkilomètre au compteur : {km_int}\nmodel de la voiture : {model_car}\nenergy utiliser par la voiture : {energy_car}\nprix du véhicule : {price_int}")
                print("\n")
                data.append([brand, model, car_motor, year_card,
                             km_int, energy_car, price_int])
            print("page : ", page)
        page += 1
    with open('card.csv', 'w', newline='') as fichier_csv:
        write = csv.writer(fichier_csv)
        write.writerows(data)
    # df = pd.read_csv("card.csv")
    # print(df)


# Écrire les données dans un fichier CSV
if __name__ == "__main__":
    scrap_list()
