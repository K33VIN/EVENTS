from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import json
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('inicio.html')

@app.route('/inicio')
def inicio():
    eventos = []
    return render_template('inicio.html', eventos=eventos)

@app.route('/acerca-de')
def acerca_de():
    return render_template('acerca_de.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/politica')
def politica():
    return render_template('politica.html')


@app.route('/buscador', methods=['POST'])
def buscador():
    name = request.form['nombreArtista']
    city = request.form.get('ciudad')
    country = request.form.get('pais')

    api_key = '9a3vA1iPd9GiWCMnWGP28Ggw55E8iOGQ'
    url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}&keyword={name}'

    if city:
        url += f'&city={city}'
    if country:
        url += f'&countryCode={country}'

    try:
        response = requests.get(url) #utiliza la biblioteca request
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Solicitud fallida con excepción: {e}')
        return redirect(url_for('not_found_error', error=e))

    data = json.loads(response.content)
    if '_embedded' not in data or 'events' not in data['_embedded']:
        print(f'Error: No se encontraron eventos para {name} en {city or country}')
        return redirect(url_for('not_found_error', error=f'No se encontraron eventos para {name} en {city or country}'))

    events = data['_embedded']['events']
    evento_data = [] # crea una lista vacia

    for event in events: # itera sobre cada elemento sobre la lista de eventos
        evento_dict = {} #sobre cada evento crea un diccionario vacio 
        evento_dict['nombre'] = event['name'] # asigna el valor del nombre del evento a la clave 'nombre'
        
        #nos aseguramos de que tenemos en embedeed info sobre los lugares de eventos
        if '_embedded' in event and 'venues' in event['_embedded']: # verifica si embedded tiene la clave venues
            venue = event['_embedded']['venues'][0]  # solo se está interesado en el primer lugar asociado al evento.
            if 'city' in venue and 'country' in venue:
                evento_dict['lugar'] = f"{venue['city']['name']}, {venue['country']['name']}"
            elif 'city' in venue:
                evento_dict['lugar'] = venue['city']['name']
            elif 'country' in venue:
                evento_dict['lugar'] = venue['country']['name']
            else:
                evento_dict['lugar'] = 'Lugar no disponible'
        else:
            evento_dict['lugar'] = 'Lugar no disponible'
        
        if 'dates' in event and 'start' in event['dates']:
            evento_dict['fecha'] = event['dates']['start'].get('localDate', 'Fecha no disponible')
        else:
            evento_dict['fecha'] = 'Fecha no disponible'
        
        if 'priceRanges' in event:
            price_range = event['priceRanges'][0]
            evento_dict['precio'] = f"{price_range['min']} - {price_range['max']} {price_range['currency']}"
        else:
            evento_dict['precio'] = 'Precio no disponible'

        evento_dict['link'] = event.get('url', '#')  # Agregar el enlace del evento al diccionario

        evento_data.append(evento_dict)

    return render_template('buscador.html', evento_data=evento_data, nombre_artista=name, ciudad=city, pais=country)


@app.route('/not_found_error')
def not_found_error():
    error = request.args.get('error')
    return render_template('error.html', error=error)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error=error), 404

# Comprobar si la API de Ticketmaster está funcionando y su formato
try:
    api_key = '9a3vA1iPd9GiWCMnWGP28Ggw55E8iOGQ'
    url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}&size=1'
    response = requests.get(url)
    response.raise_for_status()
    data = json.loads(response.content)
    # print(f"La API de Ticketmaster está funcionando. Formato de respuesta: {json.dumps(data, indent=2)}")
except requests.exceptions.RequestException as e:
    print(f'Error en la solicitud a la API de Ticketmaster: {e}')


# Printar el json para ver su estructura
print(json.dumps(data, indent=4))


if __name__ == '__main__':
    app.run()