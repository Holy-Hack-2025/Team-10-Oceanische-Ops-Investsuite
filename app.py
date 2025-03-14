from flask import Flask, render_template
import openai
import requests
import json
import re
import ast

app = Flask(__name__)

openai.api_key = ("sk-proj--jkPAXjUhF4XzDF-bq8rm5FnWraBVq6DFuB53FJLNMYCx_MF4VGO1f_KLu0splZrC2muFEWakFT3"
                      "BlbkFJntA8k8TR_3AleSc-V2qaJ-5zrvQ3xSxoDyr3ixRakueaO_I_9Ob109m-xH4rb4Y62AsdDpCD8A")

NEWSAPI_KEY = "7c9fd40d035b41b2a4b430c759713630"


def fetch_news(keywords, language="en", page_size=3):
    """
    Haalt nieuwsartikelen op van NewsAPI voor de opgegeven zoekwoorden.

    Parameters:
        keywords (list): Een lijst van zoekwoorden (bedrijfsnamen, sectoren, etc.) waarvoor nieuws wordt opgehaald.
        language (str): De taal van de nieuwsartikelen die opgehaald moeten worden (standaard "en").
        page_size (int): Het aantal artikelen per zoekwoord dat opgehaald wordt (standaard 3).

    Returns:
        list: Een lijst van dictionaries met artikelgegevens (titel, url, beschrijving).
    """
    all_articles = []

    for keyword in keywords:
        query = keyword
        url = f"https://newsapi.org/v2/everything?q={query}&language={language}&pageSize={page_size}&apiKey={NEWSAPI_KEY}"

        response = requests.get(url)
        data = response.json()

        if "articles" in data and len(data["articles"]) > 0:
            articles = [
                {
                    "title": article["title"],
                    "url": article["url"],
                    "description": article["description"] if article["description"] else "Geen beschrijving beschikbaar"
                }
                for article in data["articles"]
            ]
            all_articles.extend(articles)
            print(f"Opgehaalde artikelen voor '{keyword}': {articles}")
        else:
            print(f"Geen artikelen gevonden voor '{keyword}' of er is een fout bij het ophalen.")

    return all_articles


def getCompanies(message):
    """
    Verstuurt een prompt naar GPT-4 om een lijst van bedrijven of sectoren te verkrijgen op basis van de input.

    Parameters:
        message (str): De input die bedrijven of sectoren beschrijft.

    Returns:
        str: Een string met de relevante bedrijven of sectoren zoals afgeleid door GPT-4.
    """
    prompt = ("Hey gpt, als input krijg je een aantal bedrijven of een bepaalde sector. Indien je enkel"
              "bedrijven krijgt moet je zelf afleiden over welke sector het gaat en geef je de belangrijkste"
              "bedrijven terug in deze sector waarin geïnvesteerd kan worden. Hier is de input: ")
    prompt += message

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )

    reply = response['choices'][0]['message']['content'].strip()
    return reply


def makeListOfCompanies(message):
    """
    Verstuurt een prompt naar GPT-4 om een lijst van bedrijven te verkrijgen uit de gegeven inputstring.

    Parameters:
        message (str): De inputstring die bedrijven of sectoren bevat.

    Returns:
        list: Een lijst van bedrijven zoals afgeleid door GPT-4.
    """
    prompt = ("Hey gpt, als input krijg je een bericht waarin allemaal bedrijven gaan staan. Ik wil dat"
              "je ENKEL een lijst teruggeeft met deze bedrijven in en misschien ook de sector indien relevant"
              "Dit mag enkel een lijst zijn omdat ik deze respons ga gebruiken in een andere functie waar"
              "ze een lijst verwachten. Hier is de input:")
    prompt += message

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.5,
    )

    reply = response['choices'][0]['message']['content'].strip().split("\n")
    return reply


def newsArticlesToScore(newsMessages):
    """
    Verstuurt een verzameling van nieuwsartikelen naar GPT-4 om een score te genereren voor elk bedrijf op basis van de artikelen.

    Parameters:
        newsMessages (list): Een lijst van nieuwsartikelen (elk artikel bevat een titel en een beschrijving).

    Returns:
        str: Een string waarin bedrijven worden beoordeeld met een score tussen 0 en 100.
    """
    news_strings = [
        f"Title: {article['title']}\nDescription: {article['description']}" for article in newsMessages
    ]

    news_string = "\n\n".join(news_strings)

    prompt = f"Hey GPT, hier is een verzameling nieuwsartikelen:\n{news_string}\n\n" \
             "Beoordeel elk bedrijf op basis van deze artikelen. Geef een score tussen 0 en 100 voor elk bedrijf" \
             " en geef de naam van het bedrijf gevolgd door de score als volgt: 'Tesla Inc.': 75."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        n=1,
        stop=None,
        max_tokens=200,
        temperature=0.5,
    )

    reply = response.choices[0].message.content.strip()
    return reply


