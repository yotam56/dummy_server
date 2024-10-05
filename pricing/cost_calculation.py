import dataclasses
from abc import ABC, abstractmethod
import pandas as pd

MONTH_IN_YEAR = 12
DAYS_IN_MONTH = 30
HOURS_IN_DAY = 24
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60


@dataclasses.dataclass
class TextCount:
    system_prompt_image_description_input_tokens: float = 35 * 1.1
    system_prompt_llm_analysis_input_tokens: float = 147 * 1.1
    user_prompt_question_input_tokens: float = 10 * 1.1
    image_description_output_tokens: float = 63 * 1.1
    final_json_output_tokens: float = 51 * 1.1

    system_prompt_image_description_input_char: float = 186 * 1.1
    system_prompt_llm_analysis_input_char: float = 566 * 1.1
    user_prompt_question_input_char: float = 49 * 1.1
    image_description_output_char: float = 319 * 1.1
    final_json_output_char: float = 239 * 1.1

    def total_input_tokens(self) -> float:
        return (self.image_description_output_tokens + self.system_prompt_llm_analysis_input_tokens
                + self.user_prompt_question_input_tokens + self.image_description_output_tokens)

    def total_output_tokens(self) -> float:
        return self.system_prompt_image_description_input_tokens + self.final_json_output_tokens

    def total_input_char(self) -> float:
        return (self.image_description_output_char + self.system_prompt_llm_analysis_input_char
                + self.user_prompt_question_input_char + self.image_description_output_char)

    def total_output_char(self) -> float:
        return self.system_prompt_image_description_input_char + self.final_json_output_char


text_count = TextCount()


class CostComponent(ABC):
    def __init__(self, number_of_clients, number_of_cameras_per_client):
        self.number_of_clients = number_of_clients
        self.number_of_cameras_per_client = number_of_cameras_per_client
        self.total_number_of_cameras = (
                self.number_of_clients * self.number_of_cameras_per_client
        )

    @abstractmethod
    def get_price_per_hour(self):
        pass

    def get_worst_daily_price(self):
        return self.get_price_per_hour() * HOURS_IN_DAY

    def get_avg_daily_price(self):
        return self.get_price_per_hour() * HOURS_IN_DAY / 2

    def get_avg_monthly_price(self):
        return self.get_price_per_hour() * HOURS_IN_DAY * DAYS_IN_MONTH

    def get_worst_monthly_price(self):
        return self.get_price_per_hour() * (HOURS_IN_DAY / 2) * DAYS_IN_MONTH


class WebsiteCost(CostComponent):
    def __init__(
            self, number_of_clients, number_of_cameras_per_client, domain_yearly_price=55
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.domain_yearly_price = domain_yearly_price

    def get_price_per_hour(self):
        hours_in_year = HOURS_IN_DAY * DAYS_IN_MONTH * MONTH_IN_YEAR
        return self.domain_yearly_price / hours_in_year


class WhatsAppCost(CostComponent):
    def __init__(self, number_of_clients, number_of_cameras_per_client):
        # Call the superclass constructor with the necessary parameters
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.utility_conversation_price = 0.0053
        self.utility_message_price = 0.005
        self.avg_alerts_per_camera_per_day = 1
        self.worst_alerts_per_camera_per_day = 1 * HOURS_IN_DAY

    def get_price_per_hour(self):
        self.get_worst_daily_price() / HOURS_IN_DAY

    def get_daily_price(self, alerts_per_camera_per_day):
        conversation_price = (
                self.utility_conversation_price * self.number_of_clients
        )  # A single conversion per a day per client.
        message_price = (
                self.utility_message_price
                * alerts_per_camera_per_day
                * self.total_number_of_cameras
        )
        return conversation_price + message_price

    def get_avg_daily_price(self):
        return self.get_daily_price(self.avg_alerts_per_camera_per_day)

    def get_avg_monthly_price(self):
        return self.get_avg_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self):
        return self.get_daily_price(self.worst_alerts_per_camera_per_day)

    def get_worst_monthly_price(self):
        return self.get_worst_daily_price() * DAYS_IN_MONTH


