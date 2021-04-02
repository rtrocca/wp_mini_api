import base64
from slugify import slugify

import json
import requests
import io

def get_base_api_url():
    return site + '/wp-json/wp/v2/'

def get_categories_api_url():
    return get_base_api_url() + 'categories'

def get_tags_api_url():
    return get_base_api_url() + 'tags'

def get_posts_api_url():
    return get_base_api_url() + 'posts'

class WP_Site:
    def __init__(self, user_name, user_password, site):
        self.__user_name = user_name
        self.__user_password = user_password
        self.__site = site
        self.__headers = self.__make_headers()
        self.__base_api_url = self.__site + '/wp-json/wp/v2/'
        self.__posts_url = self.__base_api_url + 'posts'
        self.__tags_url = self.__base_api_url + 'tags'
        self.__categories_url = self.__base_api_url + 'categories'
        self.__media_url = self.__base_api_url + 'media'

    def __make_auth_header(self):
        user = base64.standard_b64encode((self.__user_name + ':' + self.__user_password).encode('utf-8'))
        auth_header = 'Basic ' + user.decode('utf-8')
        return auth_header

    def __make_headers(self):
        auth_header = self.__make_auth_header()
        headers = {
            'User-Agent': 'curl/7.55.1',
            'Accept': '*/*',
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }

        return headers

    def get_tags_api_url(self):
        return self.__tags_url

    def get_categories_api_url(self):
        return self.__categories_url

    def get_posts_api_url(self):
        return self.__posts_url

    def get_media_api_url(self):
        return self.__media_url

    def get_headers(self):
        return self.__headers

    def get_post(self, id, fields=['id', 'meta', 'title']):
        params = [('_fields', ','.join(fields))]
        #print(params)
        r = requests.get(self.__posts_url + '/' + str(id), params=params, headers=self.__headers)
        post = json.loads(r.text)
        return post

    def get_posts(self, fields = ['id', 'meta', 'title'], limit=100, **filters):
        params = []
        params.append(('per_page', limit))
        if len(fields) > 0:
            params.append(('_fields', ','.join(fields)))

        params = params + list(filters.items())

        #print('Request params', params)

        r = requests.get(self.__posts_url, params=params, headers=self.__headers)
        #print(r.status_code)
        #print(r.text)
        posts = json.loads(r.text)
        return posts

    def update_post(self, id, update):
        r = requests.put(self.__posts_url + '/' + str(id), json=update, headers=self.__headers)
        return r.ok

    def save_post(self, post_data):
        r = requests.post(self.__posts_url, json=post_data, headers=self.__headers)
        return r

    def get_by_slug(self, slug, fields=['id'], limit=1):
        return self.get_posts(fields=fields, limit=limit, slug=slug, status='draft,publish')

    def set_categories(self, categories_dict):
        ''' Create categories on the WordPress site

        Parameters
        ----------

        categories_dict dictionary whose keys become the site categories
        
        ''' 
        url = self.get_categories_api_url()
        headers = self.get_headers()
        pairs = []
        #pairs = [(category, slugify(category)) for category in categories_dict.keys()]
        for category in categories_dict.keys():
            pairs.append((category, slugify(category)))

        for (key,value) in pairs:
            print(key, ' -> ',value)
            data = { 'name': key, 'slug': value, 'description': key + ' collects articles about ' + ( ', '.join(categories_dict[key]))}
            r = requests.post(url, json=data, headers=headers)
            print(r.text)

    def get_categories_raw(self):
        url = self.get_categories_api_url()
        headers = self.get_headers()
        response = requests.get(url + '?per_page=100', headers=headers)
        if response.status_code == 200:
            categories = json.loads(response.text)
            return categories
        else:
            print('Error, status_code:', response.status_code, response.text)
            return None

    def get_categories(self):
        categories = self.get_categories_raw()
        if categories is not None:
            categories_dict = {}
            for category in categories:
                #categories_dict[category['slug'].replace('-', ' ')] = category['id']
                categories_dict[category['name']] = category['id']
            return categories_dict
        return None

    def get_categories_ids(self):
        categories = self.get_categories_raw()
        if categories is not None:
            categories_dict = {}
            categories_dict = {}
            for category in categories:
                categories_dict[category['id']] = category['name']

            return categories_dict
        else:
            return None

    def set_tags(self, tags):
        ''' Create tags on the WordPress site

        Parameters
        ----------

        tags array of strings that will become the site tags
        '''
        
        url = self.get_tags_api_url()
        headers = self.get_headers()
        pairs = []
        for keyword in keywords_dict.keys():
            value = keywords_dict[keyword]
            print(keyword)
            if type(value) == list:
                value = value[0]
            pairs.append((keyword, slugify(value)))

        for (key,value) in pairs:
            print(key, ' -> ',value)
            data = { 'name': key, 'slug': value}
            r = requests.post(url, json=data, headers=headers)
            print(r.text)

    def get_tags_raw(self):
        url = self.get_tags_api_url()
        headers = self.get_headers()
        response = requests.get(url + '?per_page=100', headers=headers)
        if response.status_code == 200:
            tags = json.loads(response.text)
            return tags
        return None

    def get_tags(self):
        tags = self.get_tags_raw()
        if tags is not None:
            tags_dict = {}
            for tag in tags:
                tags_dict[tag['slug'].replace('-', ' ')] = tag['id']

            return tags_dict
        else:
            return None

    def get_tags_ids(self):
        tags = self.get_tags_raw()
        if tags is not None:
            tags_dict = {}
            for tag in tags:
                tags_dict[tag['id']] = tag['slug'].replace('-', ' ')

            return tags_dict
        else:
            return None


    def post_image(self, fileData):
        #headers={ 'Content-Type': 'image/jpg','Content-Disposition' : 'attachment; filename=%s'% fileName},
        # this function will modify the headers dict
        headers = self.__make_headers()
        headers['Content-Type'] = 'image/jpg'
        headers['Content-Disposition'] = 'attachment; filename=%s'% 'test.jpg'
        media_url = self.get_media_api_url()
        r = requests.post(media_url, data=io.BytesIO(fileData),headers=headers)
        return r

if __name__ == '__main__':
    wp_site = WP_Site(user_name, user_password, site)
    print('Tags:')
    print(wp_site.get_tags())
    print('\r\nCategories:')
    print(wp_site.get_categories())
    #print(wp_site.get_posts(limit=1))

#%%print('ciao')

# %%
