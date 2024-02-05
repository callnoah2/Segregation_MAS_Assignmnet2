
'''
Author : Adil Moujahid
Email : adil.mouja@gmail.com
Description: Simulations of Schelling's seggregation model

You will need to set up pycharm to import matplotlib.
'''

import matplotlib.pyplot as plt
import itertools
import random
import copy


class Schelling:
    def __init__(self, width, height, empty_ratio, similarity_threshold, n_iterations, colors=2):
        self.agents = None
        self.width = width
        self.height = height
        self.colors = colors
        self.empty_ratio = empty_ratio
        self.similarity_threshold = similarity_threshold
        self.n_iterations = n_iterations

    def populate(self):
            self.empty_houses = []
            self.agents = {}
            print("Populate ", self.width, self.height)
            self.all_houses = list(itertools.product(range(self.width), range(self.height)))
            print(self.all_houses)
            random.shuffle(self.all_houses)

            self.n_empty = int(self.empty_ratio * len(self.all_houses))
            self.empty_houses = self.all_houses[:self.n_empty]

            self.remaining_houses = self.all_houses[self.n_empty:]
            houses_by_color = [self.remaining_houses[i::self.colors] for i in range(self.colors)]
            print("Houses by color ", houses_by_color[0])
            for i in range(self.colors):
                # create agents for each color
                dict2 = dict(zip(houses_by_color[i], [i + 1] * len(houses_by_color[i])))
                self.agents = {**self.agents, **dict2}
            print("dictionary", self.agents)

    def is_unsatisfied(self, x, y):

        myColor = self.agents[(x, y)]
        count_similar = 0
        count_different = 0

        if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
            if self.agents[(x - 1, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if y > 0 and (x, y - 1) not in self.empty_houses:
            if self.agents[(x, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
            if self.agents[(x + 1, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and (x - 1, y) not in self.empty_houses:
            if self.agents[(x - 1, y)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
            if self.agents[(x + 1, y)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
            if self.agents[(x - 1, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
            if self.agents[(x, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
            if self.agents[(x + 1, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1

        color_threshold = self.similarity_threshold.get(myColor, self.similarity_threshold)  # Get color-specific threshold
        if (count_similar + count_different) == 0:
            return False
        else:
            return float(count_similar) / (count_similar + count_different) < color_threshold
    
    def move_locations(self):
        total_distance = 0
        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0
            for agent in self.old_agents:
                if self.is_unsatisfied(agent[0], agent[1]):
                    agent_color = self.agents[agent]
                    empty_house = random.choice(self.empty_houses)
                    self.agents[empty_house] = agent_color
                    del self.agents[agent]
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)
                    total_distance += abs(empty_house[0] - agent[0]) + abs(empty_house[1] - agent[1])
                    n_changes += 1

            similarity_percentage = self.calculate_similarity() * 100
            print('Iteration: %d, Similarity Percentage: %3.2f%%, Number of changes: %d, total distance: %d' % (
                i + 1, similarity_percentage, n_changes, total_distance))

            if n_changes == 0:
                break


    def plot(self, title, file_name):
        fig, ax = plt.subplots()
        # If you want to run the simulation with more than 7 colors, you should set agent_colors accordingly
        agent_colors = {1: 'b', 2: 'r', 3: 'g', 4: 'c', 5: 'm', 6: 'y', 7: 'k', 8: 'orange', 9: 'purple'}
        marker_size = 150/self.width  # no logic here, I just played around with it
        for agent in self.agents:
            ax.scatter(agent[0] + 0.5, agent[1] + 0.5,s=marker_size, color=agent_colors[self.agents[agent]])

        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(file_name)

    def calculate_similarity(self):
        similarity = []
        for agent in self.agents:
            count_similar = 0
            count_different = 0
            x = agent[0]
            y = agent[1]
            color = self.agents[(x, y)]
            if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
                if self.agents[(x - 1, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if y > 0 and (x, y - 1) not in self.empty_houses:
                if self.agents[(x, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
                if self.agents[(x + 1, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and (x - 1, y) not in self.empty_houses:
                if self.agents[(x - 1, y)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
                if self.agents[(x + 1, y)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
                if self.agents[(x - 1, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
                if self.agents[(x, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
                if self.agents[(x + 1, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            try:
                similarity.append(float(count_similar) / (count_similar + count_different))
            except:
                similarity.append(1)
        return sum(similarity) / len(similarity)


def main():
    ##Starter Simulation
    schelling_0 = Schelling(5, 5, 0.3, {1: 0.3, 2: 0.3}, 200, 2)  # Example with different thresholds for each color
    schelling_0.populate()

    ##First Simulation
    schelling_1 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3}, 200, 2)
    schelling_1.populate()

    schelling_2 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.5}, 200, 2)
    schelling_2.populate()

    schelling_3 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.8}, 200, 2)
    schelling_3.populate()

    schelling_0_with_3_colors = Schelling(5, 5, 0.3, {1: 0.3, 2: 0.3, 3: 0.3}, 200, 3)
    schelling_0_with_3_colors.populate()

    schelling_1_with_3_colors = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3, 3: 0.4}, 200, 3)
    schelling_1_with_3_colors.populate()

    schelling_2_with_3_colors = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.5, 3: 0.2}, 200, 3)
    schelling_2_with_3_colors.populate()
    
    schelling_1.plot('Schelling Model with 2 colors: Initial State', 'schelling_2_initial.png')
    schelling_1_with_3_colors.plot('Schelling Model with 3 colors: Initial State', 'schelling_2_color_initial.png')

    schelling_0.move_locations()
    schelling_1.move_locations()
    schelling_2.move_locations()
    schelling_0_with_3_colors.move_locations()
    schelling_1_with_3_colors.move_locations()
    schelling_2_with_3_colors.move_locations()
    schelling_3.move_locations()
    schelling_0.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 30%',
                     'schelling_0_30_final.png')
    schelling_1.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 30%',
                     'schelling_30_final.png')
    schelling_2.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 50%',
                     'schelling_50_final.png')
    schelling_3.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 80%',
                     'schelling_80_final.png')
    schelling_0_with_3_colors.plot('Schelling Model with 3 colors: Final State with Happiness Threshold 30%',
                     'schelling_0_30_color_final.png')
    schelling_1_with_3_colors.plot('Schelling Model with 3 colors: Final State with Happiness Threshold 30%',
                     'schelling_30_color_final.png')
    schelling_2_with_3_colors.plot('Schelling Model with 3 colors: Final State with Happiness Threshold 50%',
                     'schelling_50_color_final.png')


if __name__ == "__main__":
    main()