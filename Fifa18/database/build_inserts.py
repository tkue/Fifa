file_clubs = 'schema/clubs.txt'
file_countries = 'schema/countries.txt'
file_leagues = 'schema/leagues.txt'


def get_sql(table_name: str, lines: []):
    sql = []

    for line in lines:
        sql.append('INSERT INTO `{}` (`Name`) VALUES(\'{}\');'.format(table_name, line.strip()))

    return sql

def write_file(input_file: str, output_file: str, table_name: str):
    lines = None

    with open(input_file, 'r') as f:
        lines = f.readlines()

    sql = get_sql(table_name, lines)

    with open(output_file, 'w+') as f:
        f.writelines('\n'.join(sql))



if __name__ == '__main__':
    write_file(file_clubs, 'schema/clubs.sql', 'Club')
    write_file(file_countries, 'schema/countries.sql', 'Country')
    write_file(file_leagues, 'schema/leagues.sql', 'League')