def parse_scores_to_tuples(scores_string, companies, news_articles):
    """
    Verwerkt de scores en zet deze om in een lijst van tuples met de bedrijfsnaam, artikel-URL en de score.

    Parameters:
        scores_string (str): Een string met de scores van bedrijven.
        companies (list): Een lijst van bedrijven die in de beoordeling zijn meegenomen.
        news_articles (list): Een lijst van nieuwsartikelen die bij de beoordeling gebruikt zijn.

    Returns:
        str: Een string met een lijst van tuples (bedrijf, artikel-URL, score).
    """
    prompt = (f"Hey GPT, hier is een verzameling scores van bedrijven:\n{scores_string}\n\n"
              "Ik wil exact een lijst terugkrijgen van tuples van lengte 3, in deze tuple moet op"
              "de eerste positie de naam van het bedrijf komen, daarna de link naar het artikel"
              "en ten slotte de juiste score. Belangrijk dat dit ENKEL een lijst is zodat ik hier"
              "later nog verder mee kan werken!!!"

              "\n\nDe artikelen die je kunt gebruiken zijn:\n"
              f"{news_articles}\n\n"
              f"Bedrijven die betrokken zijn:\n{companies}")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        n=1,
        stop=None,
        max_tokens=500,
        temperature=0.5,
    )

    reply = response.choices[0].message.content.strip()
    return reply


def extract_list_from_string(input_string):
    """
    Zoekt naar een lijst van tuples in een string en converteert deze naar een echte Python-lijst.

    Parameters:
        input_string (str): De string die de lijst van tuples bevat.

    Returns:
        list: Een lijst van tuples (bedrijf, artikel-URL, score).
    """
    print(input_string)
    start_index = input_string.find("[")
    end_index = input_string.find("]") + 1

    if start_index != -1 and end_index != -1:
        list_string = input_string[start_index:end_index]

        try:
            extracted_list = ast.literal_eval(list_string)
            return extracted_list
        except Exception as e:
            print(f"Er is een fout opgetreden bij het verwerken van de lijst: {e}")
            return []
    else:
        print("Er werd geen lijst gevonden in de string.")
        return []

import random
import math

def generate_spread_points(width=2000, height=2000, num_points=100, min_distance=100):
    """
    Genereert een lijst van punten op een 2000x2000 scherm waarbij:
    - Punten willekeurig geplaatst worden.
    - Geen twee punten dichter bij elkaar staan dan min_distance.

    Parameters:
        width (int): Breedte van het canvas.
        height (int): Hoogte van het canvas.
        num_points (int): Aantal punten dat gegenereerd moet worden.
        min_distance (int): Minimale afstand tussen punten.

    Returns:
        list: Lijst met tuples van coördinaten (x, y).
    """
    points = []

    while len(points) < num_points:
        x = random.randint(0, width)
        y = random.randint(0, height)

        # Check of het nieuwe punt ver genoeg is van bestaande punten
        if all(math.dist((x, y), (px, py)) >= min_distance for px, py in points):
            points.append((x, y))

    return points


def getDataHeatmap(input):
    """
    De hoofdcode die verschillende functies aanroept om bedrijven op te halen, nieuwsartikelen te vinden,
    bedrijven te beoordelen en de resultaten te retourneren.

    Parameters:
        input (str): Een lijst van bedrijfsnamen (of sectoren) als invoer voor de analyse.

    Returns:
        list: Een lijst van tuples (bedrijf, artikel-URL, score).
    """
    companiesString = getCompanies(input)
    companiesList = makeListOfCompanies(companiesString)

    companies_str = companiesList[0].strip()

    print(companies_str)

    try:
        companies = json.loads(companies_str)
    except json.JSONDecodeError:
        print("Er is een fout opgetreden bij het omzetten van de bedrijvenlijst naar een lijst.")
        return []

    newsArticles = fetch_news(companies)

    if not newsArticles:
        print("Geen nieuwsartikelen gevonden.")
        return []

    ScoresString = newsArticlesToScore(newsArticles)

    almost = parse_scores_to_tuples(ScoresString, companies, newsArticles)

    result = extract_list_from_string(almost)

    length_result = len(result)
    points = generate_spread_points(num_points=length_result)

    # Maak de lijst van dicts met "x", "y", "value", "name" en "url"
    data = [
        {"x": x, "y": y, "value": int(value), "name": name, "url": url}
        for (name, url, value), (x, y) in zip(result, points)
    ]

    return data


print(getDataHeatmap('Volkswagen, Pirelli, Mercedes'))
