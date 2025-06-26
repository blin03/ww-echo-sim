from echo import Echo
from tacet import TacetField
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from collections import defaultdict
import time


class BaseSimulation:
    def __init__(self, iterations: int, cost_filter: int) -> None:
        assert cost_filter in (1, 3), "cost_filter must be 1 or 3"
        self.cost_filter = cost_filter
        self.iterations = iterations
        self.results = defaultdict(lambda: {
            'xp': [],
            'tuners': [],
            'total': [],
            'rolled': [],
            'echo_waveplates': [],
            'xp_waveplates': [],
            'tuners_waveplates': [],
            'waveplates': [],
        })
        self.averages = {}
        self.run()

    def run(self) -> None:
        for threshold in range(1, 6):
            for _ in range(self.iterations):
                t = TacetField()
                usable = []
                xp, tuners, rolled, tacet_runs = 0, 0, 0, 0

                while len(usable) < 2:
                    t.run()
                    tacet_runs += 1
                    for e in t.drops:
                        if (
                            e.cost == self.cost_filter
                            and e.set == 'Correct'
                            and e.mainstat in t.acceptable[self.cost_filter]
                            and len(usable) < 2
                        ):
                            e.roll_substats(threshold)
                            cost = e.calculate_costs()
                            xp += cost[0]
                            tuners += cost[1]
                            rolled += 1
                            if e.dbl_crit:
                                usable.append(e)

                xp_waveplates = 12.4136 * xp
                tuners_waveplates = 3 * tuners
                tacet_waveplates = tacet_runs * 60

                self.results[threshold]['xp'].append(xp)
                self.results[threshold]['tuners'].append(tuners)
                self.results[threshold]['total'].append(t.total_echoes_generated)
                self.results[threshold]['rolled'].append(rolled)
                self.results[threshold]['echo_waveplates'].append(tacet_waveplates)
                self.results[threshold]['xp_waveplates'].append(xp_waveplates)
                self.results[threshold]['tuners_waveplates'].append(tuners_waveplates)
                self.results[threshold]['waveplates'].append(max(xp_waveplates, tuners_waveplates, tacet_waveplates))

    def compute_averages(self) -> None:
        for threshold in sorted(self.results.keys()):
            metrics = self.results[threshold]
            self.averages[threshold] = {}

            for key, values in metrics.items():
                if not values:
                    self.averages[threshold][key] = 0
                else:
                    if key == 'total':
                        combined = {1: 0, 3: 0}
                        for d in values:
                            combined[1] += d.get(1, 0)
                            combined[3] += d.get(3, 0)
                        count = len(values)
                        self.averages[threshold][key] = {
                            1: combined[1] / count,
                            3: combined[3] / count,
                        }
                    else:
                        self.averages[threshold][key] = sum(values) / len(values)

        for threshold in self.averages:
            avg_echo_waveplates = self.averages[threshold]['echo_waveplates']
            avg_xp_waveplates = self.averages[threshold]['xp_waveplates']
            avg_tuners_waveplates = self.averages[threshold]['tuners_waveplates']
            avgs = [avg_echo_waveplates, avg_xp_waveplates, avg_tuners_waveplates]
            bottleneck = (max(avgs) / min(avgs) - 1) * 100 if min(avgs) > 0 else 0
            self.averages[threshold]['bottleneck'] = round(bottleneck, 2)

    def create_plot(self, ax=None) -> None:
        thresholds = sorted(self.averages.keys())

        xp_wp = [self.averages[t]['xp_waveplates'] for t in thresholds]
        tuner_wp = [self.averages[t]['tuners_waveplates'] for t in thresholds]
        echo_wp = [self.averages[t]['echo_waveplates'] for t in thresholds]

        if ax is None:
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor('#303030')
        ax.set_facecolor('#303030')

        ax.plot(thresholds, xp_wp, label='XP', marker='o', color='cyan')
        ax.plot(thresholds, tuner_wp, label='Tuners', marker='o', color='magenta')
        ax.plot(thresholds, echo_wp, label='Echoes', marker='o', color='yellow')

        ax.set_xlabel("Fodder Threshold", color="white")
        ax.set_ylabel("Waveplate Cost", color="white")
        ax.set_title(f"Waveplate Costs vs Threshold (Cost {self.cost_filter})", color="white")
        ax.tick_params(axis='both', colors="white")
        ax.grid(True, color="white", linestyle=':', linewidth=0.5)
        ax.set_xticks(thresholds)

        legend = ax.legend()
        for text in legend.get_texts():
            text.set_color("black")

    def create_table(self, ax=None) -> None:
        columns = ["Threshold", "Echoes Rolled", "XP Used", "Tuners Used", "Echo Waveplates", "XP Waveplates", "Tuner Waveplates", "Bottleneck %"]

        table_data = []
        for threshold, data in sorted(self.averages.items()):
            row = [
                str(threshold),
                f"{data['rolled']:.2f}",
                f"{data['xp']:.2f}",
                f"{data['tuners']:.2f}",
                f"{data['echo_waveplates']:.2f}",
                f"{data['xp_waveplates']:.2f}",
                f"{data['tuners_waveplates']:.2f}",
                f"{data['bottleneck']:.2f}",
            ]
            table_data.append(row)

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, len(table_data) * 0.5 + 1))
            fig.patch.set_facecolor('#303030')
        ax.axis('off')

        ax.set_title(f"Simulation Results Table (Cost {self.cost_filter})", color='white')

        mpl_table = ax.table(cellText=table_data, colLabels=columns, cellLoc='center', loc='center')
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(10)
        mpl_table.scale(1, 1.5)

        for (row, _), cell in mpl_table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#303030')
            else:
                cell.set_facecolor('#505050')
                cell.set_text_props(color='white')


def plot_combined(sim1: BaseSimulation, sim3: BaseSimulation) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig.patch.set_facecolor('#303030')

    for i, (ax, sim, cost_label) in enumerate(zip(axes, (sim1, sim3), ('Cost 1', 'Cost 3'))):
        sim.create_plot(ax)
        ax.set_title(f"Waveplate Costs vs Threshold ({cost_label})")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=False))
        ax.tick_params(axis='both', colors="white")
        ax.grid(True, color="white", linestyle=':', linewidth=0.5)
        ax.set_xlabel("Fodder Threshold", color="white")

        if i == 0:
            ax.set_ylabel("Waveplate Cost", color="white")
        else:
            ax.yaxis.set_tick_params(labelleft=True)

    plt.tight_layout()


def create_combined_table(sim1: BaseSimulation, sim3: BaseSimulation) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.patch.set_facecolor('#303030')

    sim1.create_table(ax=axes[0])
    sim3.create_table(ax=axes[1])

    plt.tight_layout()


if __name__ == "__main__":
    start_time = time.perf_counter()

    iterations = 50000
    sim_1 = BaseSimulation(iterations, cost_filter=1)
    sim_3 = BaseSimulation(iterations, cost_filter=3)
    sim_1.compute_averages()
    sim_3.compute_averages()

    plot_combined(sim_1, sim_3)
    create_combined_table(sim_1, sim_3)

    end_time = time.perf_counter()
    print(f"Finished in {end_time - start_time:.6f}s")

    plt.show()
