from dataclasses import dataclass
import re
import requests
from bs4 import BeautifulSoup, Tag

def get_meal_plan_str(url: str, showAllergies: bool) -> str:
    raw_website = __get_raw_website(url)
    divs = __get_meal_plan_divs(raw_website)
    meal_plan = __parse_meal_plan(divs, showAllergies)
    return "\n\n".join(map(str, meal_plan))

def icon_help() -> str:
    return """
    Icons:
        ⭐ = Bessere Tierhaltung
        🐟 = Fisch/Meeresfrüchte
        🐔 = Geflügel
        🐑 = Lamm
        🐄 = Rind
        🐖 = Schwein
        🌿 = Vegan
        🥕 = Vegetarisch
        🦌 = Wild
    """

@dataclass
class Meal:
    category: str
    category_icons: str
    icons: str
    description: str
    cost: str
    
    def __str__(self) -> str:
        return f"{self.category_icons} *{self.category}* {self.icons} ```{self.cost}```\n- {self.description}"

def __get_raw_website(url: str) -> str:
    '''
    This function takes a URL as an argument and sends a GET request to that URL.
    It then returns the HTML content of the webpage as a string.

    Parameters:
    url (str): The URL of the webpage to fetch.

    Returns:
    str: The HTML content of the webpage as a string.
'''
    return requests.get(url).text


def __get_meal_plan_divs(html: str) -> list[Tag]:
    '''
    This function takes a string of HTML content and parses it to extract the meal plan divs.

    Parameters:
    html (str): The HTML content to parse.
    
    Returns:
    list[Tag]: A list of divs with class 'speiseplanTagKat'.
    '''
    return BeautifulSoup(html, 'html.parser').find('div', {'class': 'contents_aktiv'}).find_all('div', {'class': 'speiseplanTagKat'})

def __parse_meal_plan(meal_plan_divs: list[Tag], showAllergies: bool) -> list[Meal]:
    '''
    This function takes a list of Tag objects and parses them to extract the meal plan.

    Parameters:
    meal_plan_divs (list[Tag]): The list of Tag objects to parse.
    showAllergies (bool): A flag indicating whether to show allergies in the meal plan.

    Returns:
    list[Meal]: A list of Meal objects.
    '''
    return list(filter(None, map(lambda m: __parse_meal_plan_div(m, showAllergies), meal_plan_divs)))



def __parse_meal_plan_div(meal_plan_div: Tag, showAllergies: bool) -> Meal:
    '''
    This function takes a Tag object representing a meal plan div and parses it to extract the Meal.

    Parameters:
    meal_plan_div (Tag): The Tag object to parse.
    showAllergies (bool): A flag indicating whether to show allergies in the meal description.

    Returns:
    Meal: A Meal object representing the parsed meal plan div.
    '''
    category_div = meal_plan_div.find('div', {'class': 'category'})
    title_div = meal_plan_div.find('div', {'class': 'title'})
    costs_div = meal_plan_div.find('div', {'class': 'preise'})
    title2_div = meal_plan_div.find('div', {'class': 'title_preise_2'})
    icon_divs = title2_div.find_all('div', {'class': 'speiseplanTagKatIcon'})
    category =  category_div.text
    category_icons = __parse_category(category_div.text)
    icons = __parse_icons(icon_divs)
    description = __parse_description(title_div.text, showAllergies)
    cost = __parse_cost(costs_div.text)

    return Meal(category, category_icons, icons, description, cost)

def __parse_cost(costs: str) -> str:
    big = re.search(r'Groß: \d+,?\d+', costs)
    small = re.search(r'Klein: \d+,?\d+', costs)
    if big and small:
        return "\n" + big.group(0) + "€ | " + small.group(0) + "€"
    return re.search(r'\d+,?\d+', costs).group(0) + "€"
    
def __parse_category(category: str) -> str:
    match category:
        case "Seezeit-Teller": return "🌊🕚"
        case "hin&weg": return "💨"
        case "KombinierBar": return "🖇️"
        case "Beilagen": return "🥗"
        case "Pasta": return "🍝"
        case "Pasta vegetarisch": return "🍝"
        case _: return ""

def __parse_icons(icon_divs: list[Tag]) -> str:
    icons = []
    classes = list(map(lambda icon_div: icon_div.attrs['class'].pop(), icon_divs))
    for _class in classes: 
        match _class:
            case "B": icons.append("⭐")
            case "F": icons.append("🐟")
            case "G": icons.append("🐔")
            case "L": icons.append("🐑")
            case "R": icons.append("🐄")
            case "Sch": icons.append("🐖")
            case "Vegan": icons.append("🌿")
            case "Veg": icons.append("🥕")
            case "W": icons.append("🦌")
    return " ".join(icons)

def __parse_description(description: str, showAllergies: bool) -> str:
    matches = re.findall(r'\((?:\d+[a-z]*,?)*\)', description)
    for match in matches:
        description = description.replace(match, f'```{match}```' if showAllergies else '')
    return description.replace(" |", "\n-")

