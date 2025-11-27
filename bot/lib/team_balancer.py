import random

ADJECTIVES = [
    "Angry", "Brave", "Clever", "Daring", "Energetic", "Fearless", "Gentle",
    "Happy", "Incredible", "Jolly", "Keen", "Lively", "Mighty", "Noble",
    "Optimistic", "Powerful", "Quick", "Radical", "Smart", "Tough", "Unique",
    "Victorious", "Wild", "Xenial", "Young", "Zealous"
]

DOG_BREEDS = [
    "Husky", "Bulldog", "Poodle", "Beagle", "Labrador", "Retriever",
    "Shepherd", "Corgi", "Shiba", "Boxer", "Terrier", "Spaniel",
    "Rottweiler", "Doberman", "Pitbull", "Dalmatian", "Chihuahua", "Pug"
]

class TeamBalancer:
    @staticmethod
    def generate_team_name() -> str:
        adjective = random.choice(ADJECTIVES)
        breed = random.choice(DOG_BREEDS)
        return f"{adjective} {breed}s"
    
    @staticmethod
    def pick_captain(player_ids: list[int]) -> int:
        return random.choice(player_ids)
    
    @staticmethod
    def balance_teams(player_ids: list[int]) -> tuple[list[int], list[int]]:
        shuffled = player_ids.copy()
        random.shuffle(shuffled)
        mid = len(shuffled) // 2
        teams = shuffled[:mid], shuffled[mid:]
        print(f"Team 1:")
        for p in teams[0]:
            print(f" - {p}")
        print(f"Team 2:")
        for p in teams[1]:
            print(f" - {p}")
        return teams
