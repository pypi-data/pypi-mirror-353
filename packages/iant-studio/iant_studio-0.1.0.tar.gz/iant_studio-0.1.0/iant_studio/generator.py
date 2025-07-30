import random

prefixes = ["Smart", "Hyper", "Neo", "Eco", "Meta", "Quick", "Cyber", "Open", "Ultra"]
suffixes = ["Flow", "Lab", "Hive", "Works", "Base", "Space", "Wave", "Verse", "Bridge"]

def generate_name():
    return f"{random.choice(prefixes)}{random.choice(suffixes)}"
