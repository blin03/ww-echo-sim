from echo import Echo
import matplotlib.pyplot as plt
from collections import defaultdict
import time

class Simulation:
    def __init__(self, iterations: int) -> None:
        self.results = defaultdict(lambda: {
            'xp': [], 
            'tuners': [], 
            'rolled': [],
            'xp_waveplates': [],
            'tuners_waveplates': [],
            'waveplates': [],
        })
        self.averages = {}
        self.run(iterations)

    def run(self, iterations: int) -> None:
        # Roll echoes with every possible threshold for the specified number of iterations
        for threshold in range(1, 6): 
            for _ in range(iterations):
                xp, tuners, rolled, usable = 0, 0, 0, 0
                while usable < 5:
                    echo = Echo(threshold)
                    if echo.dbl_crit:
                        usable += 1

                    cost = echo.calculate_costs()
                    xp += cost[0]
                    tuners += cost[1]
                    rolled += 1

                xp_waveplates = 12.4136 * xp
                tuners_waveplates = 3 * tuners
                self.results[threshold]['xp'].append(xp)
                self.results[threshold]['tuners'].append(tuners)
                self.results[threshold]['rolled'].append(rolled)
                self.results[threshold]['xp_waveplates'].append(xp_waveplates)
                self.results[threshold]['tuners_waveplates'].append(tuners_waveplates)
                self.results[threshold]['waveplates'].append(max(xp_waveplates, tuners_waveplates))

        return

    def compute_averages(self) -> None:
        for threshold in sorted(self.results.keys()):
            metrics = self.results[threshold]
            self.averages[threshold] = {
                key: sum(values) / len(values) if values else 0
                for key, values in metrics.items()
            }

        for threshold in self.averages:
            avg_xp_waveplates = self.averages[threshold]['xp_waveplates']
            avg_tuners_waveplates = self.averages[threshold]['tuners_waveplates']
            bottleneck = (1 - avg_xp_waveplates / avg_tuners_waveplates) * 100
            self.averages[threshold]['bottleneck'] = bottleneck

        return

    def create_table(self) -> None:
        columns = ["Threshold", "Echoes Rolled", "Gold Tubes Used", "Tuners Used", "Days of Waveplate", "Limiting Factor"]

        table_data = []
        for threshold, data in sorted(self.averages.items()):
            echoes = data['rolled']
            xp = data['xp']
            tuners = data['tuners']
            days = data['waveplates'] / 240
            bottleneck = data['bottleneck']

            row = [
                str(threshold),
                f"{echoes:.2f}",
                f"{xp:.2f}",
                f"{tuners:.2f}",
                f"{days:.2f}",
                f"{abs(bottleneck):.2f}% {'Tuners' if bottleneck > 0 else 'XP'}"
            ]
            table_data.append(row)

        fig, ax = plt.subplots(figsize=(10, len(table_data) * 0.5 + 1))
        plt.title("Costs to Achieve 5x Double Crit by Fodder Threshold", color="white")
        fig.patch.set_facecolor('#303030')
        ax.axis('off')

        mpl_table = ax.table(cellText=table_data, colLabels=columns, cellLoc='center', loc='center')
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(10)
        mpl_table.scale(1, 1.5)

        for (row, _), cell in mpl_table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color="white")
                cell.set_facecolor('#303030')
            else:
                cell.set_facecolor('#505050')
                cell.set_text_props(color="white")

        return

    def create_plot(self) -> None:
        thresholds = sorted(self.averages.keys())
        avg_xp_waveplates = [self.averages[t]['xp_waveplates'] for t in thresholds]
        avg_tuners_waveplates = [self.averages[t]['tuners_waveplates'] for t in thresholds]

        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#303030')
        ax.set_facecolor('#303030')

        ax.plot(thresholds, avg_xp_waveplates, label="XP", marker='o')
        ax.plot(thresholds, avg_tuners_waveplates, label="Tuners", marker='o')
        ax.set_xlabel("Fodder Threshold", color="white")
        ax.set_ylabel("Waveplate Cost", color="white")
        ax.set_title("XP vs Tuner Economy", color="white")
        ax.tick_params(axis='both', colors="white")
        ax.grid(True, color="white")
        ax.set_xticks(thresholds)
        legend = ax.legend()
        for text in legend.get_texts():
            text.set_color("black")

        return

    def print_to_console(self) -> None:
        for threshold, data in self.averages.items():
            print(
                f"Threshold {threshold}: "
                f"{data['xp']:.2f} tubes, "
                f"{data['tuners']:.2f} tuners, "
                f"{data['rolled']:.2f} echoes rolled, "
                f"{data['xp_waveplates']:.2f} xp waveplates, "
                f"{data['tuners_waveplates']:.2f} tuner waveplates, "
                f"{abs(data['bottleneck']):.2f}% "
                f"{'tuner' if data['bottleneck'] > 0 else 'xp'} bottleneck"
            )
        return

if __name__ == "__main__":
    start_time = time.perf_counter()

    iterations = 10000  # Number of iterations for the simulation
    sim = Simulation(iterations)
    print(f"Averages over {iterations} iterations to roll 5 double crit echoes:")
    sim.compute_averages()
    sim.print_to_console()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Finished in {elapsed_time:.6f}s")

    sim.create_table()
    sim.create_plot()
    plt.tight_layout()
    plt.show()