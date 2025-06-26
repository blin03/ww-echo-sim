from echo import Echo
from tacet import TacetField
import matplotlib.pyplot as plt
from collections import defaultdict
import time

class Simulation:
    def __init__(self, iterations: int) -> None:
        self.results = defaultdict(lambda: {
            'xp': [], 
            'tuners': [],
            'total': [],
            'rolled_1c': [],
            'rolled_3c': [],
            'echo_waveplates': [],
            'xp_waveplates': [],
            'tuners_waveplates': [],
            'waveplates': [],
        })
        self.averages = {}
        self.run(iterations)

    def run(self, iterations: int) -> None:
        # Simulate tacet field drops, rolling with every possible threshold 
        # for the specified number of iterations until we have 5 usable echoes
        # Note: we will use the logic in tacet.py for 1 and 3 cost echoes,
        # but 4 cost echoes are not farmed with stamina, so they will be handled separately.
        for threshold in range(1, 6): 
            for _ in range(iterations):
                t = TacetField()
                usable_1c, usable_3c, usable_4c = [], [], []
                xp, tuners, rolled_1c, rolled_3c, tacet_runs = 0, 0, 0, 0, 0

                while len(usable_1c) < 2 or len(usable_3c) < 2:
                    t.run()
                    tacet_runs += 1
                    for e in t.drops:
                        match e.cost:
                            case 1:
                                if e.set == 'Correct' and e.mainstat in t.acceptable[1] and len(usable_1c) < 2:
                                    e.roll_substats(threshold)
                                    cost = e.calculate_costs()
                                    xp += cost[0]
                                    tuners += cost[1]
                                    rolled_1c += 1
                                    if e.dbl_crit:
                                        usable_1c.append(e)
                            case 3:
                                if e.set == 'Correct' and e.mainstat in t.acceptable[3] and len(usable_3c) < 2:
                                    e.roll_substats(threshold)
                                    cost = e.calculate_costs()
                                    xp += cost[0]
                                    tuners += cost[1]
                                    rolled_3c += 1
                                    if e.dbl_crit:
                                        usable_3c.append(e)
                
                four_cost = Echo(mainstat="Crit Rate", cost="4", set="Correct")
                while not four_cost.dbl_crit:
                    four_cost.substats = []
                    four_cost.roll_substats(threshold)
                    cost = four_cost.calculate_costs()
                    xp += cost[0]
                    tuners += cost[1]
                usable_4c.append(four_cost)

                xp_waveplates = 12.4136 * xp
                tuners_waveplates = 3 * tuners
                tacet_waveplates = tacet_runs * 60
                self.results[threshold]['xp'].append(xp)
                self.results[threshold]['tuners'].append(tuners)
                self.results[threshold]['total'].append(t.total_echoes_generated)
                self.results[threshold]['rolled_1c'].append(rolled_1c)
                self.results[threshold]['rolled_3c'].append(rolled_3c)
                self.results[threshold]['echo_waveplates'].append(tacet_waveplates)
                self.results[threshold]['xp_waveplates'].append(xp_waveplates)
                self.results[threshold]['tuners_waveplates'].append(tuners_waveplates)
                self.results[threshold]['waveplates'].append(max(xp_waveplates, tuners_waveplates, tacet_waveplates))
        return
    
    def compute_averages(self) -> None:
        for threshold in sorted(self.results.keys()):
            metrics = self.results[threshold]
            self.averages[threshold] = {}

            for key, values in metrics.items():
                if not values:
                    self.averages[threshold][key] = 0
                    continue

                if key == 'total':
                    combined = {1: 0, 3: 0}
                    for d in values:
                        combined[1] += d.get(1, 0)
                        combined[3] += d.get(3, 0)
                    count = len(values)
                    self.averages[threshold][key] = {
                        1: combined[1] / count,
                        3: combined[3] / count
                    }
                else:
                    self.averages[threshold][key] = sum(values) / len(values)

        for threshold in self.averages:
            avg_echo_waveplates = self.averages[threshold]['echo_waveplates']
            avg_xp_waveplates = self.averages[threshold]['xp_waveplates']
            avg_tuners_waveplates = self.averages[threshold]['tuners_waveplates']
            avgs = [avg_echo_waveplates, avg_xp_waveplates, avg_tuners_waveplates]
            bottleneck = (max(avgs) / min(avgs) - 1) * 100
            self.averages[threshold]['bottleneck'] = round(bottleneck, 2)

        return

    def create_plot(self) -> None:
        thresholds = sorted(self.averages.keys())
        
        xp_wp = [self.averages[t]['xp_waveplates'] for t in thresholds]
        tuner_wp = [self.averages[t]['tuners_waveplates'] for t in thresholds]
        echo_wp = [self.averages[t]['echo_waveplates'] for t in thresholds]

        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#303030')
        ax.set_facecolor('#303030')

        ax.plot(thresholds, xp_wp, label='XP', marker='o', color='cyan')
        ax.plot(thresholds, tuner_wp, label='Tuners', marker='o', color='magenta')
        ax.plot(thresholds, echo_wp, label='Echoes', marker='o', color='yellow')

        ax.set_xlabel("Fodder Threshold", color="white")
        ax.set_ylabel("Waveplate Cost", color="white")
        ax.set_title("Waveplate Costs vs Threshold", color="white")
        ax.tick_params(axis='both', colors="white")
        ax.grid(True, color="white", linestyle=':', linewidth=0.5)
        ax.set_xticks(thresholds)

        legend = ax.legend()
        for text in legend.get_texts():
            text.set_color("black")

        plt.tight_layout()
        return

if __name__ == "__main__":
    start_time = time.perf_counter()

    iterations = 1000  # Number of iterations for the simulation
    sim = Simulation(iterations)
    sim.compute_averages()
    sim.create_plot()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Finished in {elapsed_time:.6f}s")

    plt.tight_layout()
    plt.show()
