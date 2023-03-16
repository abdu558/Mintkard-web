import requests,json


choice = input('Do you like cats or dogs or none?')

if choice == 'cats':
    response = requests.get("https://api.thecatapi.com/v1/images/search?limit=10")
    response = response.json()
    cats =[]
    for cat in response:
        cats.append(cat['url'])
    
    print(cats)

elif choice == 'dogs':
    response = requests.get("https://dog.ceo/api/breeds/image/random")#/10
    response = response.json()
    dogs =[response['message']]

    print(dogs)