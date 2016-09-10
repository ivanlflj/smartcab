import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from sklearn.tree import DecisionTreeRegressor

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.possible_actions = [None, 'forward', 'left', 'right']
        self.tree = DecisionTreeRegressor(min_samples_split = 1)
        self.X = self.prepare_X()
        self.y = self.prepare_y(self.X)
        self.tree.fit(self.X,self.y)
        self.epsilon = 0.0
        #Performance variables
        self.steps = 0
        self.errors = 0

    def prepare_X(self):
        X = []
        for i in range(4):
            for j in range(2):
                for k in range(4):
                    for l in range(4):
                        for m in range(4):
                            X.append([i,j,k,l,m])
        return X

    def prepare_y(self, X):
        y = []
        for i in range(len(X)):
            y.append(1.)
        return y



    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = [self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left']]
        transformed_state = transform_state(self.state)

        # TODO: Select action according to your policy
        if random.random() > (1 - self.epsilon):
            action = random.choice([None, 'forward', 'left', 'right'])
        else:
            reward_max = max(self.tree.predict([transform_action(action),transformed_state[0],transformed_state[1],transformed_state[2],transformed_state[3]]) for action in self.possible_actions)
            for act in self.possible_actions:
                if self.tree.predict([transform_action(act),transformed_state[0],transformed_state[1],transformed_state[2],transformed_state[3]]) == reward_max:
                    action = act
            
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.X.append([transform_action(action),transformed_state[0],transformed_state[1],transformed_state[2],transformed_state[3]])
        self.y.append(reward)
        self.tree.fit(self.X,self.y)


        #Update performance variables
        self.steps += 1
        if reward < 0.:
            self.errors += 1

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        print "Performance variables: %0.1f steps until here and %0.1f errors in total." % (self.steps, self.errors)

def transform_state(state):
    state_transformed = []
    for value in range(len(state)):
        if value == 1:
            state_transformed.append(0 if state[value] == 'green' else 1)
        else:
            state_transformed.append({None: 0, 'forward': 1, 'left': 2, 'right': 3}[state[value]])
    return state_transformed

def transform_action(action):
    action_transformed = {None: 0, 'forward': 1, 'left': 2, 'right': 3}[action]
    return action_transformed

def untransform_action(action_transformed):
    for action, act_trans in {None: 0, 'forward': 1, 'left': 2, 'right': 3}.iteritems():
        if act_trans == action_transformed:
            return action


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.1, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
