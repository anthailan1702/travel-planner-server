import json
import os
import time
import threading

from app.api import FoursquareAPI, GooglePlaceAPI, FacebookAPI
from app.constants import Service


class APIDispatcher:
    foursquare_api = FoursquareAPI()
    google_api = GooglePlaceAPI()
    facebook_api = FacebookAPI()

    def __init__(self, args):
        self.args = args
        self.results = {
            Service.FOURSQUARE: [],
            Service.FACEBOOK: [],
            Service.GOOGLE: []
        }

    def dispatch_api_calls(self):
        threads = [
            threading.Thread(target=self._query_from_google),
            threading.Thread(target=self._query_from_facebook),
            threading.Thread(target=self._query_from_foursquare),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return self.results

    def _query_from_facebook(self):
        after = None
        results = []
        params = self.args.get(Service.FACEBOOK)
        if len(params.get('categories')) > 0:
            for category in params.get('categories'):
                category = '["{}"]'.format(category)
                params['categories'] = category
                while True:
                    params['after'] = after
                    params['fields'] = 'id,about,description,name,location,phone,picture,website,overall_star_rating,' \
                                       'category_list,checkins'
                    res = self.facebook_api.find_places(params=params)
                    data = res.json().get('data')
                    if data:
                        for item in data:
                            item['unified_type'] = category
                        results.extend(data)
                    paging = res.json().get('paging')
                    if paging:
                        after = paging['cursors'].get('after')
                        if after is None:
                            break
                    else:
                        break
        else:
            while True:
                params['after'] = after
                params['fields'] = 'id,about,description,name,location,phone,picture,website,overall_star_rating,' \
                                   'category_list,checkins'
                res = self.facebook_api.find_places(params=params)
                data = res.json().get('data')
                if data:
                    results.extend(data)
                paging = res.json().get('paging')
                if paging:
                    after = paging['cursors'].get('after')
                    if after is None:
                        break
                else:
                    break
        self.results[Service.FACEBOOK] = results

    def _query_from_google(self):
        results = []
        params = self.args.get(Service.GOOGLE)
        if len(params.get('types')) > 0:
            types = params.pop('types')
            for type in types:
                pagetoken = None
                while True:
                    params['pagetoken'] = pagetoken
                    params['type'] = type
                    res = self.google_api.nearby_search(params=params)
                    pagetoken = res.json().get('next_page_token')
                    items = res.json()['results']
                    for item in items:
                        item['unified_type'] = type
                    results.extend(items)
                    time.sleep(2)
                    if pagetoken is None:
                        break
        else:
            pagetoken = None
            while True:
                params['pagetoken'] = pagetoken
                res = self.google_api.nearby_search(params=params)
                pagetoken = res.json().get('next_page_token')
                results.extend(res.json()['results'])
                time.sleep(2)
                if pagetoken is None:
                    break
        self.results[Service.GOOGLE] = results

    def _query_from_foursquare(self):
        results = []
        params = self.args.get(Service.FOURSQUARE)
        if len(params.get('sections')) > 0:
            sections = params.pop('sections')
            for section in sections:
                temp_results = []
                total_results = 1000000
                last_length = 0
                while len(temp_results) < total_results:
                    params['limit'] = 50
                    params['offset'] = len(temp_results)
                    params['section'] = section
                    res = self.foursquare_api.search_venues(params=params)
                    items = res.json()['response']['groups'][0]['items']
                    for item in items:
                        item['unified_type'] = section
                    temp_results.extend(items)
                    total_results = res.json()['response']['totalResults']
                    if len(temp_results) == last_length:
                        break
                    last_length = len(temp_results)
                results.extend(temp_results)
        else:
            total_results = 1000000
            last_length = 0
            while len(results) < total_results:
                params['limit'] = 50
                params['offset'] = len(results)
                res = self.foursquare_api.search_venues(params=params)
                results.extend(res.json()['response']['groups'][0]['items'])
                total_results = res.json()['response']['totalResults']
                if len(results) == last_length:
                    break
                last_length = len(results)
        self.results[Service.FOURSQUARE] = results
