import random

class Echo:
    possible_substats = {
            'Crit Rate'     : [6.3, 6.9, 7.5, 8.1, 8.7, 9.3, 9.9, 10.5],
            'Crit Damage'   : [12.6, 13.8, 15.0, 16.2, 17.4, 18.6, 19.8, 21.0],
            'ATK'           : [30, 40, 50, 60],
            'ATK%'          : [6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6],
            'DEF'           : [40, 50, 60, 70],
            'DEF%'          : [8.1, 9.0, 10.0, 10.9, 11.8, 12.8, 13.8, 14.7],
            'HP'            : [320, 360, 390, 430, 470, 510, 540, 580],
            'HP%'           : [6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6],
            'Energy Regen'  : [6.8, 7.6, 8.4, 9.2, 10, 10.8, 11.6, 12.4],
            'Basic%'        : [6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6],
            'Heavy%'        : [6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6],
            'Skill%'        : [6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6],
            'Liberation%'   : [6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6],
        }

    substat_distribution = {
            'Crit Rate'     : [22.57, 44.61, 68.56, 77.60, 84.83, 92.54, 96.28, 100.00],
            'Crit Damage'   : [22.57, 44.61, 68.56, 77.60, 84.83, 92.54, 96.28, 100.00],
            'ATK'           : [9.36, 59.42, 97.25, 100.00],
            'ATK%'          : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'DEF'           : [9.36, 59.42, 97.25, 100.00],
            'DEF%'          : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'HP'            : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'HP%'           : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'Energy Regen'  : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'Basic%'        : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'Heavy%'        : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'Skill%'        : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
            'Liberation%'   : [7.13, 14.57, 34.06, 58.79, 76.43, 91.17, 97.32, 100.00],
        }
    
    xp_thresholds = {
            1: [0.88, 10],
            2: [3.3, 20],
            3: [7.92, 30],
            4: [15.82, 40],
            5: [28.52, 50],
    }

    # Initialize Echo object
    # :threshold: int - The number of substats by which the echo must have at least one crit stat to proceed
    def __init__(self, threshold: int) -> None:
        self.substats = []
        self.dbl_crit = None
        self.roll_substats(threshold)
        return
    
    # Roll the substats for the Echo object
    # :threshold: int - The number of substats to roll before checking for the presence of a crit stat
    def roll_substats(self, threshold: int) -> None:
        while len(self.substats) < threshold:
            # Randomly select a substat from the available options
            substat = random.choice(list(self.possible_substats.keys()))
            if not any(line[0] == substat for line in self.substats):
                roll = random.randrange(0, 100)
                # Determine exact substat value based on roll
                for i in range(len(self.substat_distribution[substat])):
                    if roll < self.substat_distribution[substat][i]:
                        self.substats.append((substat, self.possible_substats[substat][i]))
                        break

        has_cr = any(line[0] == 'Crit Rate' for line in self.substats)
        has_cd = any(line[0] == 'Crit Damage' for line in self.substats)
        # If neither crit stat is present by the threshold, mark dbl_crit as False and do not roll further
        # If at least one crit stat is present by the threshold, roll until we have 5 substats
        if (len(self.substats) < 5):
            if not (has_cr or has_cd):
                self.dbl_crit = False
            else: 
                self.roll_substats(5)
        else:
            # If both crit stats are present at 5 substats, mark dbl_crit as True
            # If we have at least one crit stat but not both (an echo would not have 
            # made it here unless it had at least one), mark dbl_crit as False
            if has_cr and has_cd:
                self.dbl_crit = True
            else:
                self.dbl_crit = False
        return 

    # Calculate the XP and Tuner costs associated with the Echo's substats
    def calculate_costs(self) -> list:
        if self.dbl_crit:
            cost = self.xp_thresholds[5]
        else:
            cost = [0.3 * self.xp_thresholds[len(self.substats)][0], 0.7 * self.xp_thresholds[len(self.substats)][1]]
        return cost
    
    def __str__(self) -> str:
        return f"Substats: {self.substats}"
        


if __name__ == "__main__":
    not_valid = True
    while not_valid:
        threshold = input("Enter the minimum number of substats to roll before checking for crits (1-5): ")
        try:
            threshold = int(threshold)
            if threshold < 1 or threshold > 5:
                raise ValueError("Threshold must be between 1 and 5.")
        except ValueError as e: 
            print(f"Invalid input: {e}")
            continue
        not_valid = False

    
    xp, tuners, rolled = 0, 0, 0
    usable = []
    while len(usable) < 5:
        echo = Echo(threshold)
        # print(echo)
        if echo.dbl_crit:
            usable.append(echo)

        cost = echo.calculate_costs()
        xp += cost[0]
        tuners += cost[1]
        rolled += 1


    xp_waveplates = 12.4136 * xp
    tuners_waveplates = 3 * tuners
    bottleneck = (xp_waveplates/tuners_waveplates if xp_waveplates>tuners_waveplates else tuners_waveplates/xp_waveplates) * 100
    print(f"\nRolling echoes with a minimum crit threshold of {threshold}:")
    print(f"{rolled} echoes rolled to obtain 5 usable echoes with double crit.")
    print(f"XP consumed: {round(xp, 2)} gold rarity tubes, Tuners consumed: {round(tuners)}")
    print(f"Equivalent to {round(xp_waveplates)} Waveplates of XP and {round(tuners_waveplates)} Waveplates of Tuners, "
          f"which would take {round(max(12.5 * xp, 3 * tuners) / 240, 2)} days to farm.")
    print(f"You are bottlenecked by {'XP' if xp_waveplates > tuners_waveplates else 'Tuners'} "
          f"by {round(bottleneck - 100, 2)}%.")
    for e in usable:
        print(e)
