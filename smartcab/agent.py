import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.possible_actions = [None, 'forward', 'left', 'right']
        self.q = {}
        self.alpha = 0.5
        self.gama = 0.0
        self.epsilon = 0.0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = [self.next_waypoint, inputs]
        
        max = -float('Inf')
        best_action = 'forward'
        for action in self.possible_actions:
            try:
                if self.q[str([self.state,action])] >= max:
                    max = self.q[str([self.state,action])]
                    best_action = action
            except:
                self.q[str([self.state,action])] = 0.

        # TODO: Select action according to your policy
        if random.random() < (1 - self.epsilon):
            action = best_action
        else:
            action = random.choice(possible_actions)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        try:
            self.q[self.last_state_action] = self.q[self.last_state_action] + self.alpha * (self.last_reward + self.gama * self.q[str([self.state,action])] - self.q[self.last_state_action])
        except:
            print("")
        self.last_state_action = str([self.state,action])
        self.last_reward = reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.2, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
