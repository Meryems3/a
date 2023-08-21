#Importation des librairies

import streamlit as st
import datetime
import pandas as pd
import numpy as np

#fonction qui determine si une date est valide 


def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False
    

#Fonction d interpolation linéaire 
def interpolation_lineaire(MJ,data,colonne):
    taux_interpole=0
    x=MJ
    if x<data['Maturité'][0]:
        taux_interpole=colonne[0]
    elif x>data['Maturité'][len(data)-1] :
        x1 = data['Maturité'][len(data)-1]
        x2 = data['Maturité'][len(data)-2]
        y1 = colonne[len(data)-1]
        y2 = colonne[len(data)-2]
        taux_interpole=y1 + (y1 - y2) * (x - x1) / (x1 - x2)      
    else :
        for i in range(len(data['Maturité']) - 1):
            if x==data['Maturité'][i]:
                taux_interpole = colonne[i]
            elif data['Maturité'][i] <= MJ < data['Maturité'][i + 1]:
                if data['Maturité'][i]<365 and data['Maturité'][i + 1]>365 :
                    x1 = data['Maturité'][i]
                    x2 = data['Maturité'][i + 1]
                    y1 = data['TMPA'][i]
                    y2 = data['TMPA'][i + 1]
                    taux_interpole = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
                else :
                    x1 = data['Maturité'][i]
                    x2 = data['Maturité'][i + 1]
                    y1 = colonne[i]
                    y2 = colonne[i + 1]
                    taux_interpole = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return taux_interpole

#Importation bd du bam 
date_obj = st.text_input("Entrez la date de valeur (JJ/MM/AAAA) :")
data = None

if not date_obj:
    st.warning("Veuillez entrer la date de valeur.")
else:
    if not is_valid_date(date_obj):
        st.warning("La date n'est pas au format JJ/MM/AAAA. Veuillez saisir une date valide.")
    else:
        date_obj = datetime.datetime.strptime(date_obj, "%d/%m/%Y")
        
        def taux(date_obj):
            u1="https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-obligataire/Marche-des-bons-de-tresor/Marche-secondaire/Taux-de-reference-des-bons-du-tresor?"

            #u2="date=24%2F02%2F2023&"

            u3="block=e1d6b9bbf87f86f8ba53e8518e882982#address-c3367fcefc5f524397748201aee5dab8-e1d6b9bbf87f86f8ba53e8518e882982"

            u21="date="

            u22=date_obj.day

            u23="%2F"

            u24=date_obj.month

            u25="%2F"

            u26=date_obj.year

            u27="&"

            u2=u21+ str(u22) + u23 + str(u24) + u25 + str(u26) + u27

            url=u1+u2+u3

            data=pd.read_html(url)

            data[0].drop(data[0].index[-1], inplace=True)

            return data[0]
        
        try:
            data = taux(date_obj)
        except Exception as e:
            st.error("Aucune donnée n'a été trouvée pour cette date.")
        
        if data is not None and not data.empty:
            st.write("Tableau des taux de référence des bons du Trésor")
            st.write(data)
        
            #Manipulation du tableau 


            data["Maturité"] = pd.to_datetime(data["Date d'échéance"],format='%d/%m/%Y') - pd.to_datetime(data['Date de la valeur'],format='%d/%m/%Y')

            data["Maturité"] = data["Maturité"].dt.total_seconds().astype(float)/ (24 * 60 * 60)

            data["Maturitéa"] = data["Maturité"]/ (365)

            del data["Transaction"]

            data.rename(columns={"Date d'échéance": 'Echeance', 'Taux moyen pondéré': 'Taux', 'Date de la valeur':'Date valeur', 'Maturité':'Maturité', 'Maturitéa':'Maturité en années' }, inplace=True)

            data["Taux"] = data["Taux"].str.replace('%', '').str.replace(',', '.').astype(float)
            data["Taux"]=data["Taux"]/100
            del data["Date valeur"]


            data["TMPA"] = 0
            for i in range(0,len(data)):
                if data.at[i, 'Maturité'] < 365:
                    data.at[i, 'TMPA'] = ((1 + (data.at[i, 'Taux'] * data.at[i, 'Maturité'] / 360)) ** (365 / data.at[i, 'Maturité']) - 1)
                elif data.at[i, 'Maturité'] >= 365:
                    data.at[i, 'TMPA'] = data.at[i, 'Taux']
            data= data.sort_values(by='Maturité', ascending=True)



