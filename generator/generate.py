import random
from datetime import datetime, timedelta

import numpy as np
from faker import Faker

ITEM_TYPES = ["office", "game", "photography", "fitness"]

ACTION_TYPES = {
    "start": {"log_in": 0.5, "open_store": 0.5},
    "log_in": {"open_store": 1.0},
    "open_store": {"search_item": 0.85, "view_cart": 0.15},
    "search_item": {"add_to_cart": 0.6, "open_store": 0.3, "view_cart": 0.1},
    "add_to_cart": {"view_cart": 0.6, "open_store": 0.4},
    "view_cart": {"pay": 0.4, "open_store": 0.4, "remove_from_cart": 0.2},
    "remove_from_cart": {"view_cart": 0.8, "open_store": 0.2},
    "pay": {"log_out": 0.7, "stop": 0.3},
    "log_out": {"stop": 1.0},
}


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


class DataGenerator:
    """A data generator class."""

    def __init__(
        self,
        item_types: list,
        transition_probs: dict,
        pfi: float = 0.05,
        initial_state: str = "start",
        final_state: str = "stop",
    ):
        """
        Args:
            item_types (list): The predefined set of item types.
            transition_probs (dict): The transition probabilities in Markov Chain for the predefined set of action types.
            pfi (float): Percentage of free items. (Default is 0.05)
            initial_state (str): The initial state in Markov Chain. (Default is "start")
            final_state (str): The final state in Markov Chain. (Default is "stop")
        """
        self.fake = Faker()
        self.item_types = item_types
        self.transition_probs = transition_probs
        self.pfi = pfi
        self.initial_state = initial_state
        self.final_state = final_state
        self.start_date = datetime.fromisoformat("2021-01-01")
        self.end_date = self.start_date + timedelta(days=365)

    def generate_items(self, size: int = 1000) -> list:
        """Generate a list of items.

        Args:
            size (int): The number of items in the list. (Default is 1000)

        Returns:
            The list of items.
        """
        n_free = int(size * self.pfi)
        idxs = np.arange(size)
        np.random.shuffle(idxs)
        free_idxs = idxs[:n_free]

        prices = random_pareto(size, lower=0.01, upper=50)
        prices = prices.round(decimals=2)
        prices[free_idxs] = 0.0

        discounts = random_pareto(size, lower=0, upper=100)
        discounts = discounts.round(decimals=0)
        discounts[free_idxs] = 0.0

        items = []
        for i in range(size):
            id_ = self.fake.uuid4()
            nb_words = random.randint(1, 3)
            name = self.fake.sentence(nb_words).rstrip(".")
            desc = self.fake.sentence()
            type_ = random.choice(self.item_types)
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

    def __next_state(self, current_state: str) -> str:
        """Generate the next state (action type) in Markov Chain.

        Args:
            current_state (str): The current state in Markov Chain.

        Returns:
            The next state in Markov Chain.
        """
        possible_states = list(self.transition_probs[current_state].keys())
        p = list(self.transition_probs[current_state].values())
        return np.random.choice(possible_states, p=p)

    def __generate_states(self) -> list:
        """Generate a list of states (action types) for the flow.

        Returns:
            The list of consecutive states.
        """
        current_state = self.initial_state

        states = []
        while True:
            next_state = self.__next_state(current_state)
            current_state = next_state

            if current_state == self.final_state:
                break

            states.append(next_state)

        return states

    def __generate_flow(self, user_id: str, items_ids: list) -> list:
        """Generate a list of actions in one flow for a specific user.

        Args:
            user_id (str): Id of a user.
            items_ids (list): Ids of all possible items.

        Returns:
            The list of actions for the flow.
        """
        action_types = self.__generate_states()
        start_time = self.fake.date_time_between(
            start_date=self.start_date, end_date=self.end_date
        )

        was_logged_in = True
        found_item_id = None
        cart = []

        actions = []
        for i, action_type in enumerate(action_types):
            end_time = start_time + timedelta(minutes=15)
            t = self.fake.date_time_between(
                start_date=start_time, end_date=end_time
            )
            event_time = t.strftime("%Y-%m-%d %H:%M:%S")
            start_time = t + timedelta(minutes=1)

            item_id = random.choice(items_ids)

            if action_type == "log_in":
                action_result = f"User {user_id} logged in."
                status_code = 200
                was_logged_in = False
            elif action_type == "open_store":
                if was_logged_in:
                    action_result = (
                        f"User {user_id} was logged in. Keep buying."
                    )
                    status_code = 100
                else:
                    action_result = (
                        f"User {user_id} was not logged in. Start buying."
                    )
                    status_code = 200
                was_logged_in = True
            elif action_type == "search_item":
                if action_types[i + 1 :] and action_types[i + 1] in (
                    "open_store",
                    "view_cart",
                ):
                    variants = (
                        ("Item not found.", 404),
                        (f"Item {item_id} not available.", 204),
                        (f"Item {item_id} available.", 200),
                    )
                    action_result, status_code = random.choice(variants)
                else:
                    found_item_id = item_id
                    action_result = f"Item {item_id} available."
                    status_code = 200
            elif action_type == "add_to_cart":
                action_result = f"Add item {found_item_id} to cart."
                status_code = 200
                cart.append(found_item_id)
            elif action_type == "view_cart":
                action_result = str(cart)
                if cart:
                    status_code = 200
                else:
                    status_code = 204
            elif action_type == "remove_from_cart":
                if cart:
                    id_to_remove = random.choice(cart)
                    cart.remove(id_to_remove)
                    action_result = f"Item {id_to_remove} removed from cart."
                    status_code = 200
                else:
                    action_result = "Cart is empty."
                    status_code = 405
            elif action_type == "pay":
                if cart:
                    if random.random() <= 0.9:
                        action_result = "Payment successful."
                        status_code = 200
                    else:
                        action_result = "Payment failed."
                        status_code = random.choice([400, 402])
                else:
                    action_result = "Payment failed. Cart is empty."
                    status_code = 405
            elif action_type == "log_out":
                action_result = f"User {user_id} logged out."
                status_code = 200

            action = {
                "event_time": event_time,
                "user_id": user_id,
                "action_type": action_type,
                "action_result": action_result,
                "status_code": status_code,
            }

            actions.append(action)

            if random.random() <= 0.005:
                break

        return actions

    def generate_user_actions(self, items_ids: list, size: int = 1000) -> list:
        """Generate a list of user actions.

        Args:
            items_ids (list): Ids of all possible items.
            size (int): The number of actions in the list. (Default is 1000)

        Returns:
            The list of user actions.
        """
        n_ids = size // 3
        user_ids = [self.fake.uuid4() for _ in range(n_ids)]

        user_actions = []
        while len(user_actions) < size:
            user_id = random.choice(user_ids)
            actions = self.__generate_flow(user_id, items_ids)
            user_actions.extend(actions)

        return user_actions