# class AWSCost(CostComponent):
#     def __init__(self, number_of_clients, number_of_cameras_per_client):
#         super().__init__(number_of_clients, number_of_cameras_per_client)
#         self.single_eks_cluster_cost_per_hour = 0.01
#         self.one_giga_ecr_cost_per_hour = 0.1 / (DAYS_IN_MONTH * HOURS_IN_DAY)
#         self.data_transfer = "not implemented"
#
#     def get_price_per_hour(self):
#         return self.single_request_price * SECONDS_IN_MINUTE * MINUTES_IN_HOUR * self.total_number_of_cameras


class Gemini(CostComponent):
    def __init__(
            self,
            number_of_clients,
            number_of_cameras_per_client,
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.image_size = "Not Relevant"
        self.model_name = "Gemini 1.5 Flash"
        self.cost_per_image = 0.00002
        self.cost_per_input_char = 0.00001875 / 1000
        self.cost_per_output_char = 0.000075 / 1000
        self.single_request_price = self.get_price_per_single_request()

    def get_price_per_single_request(self) -> float:
        input_price = text_count.total_input_char() * self.cost_per_input_char
        output_price = text_count.total_output_char() * self.cost_per_output_char
        return input_price + output_price + self.cost_per_image

    def get_price_per_hour(self):
        return self.single_request_price * SECONDS_IN_MINUTE * MINUTES_IN_HOUR * self.total_number_of_cameras



class GPT4O(CostComponent):
    def __init__(
            self,
            number_of_clients,
            number_of_cameras_per_client,
            low_resolution=False,
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.low_resolution = low_resolution
        self.image_size = (512, 512)
        self.model_name = "gpt-4o-2024-08-06"
        self.cost_per_input_token = 2.5 / 1_000_000
        self.cost_per_output_token = 10 / 1_000_000
        self.tokens_per_image = self.get_tokens_per_image()
        self.single_request_price = self.get_price_per_single_request()

    def get_tokens_per_image(self):
        if self.low_resolution and self.image_size[0] <= 512 and self.image_size[1] <= 512:
            return 85
        if self.image_size[0] <= 512 and self.image_size[1] <= 512:
            base_token = 85
            title_token = 170
            total_token = base_token + title_token
            return total_token
        else:
            raise NotImplemented("get_tokens_per_image")

    def get_price_per_single_request(self) -> float:
        input_price = (text_count.total_input_tokens() + self.tokens_per_image) * self.cost_per_input_token
        output_price = text_count.total_output_tokens() * self.cost_per_output_token
        return input_price + output_price

    def get_price_per_hour(self):
        return self.single_request_price * SECONDS_IN_MINUTE * MINUTES_IN_HOUR * self.total_number_of_cameras


class GPT4OMini(CostComponent):
    def __init__(
            self,
            number_of_clients,
            number_of_cameras_per_client,
            low_resolution=False,
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.low_resolution = low_resolution
        self.image_size = (512, 512)
        self.model_name = "gpt-4o-mini-2024-07-18"
        self.cost_per_input_token = 0.15 / 1_000_000
        self.cost_per_output_token = 0.6 / 1_000_000
        self.tokens_per_image = self.get_tokens_per_image()
        self.single_request_price = self.get_price_per_single_request()

    def get_tokens_per_image(self):
        if self.low_resolution and self.image_size[0] <= 512 and self.image_size[1] <= 512:
            return 2833
        if self.image_size[0] <= 512 and self.image_size[1] <= 512:
            base_token = 2833
            title_token = 5667
            total_token = base_token + title_token
            return total_token
        else:
            raise NotImplemented("get_tokens_per_image")

    def get_price_per_single_request(self) -> float:
        input_price = (text_count.total_input_tokens() + self.tokens_per_image) * self.cost_per_input_token
        output_price = text_count.total_output_tokens() * self.cost_per_output_token
        return input_price + output_price

    def get_price_per_hour(self):
        return self.single_request_price * SECONDS_IN_MINUTE * MINUTES_IN_HOUR * self.total_number_of_cameras


class StartupCostCalculator:
    def __init__(self, number_of_clients, number_of_cameras_per_client, llm_class, low_resolution=False):
        self.number_of_clients = number_of_clients
        self.number_of_cameras_per_client = number_of_cameras_per_client
        self.low_resolution = low_resolution

        # Initialize the costs
        # self.marketing = self._initialize_cost(MarketingCost)
        self.whatsapp = self._initialize_cost(WhatsAppCost)
        self.website = self._initialize_cost(WebsiteCost)
        # self.aws = self._initialize_cost(AWSCost)
        self.llm = self._initialize_cost(llm_class)

    def _initialize_cost(self, CostClass):
        """Helper function to instantiate cost classes with shared parameters."""
        if CostClass in [GPT4O, GPT4OMini]:
            return CostClass(
                number_of_clients=self.number_of_clients,
                number_of_cameras_per_client=self.number_of_cameras_per_client,
                low_resolution=self.low_resolution
            )

        # Default instantiation for other classes
        return CostClass(
            number_of_clients=self.number_of_clients,
            number_of_cameras_per_client=self.number_of_cameras_per_client
        )

    def generate_cost_data(self):
        data = []
        total_avg_monthly_cost = 0
        total_worst_monthly_cost = 0

        total_avg_daily_cost = 0
        total_worst_daily_cost = 0

        # Iterate over class attributes and calculate total costs
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, CostComponent):
                # Get the class name without "Cost" suffix for a cleaner report
                component_name = attr_value.__class__.__name__.replace("Cost", "")

                # Get the costs
                avg_monthly_price = attr_value.get_avg_monthly_price()
                worst_monthly_price = attr_value.get_worst_monthly_price()
                avg_daily_price = attr_value.get_avg_daily_price()
                worst_daily_price = attr_value.get_worst_daily_price()

                # Accumulate the total costs
                total_avg_monthly_cost += avg_monthly_price
                total_worst_monthly_cost += worst_monthly_price
                total_avg_daily_cost += avg_daily_price
                total_worst_daily_cost += worst_daily_price

                # Append data to the list for the table
                data.append({
                    'Component': component_name,
                    'Avg Daily Cost': f"${avg_daily_price:.2f}",
                    'Worst Daily Cost': f"${worst_daily_price:.2f}",
                    'Avg Monthly Cost': f"${avg_monthly_price:.2f}",
                    'Worst Monthly Cost': f"${worst_monthly_price:.2f}",
                })

        # Add the totals as the last row
        data.append({
            'Component': 'Total',
            'Avg Daily Cost': f"${total_avg_daily_cost:.2f}",
            'Worst Daily Cost': f"${total_worst_daily_cost:.2f}",
            'Avg Monthly Cost': f"${total_avg_monthly_cost:.2f}",
            'Worst Monthly Cost': f"${total_worst_monthly_cost:.2f}",
        })

        # Add cost per camera information
        total_number_of_cameras = (
                self.number_of_clients * self.number_of_cameras_per_client
        )
        data.append({
            'Component': 'Cost per Camera',
            'Avg Daily Cost': f"${total_avg_daily_cost / total_number_of_cameras:.2f}",
            'Worst Daily Cost': f"${total_worst_daily_cost / total_number_of_cameras:.2f}",
            'Avg Monthly Cost': f"${total_avg_monthly_cost / total_number_of_cameras:.2f}",
            'Worst Monthly Cost': f"${total_worst_monthly_cost / total_number_of_cameras:.2f}",
            'Camera Per Hour Cost': f"${total_worst_daily_cost / total_number_of_cameras / HOURS_IN_DAY:.5f}",
        })

        return data

    def create_cost_csv(self, cost_data):

        # Create a DataFrame
        df = pd.DataFrame(cost_data)

        # Print the table
        # print(df)

        # Save the table to a CSV file
        df.to_csv('cost_report.csv', index=False)
        print("Cost report saved to 'cost_report.csv'")

    def generate_cost_report(self, cost_data):
        report = "Startup Cost Estimate Report\n"
        report += "-" * 40 + "\n"

        # Iterate over the data and format the report
        for row in cost_data:
            component_name = row['Component']
            report += f"{component_name} Costs:\n"

            # Iterate over key-value pairs, skipping 'Component'
            for key, value in row.items():
                if key != 'Component':
                    # Dynamically generate the report without explicitly writing key names
                    report += f"  {key}: {value}\n"

            report += "-" * 40 + "\n"

        return report


def main():
    calculator = StartupCostCalculator(
        number_of_clients=2,
        number_of_cameras_per_client=10,
        llm_class=GPT4OMini,  # Pass the LLM class
        low_resolution=True  # Optional argument for low-resolution LLMs
    )

    cost_data = calculator.generate_cost_data()
    cost_report = calculator.generate_cost_report(cost_data)
    print(cost_report)

    calculator.create_cost_csv(cost_data)


if __name__ == "__main__":
    main()
