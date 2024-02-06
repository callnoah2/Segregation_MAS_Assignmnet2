
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
    def __init__(self, width, height, empty_ratio, similarity_thresholds, n_iterations, colors=2, preference_thresholds=None):
        self.agents = None
        self.width = width
        self.height = height
        self.colors = colors
        self.empty_ratio = empty_ratio
        self.similarity_thresholds = similarity_thresholds
        self.preference_thresholds = preference_thresholds
        self.n_iterations = n_iterations

    def populate(self):
        self.empty_houses = []
        self.agents = {}
        self.all_houses = list(itertools.product(range(self.width), range(self.height)))
        random.shuffle(self.all_houses)

        self.n_empty = int(self.empty_ratio * len(self.all_houses))
        self.empty_houses = self.all_houses[:self.n_empty]

        self.remaining_houses = self.all_houses[self.n_empty:]
        houses_by_color = [self.remaining_houses[i::self.colors] for i in range(self.colors)]

        for i in range(self.colors):
            dict2 = dict(zip(houses_by_color[i], [(i + 1, self.preference_thresholds.get(i + 1, 0.5))] * len(houses_by_color[i])))
            self.agents = {**self.agents, **dict2}

    def is_unsatisfied(self, x, y):
        myColor, myThreshold = self.agents[(x, y)]
        count_similar = 0
        count_different = 0

        if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
            if self.agents[(x - 1, y - 1)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if y > 0 and (x, y - 1) not in self.empty_houses:
            if self.agents[(x, y - 1)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
            if self.agents[(x + 1, y - 1)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and (x - 1, y) not in self.empty_houses:
            if self.agents[(x - 1, y)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
            if self.agents[(x + 1, y)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
            if self.agents[(x - 1, y + 1)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
            if self.agents[(x, y + 1)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
            if self.agents[(x + 1, y + 1)][0] == myColor:
                count_similar += 1
            else:
                count_different += 1

        color_threshold = self.similarity_thresholds.get(myColor, self.similarity_thresholds)
        preference_threshold = myThreshold

        if (count_similar + count_different) == 0:
            return False
        else:
            return (float(count_similar) / (count_similar + count_different)) < color_threshold or \
                   (float(count_similar) / (count_similar + count_different)) < preference_threshold

    def move_locations(self, similarity_threshold=1e-2, consecutive_iterations_threshold=3, swap_probability=0.5):
        total_distance = 0
        prev_similarity = 0.0
        consecutive_iterations = 0

        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0

            for agent in self.old_agents:
                if self.is_unsatisfied(agent[0], agent[1]):
                    agent_color = self.agents[agent]

                    # Get the neighborhood of the current agent
                    neighborhood = self.get_neighborhood(agent[0], agent[1])

                    # Check if the agent is willing to swap with an open position in the neighborhood
                    if random.random() < swap_probability:
                        empty_houses_in_neighborhood = [pos for pos in neighborhood if pos in self.empty_houses]
                        if empty_houses_in_neighborhood:
                            empty_house = random.choice(empty_houses_in_neighborhood)
                            self.agents[empty_house] = agent_color
                            del self.agents[agent]
                            self.empty_houses.remove(empty_house)
                            self.empty_houses.append(agent)
                            total_distance += abs(empty_house[0] - agent[0]) + abs(empty_house[1] - agent[1])
                            n_changes += 1
                    else:
                        # Find a willing agent to swap with within the neighborhood
                        willing_agents = [a for a in self.old_agents if a in neighborhood and a != agent and self.is_willing_to_swap(a, agent)]
                        if willing_agents:
                            willing_agent = random.choice(willing_agents)
                            self.agents[agent], self.agents[willing_agent] = self.agents[willing_agent], self.agents[agent]
                            total_distance += abs(willing_agent[0] - agent[0]) + abs(willing_agent[1] - agent[1])
                            n_changes += 1

            similarity_percentage = self.calculate_similarity() * 100
            print('Iteration: %d, Similarity Percentage: %3.2f%%, Number of changes: %d, total distance: %d' % (
                i + 1, similarity_percentage, n_changes, total_distance))

            # Stopping condition based on little progress
            similarity_change = abs(similarity_percentage - prev_similarity)
            if similarity_change < similarity_threshold:
                consecutive_iterations += 1
            else:
                consecutive_iterations = 0

            if consecutive_iterations >= consecutive_iterations_threshold:
                print(f'Stopping early. Little progress for {consecutive_iterations_threshold} consecutive iterations.')
                break

            prev_similarity = similarity_percentage

            if n_changes == 0:
                break
            
    def get_neighborhood(self, x, y):
        neighborhood = [(x + i, y + j) for i in range(-1, 2) for j in range(-1, 2) if 0 <= x + i < self.width and 0 <= y + j < self.height]
        return neighborhood
    
    def is_willing_to_swap(self, agent1, agent2):
        x1, y1 = agent1
        x2, y2 = agent2

        # Check if the coordinates are in the agents dictionary
        if (x1, y1) not in self.agents or (x2, y2) not in self.agents:
            return False

        return self.calculate_similarity_for_agent(agent1) < self.calculate_similarity_for_agent(agent2)
    
    def calculate_similarity_for_agent(self, agent):
        count_similar = 0
        count_different = 0
        x, y = agent
        color = self.agents[(x, y)]

        # Check similarity with neighbors
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= x + i < self.width and 0 <= y + j < self.height and (i, j) != (0, 0):
                    neighbor_color = self.agents.get((x + i, y + j), None)
                    if neighbor_color is not None:
                        if neighbor_color == color:
                            count_similar += 1
                        else:
                            count_different += 1

        try:
            return float(count_similar) / (count_similar + count_different)
        except ZeroDivisionError:
            return 1.0
    
    def plot(self, title, file_name):
        fig, ax = plt.subplots()

        # Define color schemes for 2, 3, and 5 colors
        color_schemes = {
            2: {1: 'blue', 2: 'red'},
            3: {1: 'blue', 2: 'red', 3: 'green'},
            5: {1: 'blue', 2: 'red', 3: 'green', 4: 'yellow', 5: 'purple'}
        }

        agent_colors = color_schemes.get(self.colors, {i: 'gray' for i in range(1, self.colors + 1)})

        marker_size = 150 / self.width
        for agent, color in self.agents.items():
            x, y = agent
            ax.scatter(x + 0.5, y + 0.5, s=marker_size, color=agent_colors.get(color[0], 'gray'))

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
    schelling_0 = Schelling(5, 5, 0.3, {1: 0.3, 2: 0.3}, 200, 2, {1: 0.5, 2: 0.5})  # Example with different thresholds for each color
    schelling_0.populate()

    ##First Simulation
    schelling_1 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3}, 200, 2, {1: 0.5, 2: 0.5})
    schelling_1.populate()

    schelling_2 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.5}, 200, 2, {1: 0.5, 2: 0.5})
    schelling_2.populate()

    schelling_3 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.8}, 200, 2, {1: 0.5, 2: 0.5})
    schelling_3.populate()
    
    schelling_0_with_3_colors = Schelling(5, 5, 0.3, {1: 0.3, 2: 0.3, 3: 0.3}, 200, 3, {1: 0.5, 2: 0.5})
    schelling_0_with_3_colors.populate()

    schelling_1_with_3_colors = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3, 3: 0.4}, 200, 3, {1: 0.5, 2: 0.5})
    schelling_1_with_3_colors.populate()

    schelling_2_with_3_colors = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.5, 3: 0.2}, 200, 3, {1: 0.5, 2: 0.5})
    schelling_2_with_3_colors.populate()
    
    schelling_3_with_3_colors = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.8, 3: 0.4}, 200, 3, {1: 0.5, 2: 0.5})
    schelling_3_with_3_colors.populate()
    
    schelling_4_with_5_colors = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.4, 3: 0.2, 4: 0.1, 5: 0.5}, 200, 5, {1: 0.5, 2: 0.5})
    schelling_4_with_5_colors.populate()
    
    schelling_4_with_5_colors.plot('Schelling Model with 5 colors: Initial State', 'schelling_5_color_initial.png')
    
    schelling_1.plot('Schelling Model with 2 colors: Initial State', 'schelling_2_initial.png')
    schelling_1_with_3_colors.plot('Schelling Model with 3 colors: Initial State', 'schelling_2_color_initial.png')

    schelling_0.move_locations()
    schelling_1.move_locations()
    schelling_2.move_locations()
    schelling_3.move_locations()
    schelling_0_with_3_colors.move_locations()
    schelling_1_with_3_colors.move_locations()
    schelling_2_with_3_colors.move_locations()
    schelling_4_with_5_colors.move_locations()
    
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
    schelling_3_with_3_colors.plot('Schelling Model with 3 colors: Final State with Happiness Threshold 80%',
                     'schelling_80_color_final.png')
    schelling_4_with_5_colors.plot('Schelling Model with 5 colors: Final State with Happiness Threshold 50%',
                                   'schelling_5_color_final.png')

if __name__ == "__main__":
    main()