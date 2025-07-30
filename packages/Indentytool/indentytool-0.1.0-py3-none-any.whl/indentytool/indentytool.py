import random
import datetime

class Indentytool:
    names = {
        'it': {
            'M': ['Luca', 'Marco', 'Giovanni', 'Francesco', 'Andrea', 'Matteo', 'Alessandro', 'Davide', 'Simone', 'Fabio',
                  'Stefano', 'Nicola', 'Paolo', 'Gabriele', 'Antonio', 'Roberto', 'Vincenzo', 'Claudio', 'Maurizio', 'Enrico',
                  'Riccardo', 'Daniele', 'Filippo', 'Emanuele', 'Carlo', 'Giuseppe', 'Alberto', 'Massimo', 'Luigi', 'Cesare'],
            'F': ['Maria', 'Giulia', 'Anna', 'Sara', 'Francesca', 'Chiara', 'Valentina', 'Elena', 'Martina', 'Laura',
                  'Alessandra', 'Federica', 'Simona', 'Cristina', 'Ilaria', 'Angela', 'Paola', 'Silvia', 'Veronica', 'Roberta',
                  'Monica', 'Elisa', 'Barbara', 'Claudia', 'Antonella', 'Sabrina', 'Beatrice', 'Lucia', 'Gabriella', 'Daniela'],
            'N': ['Andrea', 'Gabriele', 'Valerio', 'Lorenzo', 'Nicola', 'Francesco', 'Samuele', 'Dario', 'Edoardo', 'Alessio']
        },
        'fr': {
            'M': ['Jean', 'Pierre', 'Michel', 'Alain', 'Philippe', 'Jacques', 'Bernard', 'Louis', 'Claude', 'Henri',
                  'Nicolas', 'Daniel', 'Pascal', 'Yves', 'Frédéric', 'Didier', 'Thierry', 'Éric', 'Patrick', 'Bruno',
                  'Christian', 'Laurent', 'Gérard', 'Vincent', 'Dominique', 'Jean-Claude', 'Jean-Pierre', 'Marc', 'Olivier', 'René'],
            'F': ['Marie', 'Sophie', 'Claire', 'Isabelle', 'Nathalie', 'Catherine', 'Françoise', 'Christine', 'Laurence', 'Monique',
                  'Sandrine', 'Sylvie', 'Caroline', 'Véronique', 'Hélène', 'Dominique', 'Anne', 'Valérie', 'Martine', 'Michèle',
                  'Josiane', 'Élise', 'Brigitte', 'Corinne', 'Pascale', 'Chantal', 'Muriel', 'Agnès', 'Josette', 'Cécile'],
            'N': ['Morgan', 'Camille', 'Sacha', 'Alexis', 'Dominique', 'Claude', 'Charlie', 'Maxime', 'Michel', 'Célestin']
        },
        'uk': {
            'M': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Charles', 'Joseph', 'Thomas',
                  'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua',
                  'Kevin', 'Brian', 'George', 'Edward', 'Ronald', 'Timothy', 'Jason', 'Jeffrey', 'Ryan', 'Jacob'],
            'F': ['Mary', 'Patricia', 'Linda', 'Barbara', 'Elizabeth', 'Jennifer', 'Maria', 'Susan', 'Margaret', 'Dorothy',
                  'Lisa', 'Nancy', 'Karen', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon',
                  'Michelle', 'Laura', 'Sarah', 'Kimberly', 'Deborah', 'Jessica', 'Shirley', 'Cynthia', 'Angela', 'Melissa'],
            'N': ['Alex', 'Taylor', 'Jordan', 'Casey', 'Morgan', 'Jamie', 'Riley', 'Cameron', 'Dylan', 'Quinn']
        }
    }

    surnames = {
        'it': ['Rossi', 'Bianchi', 'Romano', 'Ferrari', 'Esposito', 'Ricci', 'Marino', 'Greco', 'Bruno', 'Gallo',
               'Conti', 'De Luca', 'Mancini', 'Costa', 'Giordano', 'Rizzo', 'Lombardi', 'Moretti', 'Barbieri', 'Fontana',
               'Santoro', 'Mariani', 'Rinaldi', 'Caruso', 'Ferrara', 'Guerra', 'Palumbo', 'Longo', 'Amato', 'Bianco'],
        'fr': ['Dubois', 'Moreau', 'Leroy', 'Roux', 'David', 'Bertrand', 'Morel', 'Fournier', 'Girard', 'Bonnet',
               'Dupont', 'Lambert', 'Fontaine', 'Chevalier', 'Faure', 'Blanc', 'Guerin', 'Muller', 'Henry', 'Rousseau',
               'Colin', 'Masson', 'Marchand', 'Dumas', 'Perrin', 'Poirier', 'Barbier', 'Leclerc', 'Renaud', 'Benoit'],
        'uk': ['Smith', 'Johnson', 'Brown', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin',
               'Thompson', 'Moore', 'Clark', 'Walker', 'Wright', 'Robinson', 'Green', 'Hall', 'Lewis', 'Young',
               'King', 'Scott', 'Hill', 'Adams', 'Baker', 'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts']
    }

    cities = {
        'it': [
            {'city': 'Roma', 'province': 'RM', 'cap': '00100'},
            {'city': 'Milano', 'province': 'MI', 'cap': '20100'},
            {'city': 'Napoli', 'province': 'NA', 'cap': '80100'},
            {'city': 'Torino', 'province': 'TO', 'cap': '10100'},
            {'city': 'Palermo', 'province': 'PA', 'cap': '90100'},
            {'city': 'Genova', 'province': 'GE', 'cap': '16100'},
            {'city': 'Bologna', 'province': 'BO', 'cap': '40100'},
            {'city': 'Firenze', 'province': 'FI', 'cap': '50100'},
            {'city': 'Bari', 'province': 'BA', 'cap': '70100'},
            {'city': 'Catania', 'province': 'CT', 'cap': '95100'},
            {'city': 'Verona', 'province': 'VR', 'cap': '37100'},
            {'city': 'Messina', 'province': 'ME', 'cap': '98100'},
            {'city': 'Padova', 'province': 'PD', 'cap': '35100'},
            {'city': 'Trieste', 'province': 'TS', 'cap': '34100'},
            {'city': 'Taranto', 'province': 'TA', 'cap': '74100'},
            {'city': 'Brescia', 'province': 'BS', 'cap': '25100'},
            {'city': 'Prato', 'province': 'PO', 'cap': '59100'},
            {'city': 'Parma', 'province': 'PR', 'cap': '43100'},
            {'city': 'Modena', 'province': 'MO', 'cap': '41100'},
            {'city': 'Reggio Calabria', 'province': 'RC', 'cap': '89100'}
        ],
        'fr': [
            {'city': 'Parigi', 'province': 'IDF', 'cap': '75000'},
            {'city': 'Marsiglia', 'province': 'PAC', 'cap': '13000'},
            {'city': 'Lione', 'province': 'ARA', 'cap': '69000'},
            {'city': 'Toulouse', 'province': 'OCC', 'cap': '31000'},
            {'city': 'Nizza', 'province': 'PAC', 'cap': '06000'},
            {'city': 'Nantes', 'province': 'PDC', 'cap': '44000'},
            {'city': 'Strasburgo', 'province': 'GRD', 'cap': '67000'},
            {'city': 'Montpellier', 'province': 'OCC', 'cap': '34000'},
            {'city': 'Bordeaux', 'province': 'NAQ', 'cap': '33000'},
            {'city': 'Lille', 'province': 'HDF', 'cap': '59000'},
            {'city': 'Rennes', 'province': 'BRE', 'cap': '35000'},
            {'city': 'Reims', 'province': 'GRA', 'cap': '51100'},
            {'city': 'Le Havre', 'province': 'NOR', 'cap': '76600'},
            {'city': 'Saint-Étienne', 'province': 'ARA', 'cap': '42000'},
            {'city': 'Toulon', 'province': 'PAC', 'cap': '83000'},
            {'city': 'Angers', 'province': 'PDC', 'cap': '49000'},
            {'city': 'Grenoble', 'province': 'ARA', 'cap': '38000'},
            {'city': 'Dijon', 'province': 'BFC', 'cap': '21000'},
            {'city': 'Nîmes', 'province': 'OCC', 'cap': '30000'},
            {'city': 'Aix-en-Provence', 'province': 'PAC', 'cap': '13100'}
        ],
        'uk': [
            {'city': 'Londra', 'province': 'LDN', 'cap': 'EC1A'},
            {'city': 'Manchester', 'province': 'MAN', 'cap': 'M1'},
            {'city': 'Birmingham', 'province': 'BIR', 'cap': 'B1'},
            {'city': 'Leeds', 'province': 'LDS', 'cap': 'LS1'},
            {'city': 'Glasgow', 'province': 'GLA', 'cap': 'G1'},
            {'city': 'Sheffield', 'province': 'SHF', 'cap': 'S1'},
            {'city': 'Liverpool', 'province': 'LIV', 'cap': 'L1'},
            {'city': 'Bristol', 'province': 'BRI', 'cap': 'BS1'},
            {'city': 'Newcastle', 'province': 'NCL', 'cap': 'NE1'},
            {'city': 'Sunderland', 'province': 'SUN', 'cap': 'SR1'},
            {'city': 'Nottingham', 'province': 'NTM', 'cap': 'NG1'},
            {'city': 'Southampton', 'province': 'SOU', 'cap': 'SO1'},
            {'city': 'Portsmouth', 'province': 'POR', 'cap': 'PO1'},
            {'city': 'Belfast', 'province': 'BEL', 'cap': 'BT1'},
            {'city': 'Cardiff', 'province': 'CRD', 'cap': 'CF10'},
            {'city': 'Coventry', 'province': 'COV', 'cap': 'CV1'},
            {'city': 'Leicester', 'province': 'LEI', 'cap': 'LE1'},
            {'city': 'Bradford', 'province': 'BRD', 'cap': 'BD1'},
            {'city': 'Hull', 'province': 'HUL', 'cap': 'HU1'},
            {'city': 'Stoke-on-Trent', 'province': 'STK', 'cap': 'ST1'}
        ]
    }

    email_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com', 'mail.com', 'protonmail.com', 'icloud.com', 'aol.com', 'gmx.com'
    ]

    phone_formats = {
        'it': '+39 {}{}{} {}{}{} {}{}{} {}{}{}',
        'fr': '+33 {} {} {} {} {}',
        'uk': '+44 {} {}{} {}{} {}{}',
    }

    common_passwords = [
        '123456', 'password', '123456789', '12345', '12345678', 'qwerty', 'abc123', 'football',
        'monkey', 'letmein', 'dragon', '111111', 'baseball', 'iloveyou', 'trustno1', '1234567'
    ]

    def __init__(self, country='it'):
        if country not in self.names:
            raise ValueError(f"Paese {country} non supportato")
        self.country = country

    def random_name(self, gender=None):
        if gender not in ['M', 'F', 'N']:
            gender = random.choice(['M', 'F', 'N'])
        nome = random.choice(self.names[self.country][gender])
        cognome = random.choice(self.surnames[self.country])
        return nome, cognome

    def random_email(self, nome, cognome):
        domain = random.choice(self.email_domains)
        number = random.randint(1, 9999)
        email = f"{nome.lower()}.{cognome.lower()}{number}@{domain}"
        return email

    def random_password(self, length=12):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        pw = ''.join(random.choice(chars) for _ in range(length))
        return pw

    def password_with_name_dob(self, nome, data_nascita):
        anno = data_nascita.split('-')[0]
        special_chars = ['!', '@', '#', '2023', '*', '?']
        pw = f"{nome.capitalize()}{anno}{random.choice(special_chars)}"
        return pw

    def common_password(self):
        return random.choice(self.common_passwords)

    def random_phone(self):
        fmt = self.phone_formats.get(self.country, '+00 {}{}{} {}{}{} {}{}{} {}{}{}')
        # Per semplicità prendo cifre random per il formato
        digits = [str(random.randint(0, 9)) for _ in range(fmt.count('{}'))]
        phone = fmt.format(*digits)
        return phone

    def random_date_of_birth(self, start_year=1950, end_year=2005):
        start_date = datetime.date(start_year, 1, 1)
        end_date = datetime.date(end_year, 12, 31)
        time_between = end_date - start_date
        days_between = time_between.days
        random_number_of_days = random.randint(0, days_between)
        dob = start_date + datetime.timedelta(days=random_number_of_days)
        return dob.isoformat()

    def random_city(self):
        city_info = random.choice(self.cities[self.country])
        return city_info['city'], city_info['province'], city_info['cap']

    def random_gender(self):
        return random.choice(['M', 'F', 'N'])

    def generate_identity(self):
        gender = self.random_gender()
        nome, cognome = self.random_name(gender)
        dob = self.random_date_of_birth()
        email = self.random_email(nome, cognome)
        phone = self.random_phone()
        city, province, cap = self.random_city()

        # Scelgo casualmente il tipo di password
        pw_type = random.choice(['random', 'name_dob', 'common'])
        if pw_type == 'random':
            password = self.random_password()
        elif pw_type == 'name_dob':
            password = self.password_with_name_dob(nome, dob)
        else:
            password = self.common_password()

        identity = {
            'nome': nome,
            'cognome': cognome,
            'sesso': gender,
            'data_nascita': dob,
            'email': email,
            'telefono': phone,
            'città': city,
            'provincia': province,
            'cap': cap,
            'password': password
        }
        return identity
    
    def random_cap(self):
       city_info = random.choice(self.cities[self.country])
       return city_info['cap']


# Esempio d'uso
if __name__ == "__main__":
    tool = Indentytool('it')
    for _ in range(3):
        print(tool.generate_identity())
