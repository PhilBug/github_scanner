import requests
import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l', nargs='+', help='list of keywords to search for (no quotes)', required=True)
parser.add_argument('-a', nargs=2, help='authenticate using github login and password')

args = parser.parse_args()
projects_dict = {}

with open('config.yaml') as config_data:
    config = yaml.load(config_data)

if args.a == None:
    try:
        login = config['creds']['login']
        password = config['creds']['password']
    except KeyError as e:
        print('Please authenticate using "-a" or by adding the credentials to config.yaml.'), exit(1)
else:
    login = args.a[0]
    password = args.a[1]


def get_projects_names(users):
    for user in users:
        r = requests.get('http://api.github.com/users/{}/repos'.format(user),
            auth=(login, password)
        )
        for project in r.json():
            try:
                name = project['name']
                author = project['owner']['login']
            except TypeError:
                continue
                
            if author not in projects_dict:
                projects_dict[author] = []
            projects_dict[author].append(name)

    if len(projects_dict.items()) == 0:
        message = r.json()['message']
        print(message)
        # if 'limit exceeded' in message.lower():
        #     print('This script handles authanticating (see -h)')


def find_in_projects(key_words):
    for word in key_words:
        for key, value in projects_dict.items():
            for proj in value:
                if word.lower() in proj.lower():
                    print(
                        '{}: {}'.format(key, proj)
                    )

if __name__ == "__main__":
    # fill dictionary with data
    get_projects_names(config['users'])
    # search all data for keywords
    find_in_projects(args.l)