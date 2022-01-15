# generator/data.py
# Data generation functions.

import random
from argparse import Namespace

import numpy as np
from faker import Faker

fake = Faker()


def generate_user_ids(size: int = 1000) -> list:
    """Generate user ids.

    Args:
        size (int): The number of ids. (Default is 1000)

    Returns:
        The list with user ids.
    """
    user_ids = [fake.uuid4() for _ in range(size)]
    return user_ids


def random_pareto(
    size: int, lower: float, upper: float, shape: float = 0.8
) -> np.ndarray:
    """Generate numbers from a Pareto distribution in the specific range.

    Args:
        size (int): The number of elements in the array.
        lower (float): The lower bound of the range.
        upper (float): The upper bound of the range.
        shape (float): Shape of the distribution. Must be positive. (Default is 0.8)

    Returns:
        The array of random numbers.
    """
    x = np.random.pareto(shape, size * 5 // 4) + lower
    return x[x < upper][:size]


def generate_items(params: Namespace, size: int = 1000) -> list:
    """Generate a list of items.

    Args:
        params (Namespace): Input parameters for operations.
        size (int): The number of items in the list. (Default is 1000)

    Returns:
        The list of items.
    """
    n_free = int(size * params.pfi)
    idxs = np.arange(size)
    np.random.shuffle(idxs)
    free_idxs = idxs[:n_free]

    prices = random_pareto(
        size, lower=params.price_lower, upper=params.price_upper
    )
    prices = prices.round(decimals=2)
    prices[free_idxs] = 0.0

    discounts = random_pareto(size, lower=0, upper=100)
    discounts = discounts.round(decimals=0)
    discounts[free_idxs] = 0.0

    items = []
    for i in range(size):
        id_ = fake.uuid4()
        nb_words = random.randint(1, 3)
        name = fake.sentence(nb_words).rstrip(".")
        desc = fake.sentence()
        type_ = random.choice(params.item_types)
        price = prices[i]
        discount = discounts[i]

        item = {
            "id": id_,
            "name": name,
            "desc": desc,
            "type": type_,
            "price": price,
            "discount": discount,
        }

        items.append(item)

    return items


class MarkovChain:
    def __init__(
        self,
        transition_probs: dict,
        initial_state: str = "start",
        final_state: str = "stop",
    ):
        """
        Args:
            transition_probs (dict): The transition probabilities in Markov Chain for the predefined set of action types.
            initial_state (str): The initial state in Markov Chain. (Default is "start")
            final_state (str): The final state in Markov Chain. (Default is "stop")
        """
        self.transition_probs = transition_probs
        self.initial_state = initial_state
        self.final_state = final_state

    def next_state(self, current_state: str) -> str:
        """Generate the next state in Markov Chain.

        Args:
            current_state (str): The current state in Markov Chain.

        Returns:
            The next state in Markov Chain.
        """
        possible_states = list(self.transition_probs[current_state].keys())
        p = list(self.transition_probs[current_state].values())
        return np.random.choice(possible_states, p=p)

    def generate_states(self) -> list:
        """Generate a list of states.

        Returns:
            The list of consecutive states.
        """
        current_state = self.initial_state

        states = []
        while True:
            next_state = self.next_state(current_state)
            current_state = next_state

            if current_state == self.final_state:
                break

            states.append(next_state)

        return states