##Création de base de données des tenors standards

if data is not None and not data.empty :
    fd = pd.DataFrame({'Maturité pleine': [ '13 sem', '26sem', '52sem', '1an', '2ans', '3ans', '4ans', '5ans', '6ans', '7ans', '8ans', '9ans', '10ans', '11ans', '12ans', '13ans', '14ans', '15ans', '16ans', '17ans', '18ans', '19ans', '20ans', '21ans', '22ans', '23ans', '24ans', '25ans', '26ans', '27ans', '28ans', '29ans', '30ans'],'Maturité en jours': [91, 182, 364, 365, 731, 1096, 1461, 1826, 2192, 2557, 2922, 3287, 3653, 4018, 4383, 4748, 5114, 5479, 5844, 6209, 6575, 6940, 7305, 7670, 8036, 8401, 8766, 9131, 9497, 9862, 10227, 10592, 10958]})
    
    #Calcul de taux zc
    S = 0
    for i in range(0,len(data)):
        if data['Maturité'][i] < 365:
            data.at[i, 'taux_zc'] = data.at[i, 'TMPA']
        elif data['Maturité'][i] >= 365:
            S = 0  
            for j in range(0,i-1):
                S = S + (1/((1 + data.at[j, 'taux_zc']) ** (j)))
            data.at[i, 'taux_zc'] = (((1 + data.at[i, 'TMPA']) / (1 - data.at[i, 'TMPA'] * S)) ** (1 / i)) - 1

    fd['Taux de rendement'] = fd['Maturité en jours'].apply(lambda maturite: f"{round(interpolation_lineaire(maturite, data, data['Taux']) * 100, 3)}%")
    fd['Taux actuariel'] = fd['Maturité en jours'].apply(lambda maturite: f"{round(interpolation_lineaire(maturite, data, data['TMPA']) * 100, 3)}%")
    fd['Taux zéro-coupon'] = fd['Maturité en jours'].apply(lambda maturite: f"{round(interpolation_lineaire(maturite, data, data['taux_zc']) * 100, 3)}%")
    st.write("Tableau de tenors :")
    st.write(fd)
    fd['Taux de rendement'] = fd['Maturité en jours'].apply(lambda maturite: interpolation_lineaire(maturite, data, data['Taux']))
    fd['Taux actuariel'] = fd['Maturité en jours'].apply(lambda maturite: interpolation_lineaire(maturite, data, data['TMPA']))
    fd['Taux zéro-coupon'] = fd['Maturité en jours'].apply(lambda maturite: interpolation_lineaire(maturite,data,data['taux_zc']))

    a=st.button("Courbe des taux")
    if a==True :
        new3=pd.DataFrame(fd)
        new3 = pd.DataFrame({
            'Maturité en jours': fd['Maturité en jours'],
            'Taux actuariel': fd['Taux actuariel'],
            'Taux zéro-coupon': fd['Taux zéro-coupon'],
            })
        st.line_chart(new3.set_index('Maturité en jours'))
    st.subheader("Calcul les taux pour d'autres maturités")
    date_echeance=st.text_input("Veuiller entrer la date d'écheance")
    if not date_echeance:
        st.warning("Veuillez entrer la date d'échéance")
    else:
        if not is_valid_date(date_echeance):
            st.warning("La date n'est pas au format JJ/MM/AAAA. Veuillez saisir une date valide.")
        else:
            date_echeance = datetime.datetime.strptime(date_echeance, "%d/%m/%Y")
            if date_echeance<=date_obj:
                st.error("Veuillez entrer une date d'échéance valable")
            else:
                MJ=(date_echeance-date_obj).days
                taux_inter = interpolation_lineaire(MJ,data,data['Taux'])
                taux_inter2 = interpolation_lineaire(MJ,data,data['taux_zc'])
                taux_inter3=interpolation_lineaire(MJ,data,data['TMPA'])
                st.write('Taux de rendement')
                st.code("{:.3%}".format(taux_inter))
                st.write('Taux actuariel')
                st.code("{:.3%}".format(taux_inter3))
                st.write('Taux zéro-coupon')
                st.code("{:.3%}".format(taux_inter2))    