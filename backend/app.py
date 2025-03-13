from flask import Flask, render_template
import openai
import requests
import re


app = Flask(__name__)

openai.api_key = "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"

NEWSAPI_KEY = "76a4c8fd5723459fae6686716d8b270c"


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
    print(reply)

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
    if not newsMessages:
        print("Geen nieuwsberichten beschikbaar")
        return "Geen nieuwsberichten beschikbaar"

    prompt = ("Hey gpt, als input krijg je een bericht met allemaal nieuwsartikels van bedrijven."
              "Ik wil dat je voor elk bedrijf een score geeft van 0 tot 100 op basis van hoe hard"
              "de stock van dit bedrijf gaat dalen of stijgen. Heel hard dalen = 0 en heel hard"
              "stijgen = 100. Dit is de input:")

    # Voeg de nieuwsberichten toe als een string
    news_string = "\n".join(newsMessages)  # Voeg ze samen gescheiden door nieuwe regels
    print(f"Samengevoegde nieuwsberichten: {news_string}")  # Debugging output
    prompt += news_string

    # Verstuur de prompt naar GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        n=1,
        stop=None,
        max_tokens=100,
        temperature=0.5,
    )

    # Ontvang en verwerk het antwoord
    reply = response.choices[0].message.content.strip()

    return reply


def scoreToDict(scores):
    prompt = ("Hey gpt, als input krijg je een bericht met allemaal bedrijven en een score van"
              "0 tot en met 100 ik wil dat je EXACT een dict teruggeeft met daarin als key de bedrijf"
              "en daarbij steeds de waarde. Dit moet ENKEL een dictionary zijn want ik moet dit later"
              "nog gebruiken om informatie uit op te halen. Hier is de input:")
    prompt += scores

    # Verstuur de prompt naar GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.5,
    )

    # Ontvang en verwerk het antwoord
    reply = response['choices'][0]['message']['content'].strip()

    return reply

def main(input):
    companiesString = getCompanies(input)
    companiesList = makeListOfCompanies(companiesString)
    newsArticles = fetch_news(companiesList)
    ScoresString = newsArticlesToScore(newsArticles)
    ScoresDict = scoreToDict(ScoresString)
    return ScoresDict

print(main('tesla, volvo, opel'))
