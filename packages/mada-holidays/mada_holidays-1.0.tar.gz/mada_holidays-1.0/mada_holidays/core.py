from datetime import date

def get_holidays(year: int) -> list:
    """ Retourne la liste des jours fériés officiels à Madagascar pour une année donnée """
    
    holidays = [
        (date(year, 1, 1), "Jour de l'an"),
        (date(year, 3, 29), "Commémoration de l'insurrection de 1947"),
        (date(year, 5, 1), "Fête du travail"),
        (date(year, 6, 26), "Fête de l'indépendance"),
        (date(year, 8, 15), "Assomption"),
        (date(year, 11, 1), "Toussain"),
        (date(year, 12, 25), "Fête de Noël"),
    ]
    return holidays