
from bs4 import BeautifulSoup
with open("Racenet_files/Racenet.html", "r") as f:
    html_doc=f.read()
soup=BeautifulSoup(html_doc,'html.parser')
print(soup.find_all('h4', class_='selection-result__info-competitor-name'))

