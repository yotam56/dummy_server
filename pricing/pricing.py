class TokenCostCalculator:
    def __init__(self, tokens_per_second, suppliers_costs):
        """
        Initialize the TokenCostCalculator with tokens per second and a dictionary of supplier costs.

        :param tokens_per_second: Number of tokens sent per second.
        :param suppliers_costs: Dictionary with supplier names as keys and cost per million tokens as values.
        """
        self.tokens_per_second = tokens_per_second
        self.suppliers_costs = suppliers_costs

    def calculate_daily_cost(self, cost_per_million_tokens):
        """
        Calculate the daily cost based on the cost per million tokens.

        :param cost_per_million_tokens: Cost per million tokens for a supplier.
        :return: Calculated daily cost.
        """
        tokens_per_day = self.tokens_per_second * 60 * 60 * 24
        cost_per_token = cost_per_million_tokens / 1_000_000
        daily_cost = tokens_per_day * cost_per_token
        return daily_cost

    def calculate_monthly_cost(self, daily_cost, days_in_month=30):
        """
        Calculate the monthly cost based on the daily cost.

        :param daily_cost: Calculated daily cost.
        :param days_in_month: Number of days in the month.
        :return: Calculated monthly cost.
        """
        monthly_cost = daily_cost * days_in_month
        return monthly_cost

    def display_costs(self, days_in_month=30):
        """
        Iterate over the suppliers and print out their daily and monthly costs.

        :param days_in_month: Number of days in the month.
        """
        for supplier, cost_per_million_tokens in self.suppliers_costs.items():
            daily_cost = self.calculate_daily_cost(cost_per_million_tokens)
            monthly_cost = self.calculate_monthly_cost(daily_cost, days_in_month)

            print(f"Supplier: {supplier}")
            print(f"  Daily Cost: ${daily_cost:.2f}")
            print(f"  Monthly Cost (for {days_in_month} days): ${monthly_cost:.2f}")
            print("-" * 40)


class TokenCostCalculator:
    def __init__(self, tokens_per_second, suppliers_info):
        """
        Initialize the TokenCostCalculator with tokens per second and a dictionary of supplier information.

        :param tokens_per_second: Number of tokens sent per second.
        :param suppliers_info: Dictionary with supplier names as keys and another dictionary containing
                               'model_name' and 'cost_per_million_tokens' as values.
        """
        self.tokens_per_second = tokens_per_second
        self.suppliers_info = suppliers_info

    def calculate_daily_cost(self, cost_per_million_tokens):
        """
        Calculate the daily cost based on the cost per million tokens.

        :param cost_per_million_tokens: Cost per million tokens for a supplier.
        :return: Calculated daily cost.
        """
        tokens_per_day = self.tokens_per_second * 60 * 60 * 12
        cost_per_token = cost_per_million_tokens / 1_000_000
        daily_cost = tokens_per_day * cost_per_token
        return daily_cost

    def calculate_monthly_cost(self, daily_cost, days_in_month=30):
        """
        Calculate the monthly cost based on the daily cost.

        :param daily_cost: Calculated daily cost.
        :param days_in_month: Number of days in the month.
        :return: Calculated monthly cost.
        """
        monthly_cost = daily_cost * days_in_month
        return monthly_cost

    def display_costs(self, days_in_month=30):
        """
        Iterate over the suppliers and print out their daily and monthly costs along with the model name.

        :param days_in_month: Number of days in the month.
        """
        for supplier, info in self.suppliers_info.items():
            model_name = info.get('model_name')
            cost_per_million_tokens = info.get('cost_per_million_tokens')

            daily_cost = self.calculate_daily_cost(cost_per_million_tokens)
            monthly_cost = self.calculate_monthly_cost(daily_cost, days_in_month)

            print(f"Supplier: {supplier}")
            print(f"  Model Name: {model_name}")
            print(f"  Daily Cost: ${daily_cost:.2f}")
            print(f"  Monthly Cost (for {days_in_month} days): ${monthly_cost:.2f}")
            print("-" * 40)


# Example usage:
if __name__ == "__main__":
    tokens_per_second = 50  # Set the number of tokens sent per second

    suppliers_info = {
        "OpenAI-GPT-4O": {
            "model_name": "gpt-4o-2024-08-06",
            "cost_per_million_tokens": 2.5
        },
        "OpenAI-GPT-4O-MINI": {
            "model_name": "gpt-4o-mini-2024-07-18",
            "cost_per_million_tokens": 0.15
        },
        "Replicate": {
            "model_name": "meta/meta-llama-3-8b",
            "cost_per_million_tokens": 0.05
        },
        "together.ai": {
            "model_name": "meta/meta-llama-3-8b-turbo",
            "cost_per_million_tokens": 0.18
        },
        "AWS-bedrock1": {
            "model_name": "Claude 3.5 Sonnet",
            "cost_per_million_tokens": 3
        },
        "AWS-bedrock2": {
            "model_name": "Llama 3.1 Instruct (8B)",
            "cost_per_million_tokens": 0.22
        },
        "Groq": {
            "model_name": "llama-3-8b",
            "cost_per_million_tokens": 0.05
        },
    }

    calculator = TokenCostCalculator(tokens_per_second, suppliers_info)
    calculator.display_costs()
