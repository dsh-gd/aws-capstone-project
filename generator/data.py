# generator/data.py
# Data generation functions.

import random
from argparse import Namespace
from datetime import datetime, timedelta

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


def generate_flow(params: Namespace, user_id: str, items_ids: list) -> list:
    """Generate a list of actions in one flow for a specific user.

    Args:
        params (Namespace): Input parameters for operations.
        user_id (str): Id of a user.
        items_ids (list): Ids of all possible items.

    Returns:
        The list of actions for the flow.
    """
    mc = MarkovChain(
        params.action_types, params.initial_state, params.final_state
    )
    action_types = mc.generate_states() + [None]

    start_date = datetime.fromisoformat(params.start_date)
    end_date = datetime.fromisoformat(params.end_date)
    start_time = fake.date_time_between(
        start_date=start_date, end_date=end_date
    )

    was_logged_in = True
    found_item_id = None
    cart = []

    actions = []
    for current_type, next_type in zip(action_types, action_types[1:]):
        end_time = start_time + timedelta(minutes=15)
        t = fake.date_time_between(start_date=start_time, end_date=end_time)
        event_time = t.strftime("%Y-%m-%d %H:%M:%S")
        start_time = t + timedelta(minutes=1)

        item_id = random.choice(items_ids)
        id_to_remove = None

        if current_type == "log_in":
            code = 200
            was_logged_in = False
        elif current_type == "open_store":
            code = 100 if was_logged_in else 200
            was_logged_in = True
        elif current_type == "search_item":
            if next_type in ("open_store", "view_cart"):
                code = random.choice([200, 204, 404])
            else:
                found_item_id = item_id
                code = 200
        elif current_type == "add_to_cart":
            cart.append(found_item_id)
            code = 200
        elif current_type == "view_cart":
            code = 200 if cart else 204
        elif current_type == "remove_from_cart":
            id_to_remove = None
            if cart:
                id_to_remove = random.choice(cart)
                cart.remove(id_to_remove)
                code = 200
            else:
                code = 405
        elif current_type == "pay":
            if cart:
                code = int(
                    np.random.choice([200, 400, 402], p=[0.9, 0.05, 0.05])
                )
            else:
                code = 405
        elif current_type == "log_out":
            code = 200

        args = {
            "user_id": user_id,
            "item_id": item_id,
            "found_item_id": found_item_id,
            "cart": cart,
            "id_to_remove": id_to_remove,
        }
        action_results = params.action_results[current_type]
        result = action_results[str(code)].format(**args)

        action = {
            "event_time": event_time,
            "user_id": user_id,
            "action_type": current_type,
            "action_result": result,
            "status_code": code,
        }
        actions.append(action)

        if random.random() <= 0.005:
            break

    return actions


def generate_user_actions(
    params: Namespace, user_ids: list, items_ids: list, size: int = 1000
) -> list:
    """Generate a list of user actions.

    Args:
        params (Namespace): Input parameters for operations.
        user_ids (list): Ids of all possible users.
        items_ids (list): Ids of all possible items.
        size (int): The number of actions in the list. (Default is 1000)

    Returns:
        The list of user actions.
    """
    user_actions = []
    while len(user_actions) < size:
        user_id = random.choice(user_ids)
        actions = generate_flow(params, user_id, items_ids)
        user_actions.extend(actions)
    return user_actions
