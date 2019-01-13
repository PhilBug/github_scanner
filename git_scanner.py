import requests
import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-list', nargs='+', help='list of keywords to search for (no quotes)', required=True)
parser.add_argument('-a', nargs=2, help='authenticate using github login and password')
parser.add_argument('-language', nargs='?', help='programming language used in project')

with open('config.yaml') as config_data:
    config = yaml.load(config_data)

args = parser.parse_args()

class Repository:
    def __init__(self, r_id, name, author, last_update, language):
        self.r_id = r_id
        self.name = name
        self.author = author
        self.last_update = last_update.replace('T', ' ').replace('Z', '')
        if language != None:
            self.language = language.lower()
        else:
            self.language = 'unknown'

class Scanner:
    def __init__(self):
        self.projects = []
        self.results = []
    
    def get_project_names(self, login, password):
        for user in config['users']:
            r = requests.get('http://api.github.com/users/{}/repos'.format(user),
                auth=(login, password)
            )
            for project in r.json():
                try:
                    name = project['name']
                    author = project['owner']['login']
                    last_update = project['updated_at']
                    r_id = project['id']
                    language = project['language']
                    repo = Repository(r_id, name, author, last_update, language)
                    self.projects.append(repo)
                except TypeError or AttributeError:
                    continue
        if len(self.projects) == 0:
            message = r.json()['message']
            print(message)


    def find_key_words(self, key_words, lang_search):
        ids = []
        for word in key_words:
            for repo in self.projects:
                if word.lower() in repo.name.lower() and repo.r_id not in ids:
                    ids.append(repo.r_id)
                    if lang_search:
                        if repo.language in args.language.lower():
                            self.results.append([repo.author, repo.name, repo.last_update])
                    else:
                        self.results.append([repo.author, repo.name, repo.last_update])


    def print_results(self, data=''):
        print('')
        if data == '': data = self.results
        col_width = max(len(word) for row in data for word in row) + 2
        for row in data:
            print('{}{}updated at: {}'.format(row[0].ljust(col_width), row[1].ljust(col_width), row[2].ljust(col_width)))

            



if __name__ == "__main__":
    if args.a == None:
        try:
            login = config['creds']['login']
            password = config['creds']['password']
        except KeyError as e:
            print('Please authenticate using "-a" or by adding the credentials to config.yaml.'), exit(1)
    else:
        login = args.a[0]
        password = args.a[1]

    lang_search = True if args.language != None else False

    scanner = Scanner()
    scanner.get_project_names(login, password)
    scanner.find_key_words(args.list, lang_search)
    scanner.print_results()
