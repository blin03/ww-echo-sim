import random
from echo import Echo

class TacetField:
    acceptable = {
        1: ['HP%'],
        3: ['Aero%']
    }

    costs = {
        1: 0.2,
        3: 0.8
    }

    sets = {
        'Correct': 0.5,
        'Incorrect': 0.5
    }

    mainstats = {
        1: ['ATK%', 'DEF%', 'HP%'],
        3: ['Spectro%', 'Electro%', 'Aero%', 'Glacio%', 'Fusion%', 'Havoc%', 'ATK%', 'DEF%', 'HP%', 'Energy Regen%'],
    }

    mainstat_probs = {
        1: [0.33, 0.33, 0.33],
        3: [12.66, 12.66, 12.66, 12.66, 12.66, 12.66, 6.0, 6.0, 6.0, 6.0],
    }

    def __init__(self, iterations=1) -> None:
        self.drops = []
        self.total_echoes_generated = {
            1: 0,
            3: 0
        }
        for _ in range(iterations):
            self.run()

        return

    def run(self) -> None:
        self.drops = []
        if random.random() <= 0.3:
            for _ in range(5):
                e = self.drop_one()
                self.drops.append(e)

        else:
            for _ in range(4):
                e = self.drop_one()
                self.drops.append(e)

        return
        
    def drop_one(self) -> Echo:
        cost = random.choices(list(self.costs.keys()), weights=list(self.costs.values()), k=1)[0]
        mainstat = random.choices(self.mainstats[cost], weights=self.mainstat_probs[cost], k=1)[0]
        set = random.choices(list(self.sets.keys()), weights=list(self.sets.values()), k=1)[0]
        self.total_echoes_generated[cost] += 1
        return Echo(mainstat=mainstat, cost=cost, set=set)

    def __str__(self) -> str:
        rep = ""
        for e in self.drops:
            rep += f"{str(e)}\n\n"

        return rep
    
if __name__ == "__main__":
    print("Simulating drops for one iteration of Tacet Field...\n")
    tacet_field = TacetField()
    for e in tacet_field.drops:
        if e.set == 'Correct':
            match e.cost:
                case 1:
                    if e.mainstat in tacet_field.acceptable[1]:
                        e.roll_substats(2)
                case 3:
                    if e.mainstat in tacet_field.acceptable[3]:
                        e.roll_substats(3)

    print(tacet_field)
    print(tacet_field.total_echoes_generated)