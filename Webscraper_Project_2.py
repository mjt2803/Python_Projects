import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.wisdompetmed.com")

print(response.url)

print(response.status_code)

print(response.headers)

#print(response.content)

#print(response.text)

soup = BeautifulSoup(response.text)

print(soup.prettify())

soup.find("title")

soup.find_all("article")

print(soup.find("span", class_= "phone").text)

featured_testomonial = soup.find_all("div", class_= "quote")

for testomonial in featured_testomonial:
  print(testomonial.text)

staff = soup.find_all("div", class_= "info col-xs-8 col-xs-offset-2 col-sm-7 col-sm-offset-0 col-md-6 col-lg-8")

for s in staff:
  print(s.text)

links = soup.find_all("a")

for link in links:
  print(link.text, link.get("href"))

with open("wisdom_vet.txt", "w") as f:
  f.write(soup.prettify())

