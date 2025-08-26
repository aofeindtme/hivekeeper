# generate_translations.py

import yaml
import os

CONFIG_PATH = "config/hivekeeper_entities.yaml"
TRANSLATIONS_PATH = "config/translations.yaml"

def generate():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    en = {}
    de = {}

    field_count = 0
    option_count = 0
    warning_count = 0

    for entity in config.get("entities", []):
        for field in entity.get("fields", []):
            key = field["name"]
            en[key] = key.replace("_", " ").capitalize()
            de[key] = key.replace("_", " ").capitalize() + " [DE]"
            field_count += 1

            if field.get("type") in ("dropdown", "select"):
                for opt in field.get("options", []):
                    if isinstance(opt, str):
                        en[opt] = opt
                        de[opt] = f"[{opt}]"
                        option_count += 1
                    elif isinstance(opt, dict):
                        en_val = opt.get("en", "MISSING")
                        de_val = opt.get("de", f"[{en_val}]")
                        en[str(en_val)] = str(en_val)
                        de[str(en_val)] = de_val
                        option_count += 1
                    elif isinstance(opt, (int, float)):
                        val = str(opt)
                        en[val] = val
                        de[val] = f"[{val}]"
                        option_count += 1
                    else:
                        print(f"⚠️  Unbekanntes Optionsformat in Feld '{key}': {opt}")
                        warning_count += 1

    # Add common interface keys
    ui_keys = {
        "add_colony_title": ("Add Colony", "Kolonie hinzufügen"),
        "logout": ("Logout", "Abmelden"),
        "save": ("Save", "Speichern"),
        "login": ("Login", "Anmelden"),
        "username": ("Username", "Benutzername"),
        "password": ("Password", "Passwort"),
        "submit": ("Submit", "Absenden"),
    }

    for key, (en_val, de_val) in ui_keys.items():
        en[key] = en_val
        de[key] = de_val

    with open(TRANSLATIONS_PATH, "w", encoding="utf-8") as out:
        yaml.dump({"en": en, "de": de}, out, allow_unicode=True, sort_keys=True)

    # CLI-Output
    print(f"✓ Translations generated:")
    print(f"  ├─ Fields:  {field_count}")
    print(f"  ├─ Options: {option_count}")
    print(f"  ├─ UI Keys: {len(ui_keys)}")
    print(f"  └─ Output:  {TRANSLATIONS_PATH}")
    if warning_count > 0:
        print(f"⚠️  {warning_count} ungewöhnliche Optionswerte wurden ignoriert.")

if __name__ == "__main__":
    generate()
