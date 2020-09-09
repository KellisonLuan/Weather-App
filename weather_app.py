import requests
import json
from datetime import date
import urllib
accuweatherAPIkey = "U2O1pTCi9MAsn3Nng11YxjDQJ7cEL3jg"
mapboxToken ="pk.eyJ1Ijoia2VsbGlzb25sdWFuIiwiYSI6ImNrOHB5bWN0MDBha2EzZ2x5OGI5Y3U0bTMifQ._BX2jCzRkB3TkId59ZnXgQ"
diasDaSemana = ['Domingo','Segunda-feira','Terça-Feira','Quarta-Feira','Quinta-Feira','Sexta-feira','Sabado']
def pegarCoordenadas():
    r = requests.get('http://www.geoplugin.net/json.gp')
    if (r.status_code != 200):
        print('Não foi possivel obter a localização')
        return None
    else:
        try:
            localização = json.loads(r.text)
            coordenadas ={}
            coordenadas['lat'] = localização['geoplugin_latitude']
            coordenadas['long']= localização['geoplugin_longitude']
            return coordenadas
        except:
            return None
def pegarCodigoLocal(lat,long):
    locatioAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey="+accuweatherAPIkey+"&q="+lat+"%2C"+long+"&language=pt-br"
    r = requests.get(locatioAPIUrl)
    if (r.status_code != 200):
        print('Não foi possivel obter o código do local')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal['nomeLocal'] = locationResponse['LocalizedName']+", "\
                        +locationResponse['AdministrativeArea']['LocalizedName']+", "\
                        +locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            return infoLocal
        except:
            return None
def pesquisarLocal(local):
    _local = urllib.parse.quote(local)
    mapboxGeocodeUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/"\
                       + _local + ".json?access_token=" + mapboxToken
    r = requests.get(mapboxGeocodeUrl)
    if (r.status_code != 200):
        print('Não foi possivel obter as coordenadas.')
        return None
    else:
        try:
            MapBoxResponse = json.loads(r.text)
            coordenadas = {}
            coordenadas['long'] = str(MapBoxResponse['features'][0]['geometry']['coordinates'][0])
            coordenadas['lat'] = str(MapBoxResponse['features'][0]['geometry']['coordinates'][1])
            return coordenadas
        except:
            print('Erro na pesquisa de local.')
def pegarTempoAgora(codigoLocal, nomeLocal):
    CurrentConditionsAPIurl = "http://dataservice.accuweather.com/currentconditions/v1/"\
                               +codigoLocal+"?apikey="+accuweatherAPIkey \
                              +"&language=pt-br"
    r = requests.get(CurrentConditionsAPIurl)
    if (r.status_code != 200):
        print('Não foi possivel obter o clima atual')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            infoClima = {}
            infoClima['textoClima'] = CurrentConditionsResponse[0]['WeatherText']
            infoClima['temperatura'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            infoClima['nomeLocal'] = nomeLocal
            return infoClima
        except:
            return None
def pegarPrevisão(codigoLocal):
    DailyAPIurl = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" \
                     +codigoLocal+"?apikey="+accuweatherAPIkey\
                     +"&language=pt-br&metric=true"
    r = requests.get(DailyAPIurl)
    if (r.status_code != 200):
        print('Não foi possivel obter a previsão')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoClima5Dias = []
            for dia in DailyResponse['DailyForecasts']:
                climaDia = {}
                climaDia['max'] = dia['Temperature']['Maximum']['Value']
                climaDia['min'] = dia['Temperature']['Minimum']['Value']
                climaDia['clima'] = dia['Day']['IconPhrase']
                diaSemana = int(date.fromtimestamp(dia['EpochDate']).strftime("%w"))
                climaDia['dia'] = diasDaSemana[diaSemana]
                infoClima5Dias.append(climaDia)
            return infoClima5Dias
        except:
            return None
def mostrarPrevisão(lat,long):
    try:
        local = pegarCodigoLocal(lat,long)
        climaAtual = pegarTempoAgora(local['codigoLocal'], local['nomeLocal'])
        print('Clima atual em: ' + climaAtual['nomeLocal'])
        print(climaAtual['textoClima'])
        print('Temperatura: ' + str(climaAtual['temperatura']) + '\xb0' + 'C')
    except:
        print('Erro ao obter o clima atual.')

    opção = input('\nDeseja ver a previsão para os próximos dias?(s ou n): ').lower()
    if opção == 's':
        print('\nClima para hoje e para os proximos dias:\n')
        try:
            previsão5dias = pegarPrevisão(local['codigoLocal'])
            for dia in previsão5dias:
                print(dia['dia'])
                print('Minima: ' + str(dia['min']) + '\xb0' + 'C')
                print('Maxima: ' + str(dia['max']) + '\xb0' + 'C')
                print('Clima: ' + dia['clima'])
                print('-------------------------------------------')
        except:
            print('Erro ao obter a previsão')
try:
    coordenadas = pegarCoordenadas()
    mostrarPrevisão(coordenadas['lat'],coordenadas['long'])
    continuar = 's'
    while continuar == 's':
        continuar = input("\nDeseja consultar a previsão de outro local? (s ou n): ").lower()
        if continuar != 's':
            break
        local = input('\nDigite a cidade e o estado: ')
        try:
            coordenadas = pesquisarLocal(local)
            mostrarPrevisão(coordenadas['lat'],coordenadas['long'])
        except:
            print('Não foi possivel obter a previsão para este local.')
except:
    print('Erro ao processar a solicitação. Entre em conta com o suporte.')