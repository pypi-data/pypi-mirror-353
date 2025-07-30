# Indentytool 🧠

Indentytool is a lightweight and versatile Python library for generating realistic fake identities, perfect for testing, social bots, behavioral analysis, or populating datasets.  
It supports generating names, surnames, emails, passwords, phone numbers, postal codes (CAP), provinces, cities, dates of birth, and much more for multiple countries including Italy, Europe, and worldwide.

---

## Key Features

- Generate realistic male, female, and neutral gender first and last names  
- Create emails consistent with the generated name and surname  
- Generate passwords in three modes: random, based on name+birthdate, or from a list of common passwords  
- Produce phone numbers with realistic formats for different countries  
- Generate random birth dates within configurable ranges  
- Provide realistic cities, provinces, and postal codes based on an integrated database (Italy and other countries)  
- Multi-country support (e.g., `'it'` for Italy, `'fr'` for France, `'uk'` for United Kingdom)  
- Easy to use and integrate into testing or simulation projects

---

## Installation

Currently, the library is not published on PyPI, so you can install it by cloning the repository or downloading the `indentytool.py` file:

```bash
git clone https://github.com/yourusername/indentytool.git
cd indentytool
pip install -r requirements.txt  # If there are dependencies (currently none)
```

Alternatively, just copy the `indentytool.py` file into your project folder.

---

## Usage

### Import and create an instance

```python
from indentytool import Indentytool

# Select country code (e.g., 'it' for Italy, 'fr' for France, 'uk' for United Kingdom)
tool = Indentytool('it')
```

### Generate a full identity

```python
identity = tool.generate_identity()
print(identity)
```

Example output:

```json
{
  "nome": "Marco",
  "cognome": "Rossi",
  "sesso": "M",
  "data_nascita": "1985-07-23",
  "email": "marco.rossi@example.com",
  "telefono": "+39 345 123 4567",
  "città": "Milano",
  "provincia": "MI",
  "cap": "20100",
  "password": "Marco1985!"
}
```

### Generate individual elements

```python
# Random city
city, province, cap = tool.random_city()
print(city, province, cap)

# Random name and surname
nome, cognome = tool.random_name('F')
print(nome, cognome)

# Random email based on name and surname
email = tool.random_email(nome, cognome)
print(email)

# Random password
password = tool.random_password()
print(password)

# Password based on name and date of birth
password2 = tool.password_with_name_dob(nome, "1990-05-15")
print(password2)

# Common password from list
common_pw = tool.common_password()
print(common_pw)

# Random phone number
phone = tool.random_phone()
print(phone)

# Random date of birth
dob = tool.random_date_of_birth()
print(dob)
```

---

## Example CLI script (`app.py`)

You can use this script to quickly test the library:

```python
from indentytool import Indentytool
import json

def main():
    tool = Indentytool('it')
    for i in range(5):
        identity = tool.generate_identity()
        print(f"Identity #{i+1}:")
        for k, v in identity.items():
            print(f"  {k}: {v}")
        # Save to JSON file
        with open(f"identity_{i+1}.json", "w", encoding="utf-8") as f:
            json.dump(identity, f, ensure_ascii=False, indent=4)
        print(f"Saved to identity_{i+1}.json\n")

if __name__ == "__main__":
    main()
```

---

## Customization

- Change country by passing the appropriate code in the class constructor, e.g., `tool = Indentytool('fr')` for France  
- Modify date ranges or phone formats by editing constants in the code  
- Extend the databases (names, cities) by adding more data to the dictionaries in the source code

---

## Internal workings and file size considerations

- The library is a pure Python file containing large internal datasets for names, cities, provinces, postal codes, etc.  
- Typical `.py` file size ranges from about 100 KB up to a few hundred KB depending on dataset size  
- When Python runs or imports the library, it compiles the `.py` into `.pyc` bytecode files stored in `__pycache__`. These `.pyc` files are binary optimized versions usually similar in size to the `.py`  
- No external dependencies or compiled modules means lightweight footprint  
- If you integrate heavy dependencies like cryptography libraries, the size can increase by several MB due to native compiled code

---

## Planned future features

- Wider country support with larger and more accurate datasets worldwide  
- Export methods for datasets in CSV, JSON, or database formats  
- Optional integration with lightweight encryption libraries for data protection  
- More advanced customization and user-defined templates

---

## License

MIT License © 2025 — Created by [Your Name]

---

## Contributing

Feel free to open issues or submit pull requests on GitHub to improve the library or add features.

---

Thank you for choosing **Indentytool**! 🧠
