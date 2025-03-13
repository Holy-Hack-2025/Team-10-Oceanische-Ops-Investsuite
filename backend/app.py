from flask import Flask, render_template
import openai
import requests
import json
import re
import ast

app = Flask(__name__)

openai.api_key = ("sk-proj--jkPAXjUhF4XzDF-bq8rm5FnWraBVq6DFuB53FJLNMYCx_MF4VGO1f_KLu0splZrC2muFEWakFT3"
                  "BlbkFJntA8k8TR_3AleSc-V2qaJ-5zrvQ3xSxoDyr3ixRakueaO_I_9Ob109m-xH4rb4Y62AsdDpCD8A")

NEWSAPI_KEY = "63a1e94e1fed45f3b24062495b1bd58c"


def fetch_news(keywords, language="en", page_size=3):
    all_articles = []

    for keyword in keywords:
        query = keyword  # Gebruik elk keyword afzonderlijk
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
            all_articles.extend(articles)  # Voeg de opgehaalde artikelen toe aan de lijst
            print(f"Opgehaalde artikelen voor '{keyword}': {articles}")
        else:
            print(f"Geen artikelen gevonden voor '{keyword}' of er is een fout bij het ophalen.")

    return all_articles


def getCompanies(message):
    prompt = ("Hey gpt, als input krijg je een aantal bedrijven of een bepaalde sector. Indien je enkel"
              "bedrijven krijgt moet je zelf afleiden over welke sector het gaat en geef je de belangrijkste"
              "bedrijven terug in deze sector waarin geïnvesteerd kan worden. Hier is de input: ")
    prompt += message

    # Verstuur de prompt naar GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )

    # Ontvang en verwerk het antwoord
    reply = response['choices'][0]['message']['content'].strip()

    return reply


def makeListOfCompanies(message):
    prompt = ("Hey gpt, als input krijg je een bericht waarin allemaal bedrijven gaan staan. Ik wil dat"
              "je ENKEL een lijst teruggeeft met deze bedrijven in en misschien ook de sector indien relevant"
              "Dit mag enkel een lijst zijn omdat ik deze respons ga gebruiken in een andere functie waar"
              "ze een lijst verwachten. Hier is de input:")
    prompt += message

    # Verstuur de prompt naar GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.5,
    )

    # Ontvang en verwerk het antwoord
    reply = response['choices'][0]['message']['content'].strip().split("\n")

    return reply


def newsArticlesToScore(newsMessages):
    # Haal de relevante informatie uit de nieuwsartikelen (bijvoorbeeld de titel en beschrijving)
    news_strings = [
        f"Title: {article['title']}\nDescription: {article['description']}" for article in newsMessages
    ]

    # Combineer deze string-lijst in één string, gescheiden door een nieuwe regel
    news_string = "\n\n".join(news_strings)  # Voeg ze samen met extra spaties tussen de artikelen

    # Verstuur de string naar GPT voor verdere verwerking
    prompt = f"Hey GPT, hier is een verzameling nieuwsartikelen:\n{news_string}\n\n" \
             "Beoordeel elk bedrijf op basis van deze artikelen. Geef een score tussen 0 en 100 voor elk bedrijf" \
             " en geef de naam van het bedrijf gevolgd door de score als volgt: 'Tesla Inc.': 75."

    # Verstuur de prompt naar GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        n=1,
        stop=None,
        max_tokens=200,
        temperature=0.5,
    )

    # Ontvang en verwerk het antwoord
    reply = response.choices[0].message.content.strip()

    return reply


def parse_scores_to_tuples(scores_string, companies, news_articles):
    # Verstuur de string naar GPT voor verdere verwerking
    prompt = (f"Hey GPT, hier is een verzameling scores van bedrijven:\n{scores_string}\n\n"
              "Ik wil exact een lijst terugkrijgen van tuples van lengte 3, in deze tuple moet op"
              "de eerste positie de naam van het bedrijf komen, daarna de link naar het artikel"
              "en ten slotte de juiste score. Belangrijk dat dit ENKEL een lijst is zodat ik hier"
              "later nog verder mee kan werken!!!"

              "\n\nDe artikelen die je kunt gebruiken zijn:\n"
              f"{news_articles}\n\n"
              f"Bedrijven die betrokken zijn:\n{companies}")

    # Verstuur de prompt naar GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        n=1,
        stop=None,
        max_tokens=500,  # Aangepast om meer tekst te kunnen verwerken
        temperature=0.5,
    )

    # Ontvang en verwerk het antwoord
    reply = response.choices[0].message.content.strip()

    return reply


def extract_list_from_string(input_string):
    # Zoek de lijst van tuples in de string met behulp van reguliere expressies
    # Hier nemen we aan dat de lijst zich altijd na "Hier is de lijst van tuples" bevindt
    start_index = input_string.find("[")
    end_index = input_string.find("]") + 1

    if start_index != -1 and end_index != -1:
        # Haal de substring die de lijst bevat
        list_string = input_string[start_index:end_index]

        try:
            # Zet de lijst van strings om naar een echte Python lijst
            extracted_list = ast.literal_eval(list_string)  # Veilige manier om de lijst van tuples te evalueren
            return extracted_list
        except Exception as e:
            print(f"Er is een fout opgetreden bij het verwerken van de lijst: {e}")
            return []
    else:
        print("Er werd geen lijst gevonden in de string.")
        return []



def main(input):
    # Verkrijg de lijst van bedrijven van GPT
    companiesString = getCompanies(input)

    # Maak een lijst van bedrijven uit de string die we terugkrijgen
    companiesList = makeListOfCompanies(companiesString)

    # Hier nemen we de eerste waarde uit de lijst (aangezien makeListOfCompanies een lijst van strings retourneert)
    companies_str = companiesList[0].strip()  # Verwijder eventuele extra spaties

    print(companies_str)

    try:
        # Converteer de string naar een echte lijst van bedrijven
        companies = json.loads(companies_str)
    except json.JSONDecodeError:
        print("Er is een fout opgetreden bij het omzetten van de bedrijvenlijst naar een lijst.")
        return []

    # Haal de nieuwsartikelen op voor de bedrijven
    newsArticles = fetch_news(companies)


    # Als er geen nieuwsartikelen zijn, retourneer een lege lijst of een passende foutmelding
    if not newsArticles:
        print("Geen nieuwsartikelen gevonden.")
        return []

    # Genereer de scores gebaseerd op de nieuwsartikelen
    ScoresString = newsArticlesToScore(newsArticles)


    # Zet de scores om in een lijst van tuples (bedrijf, url, score)
    almost = parse_scores_to_tuples(ScoresString, companies, newsArticles)

    result = extract_list_from_string(almost)

    return result


print(main('tesla, volvo, opel'))
