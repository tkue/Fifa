import json

FILE = 'fut.json'

if __name__ == '__main__':

    clubs = []
    leagues = []
    countries = []

    lines = None
    with open(FILE) as f:
        lines = f.readlines()


    for i, line in enumerate(lines):
        if i == 0:
            continue

        print(i)

        j = None
        try:
            if line.startswith(','):
                j = json.loads(line[1:])
            else:
                j = json.loads(line)

            club_name = j['club']['name'].strip().lower()
            league_name = j['league']['name'].strip().lower()
            nation_name = j['nation']['name'].strip().lower()

            if club_name not in clubs:
                clubs.append(club_name)
            if league_name not in leagues:
                leagues.append(league_name)
            if nation_name not in countries:
                countries.append(nation_name)
        except Exception as e:
            print(i)
            print(e)

    with open('clubs.txt', 'w+') as f:
        for club in clubs:
            f.write('{0}{1}'.format(club, '\n'))

    with open('leagues.txt', 'w+') as f:
        for league in leagues:
            f.write('{0}{1}'.format(league, '\n'))

    with open('countries.txt', 'w+') as f:
        for country in countries:
            f.write('{0}{1}'.format(country, '\n'))


    # j = json.loads('\n'.join(lines))

    # for i, line in enumerate(lines):
    #     if i > 1:
    #         break
    #
    #     print(line)