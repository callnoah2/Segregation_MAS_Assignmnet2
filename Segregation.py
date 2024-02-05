
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
        if (x, y) not in self.agents:
            return False

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

    def get_neighbors(self, x, y):
        neighbors = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y),                 (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        ]

        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.width and 0 <= ny < self.height]

    def try_location_swap(self, agent1, agent2):
        x1, y1 = agent1
        x2, y2 = agent2
        color1 = self.agents[agent1]
        color2 = self.agents[agent2]

        # Check if swapping is beneficial for both agents
        similarity_before = self.calculate_similarity(x1, y1)
        similarity_before += self.calculate_similarity(x2, y2)

        # Swap the agents
        self.agents[agent1] = color2
        self.agents[agent2] = color1

        # Check if swapping is beneficial for both agents after the swap
        similarity_after = self.calculate_similarity(x1, y1)
        similarity_after += self.calculate_similarity(x2, y2)

        # If swapping is not beneficial for both agents, revert the swap
        if similarity_after < similarity_before:
            self.agents[agent1] = color1
            self.agents[agent2] = color2

    
    def move_locations(self, similarity_threshold=1e-3, consecutive_iterations_threshold=2, max_swap_attempts=10):
        total_distance = 0
        prev_similarity = 0.0
        consecutive_iterations = 0
        

        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0

            for agent in self.old_agents:
                swap_attempts = 0

                while swap_attempts < max_swap_attempts and self.is_unsatisfied(agent[0], agent[1]):
                    print(f'Swap attempts: {swap_attempts}')
                    agent_color = self.agents[agent]
                    empty_house = random.choice(self.empty_houses)

                    # Try to improve current location by swapping with another agent
                    neighbors = self.get_neighbors(agent[0], agent[1])
                    for neighbor in neighbors:
                        if self.is_unsatisfied(neighbor[0], neighbor[1]):
                            self.try_location_swap(agent, neighbor)
                            n_changes += 1
                            break  # Break after the first successful swap

                    # If no improvement, move to an empty house
                    if agent in self.agents:
                        del self.agents[agent]
                    self.agents[empty_house] = agent_color
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)
                    total_distance += abs(empty_house[0] - agent[0]) + abs(empty_house[1] - agent[1])
                    n_changes += 1

                    swap_attempts += 1

            similarity_percentage = self.calculate_similarity(agent[0], agent[1]) * 100
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


    def plot(self, title, file_name):
        fig, ax = plt.subplots()
        agent_colors = {
            1: 'b', 2: 'r', 3: 'g', 4: 'c', 5: 'm', 6: 'y', 7: 'k', 8: 'orange', 9: 'purple'  # Add more colors here
        }
        marker_size = 150 / self.width
        for agent in self.agents:
            ax.scatter(agent[0] + 0.5, agent[1] + 0.5, s=marker_size, color=agent_colors[self.agents[agent]])

        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(file_name)

    def calculate_similarity(self, x, y):
        count_similar = 0
        count_different = 0
        color = self.agents[(x, y)]

        for agent_x, agent_y in self.agents:
            if (agent_x, agent_y) != (x, y):
                agent_color = self.agents[(agent_x, agent_y)]
                if (agent_x - 1, agent_y - 1) not in self.empty_houses and self.agents.get((agent_x - 1, agent_y - 1)) == color:
                    count_similar += 1
                elif (agent_x - 1, agent_y - 1) not in self.empty_houses and self.agents.get((agent_x - 1, agent_y - 1)) != color:
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
            return float(count_similar) / (count_similar + count_different)
        except ZeroDivisionError:
            return 1


def main():
    ##Starter Simulation
    schelling_0 = Schelling(5, 5, 0.3, {1: 0.3, 2: 0.3}, 200, 2)
    schelling_0.populate()

    ##First Simulation
    schelling_1 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3, 3: 0.4}, 200, 3)  # Example with 3 colors and different thresholds
    schelling_1.populate()

    schelling_2 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.5, 3: 0.2}, 200, 3)  # Example with 3 colors and different thresholds
    schelling_2.populate()

    schelling_3 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.8}, 200, 2)
    schelling_3.populate()

    schelling_1.plot('Schelling Model with 2 colors: Initial State', 'schelling_2_initial.png')

    schelling_0.move_locations()
    schelling_1.move_locations()
    schelling_2.move_locations()
    schelling_3.move_locations()
    schelling_0.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 30%',
                     'schelling_0_30_final.png')
    schelling_1.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 30%',
                     'schelling_30_final.png')
    schelling_2.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 50%',
                     'schelling_50_final.png')
    schelling_3.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 80%',
                     'schelling_80_final.png')


if __name__ == "__main__":
    main()
