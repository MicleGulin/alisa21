from flask import Flask, request, jsonify
import logging
from geo import get_distance, get_geo_info

app = Flask(__name__)

names = {}

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        names[user_id] = {
            'name': None
        }

        return

    first_name = get_first_name(req)

    if names[user_id]['name'] is None:

        if first_name is None:
            res['response']['text'] = 'Не раслышала имя. Повтори!'
        else:
            names[user_id]['name'] = first_name
            res['response']['text'] = 'Приятно познакомиться, ' + first_name.title() + '. Я Алиса. ' \
                                                                                       'Я могу сказать в какой ' \
                                                                                       'стране город или сказать ' \
                                                                                       'расстояние между городами!'

    else:

        cities = get_cities(req)

        if len(cities) == 0:

            res['response']['text'] = names[user_id]['name'].title() + ', ты не написал название не одного города!'

        elif len(cities) == 1:

            res['response']['text'] = names[user_id]['name'].title() + ', этот город в стране - ' \
                                                                       '' + get_geo_info(cities[0], 'country')

        elif len(cities) == 2:

            distance = get_distance(get_geo_info(cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
            res['response']['text'] = names[user_id]['name'].title() + ', расстояние между этими ' \
                                                                       'городами: ' + str(round(distance)) + ' км.'

        else:

            res['response']['text'] = names[user_id]['name'].title() + ', слишком много городов!'


def get_cities(req):
    cities = []

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.GEO':

            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])

    return cities


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.FIO':

            if 'first_name' in entity['value'].keys():
                return entity['value']['first_name']
            else:
                return None
    return None


if __name__ == '__main__':
    app.run()
