from abc import ABC, abstractmethod
import math

MONTH_IN_YEAR = 12
DAYS_IN_MONTH = 30
HOURS_IN_DAY = 24
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60


class CostComponent(ABC):
    def __init__(self, number_of_clients, number_of_cameras_per_client):
        self.number_of_clients = number_of_clients
        self.number_of_cameras_per_client = number_of_cameras_per_client
        self.total_number_of_cameras = (
            self.number_of_clients * self.number_of_cameras_per_client
        )

    @abstractmethod
    def get_avg_daily_price(self):
        pass

    @abstractmethod
    def get_avg_monthly_price(self):
        pass

    @abstractmethod
    def get_worst_daily_price(self):
        pass

    @abstractmethod
    def get_worst_monthly_price(self):
        pass


class MarketingCost(CostComponent):
    def __init__(self, number_of_clients, number_of_cameras_per_client):
        # Call the superclass constructor with the necessary parameters
        super().__init__(number_of_clients, number_of_cameras_per_client)
        # Online Advertising (Google/Facebook)
        self.online_advertising_price_per_day = 100
        self.online_advertising_days_in_month = 10

        # Influencer Marketing
        self.influencer_marketing_price_per_day = 150
        self.influencer_marketing_days_in_month = 5

        # Email Campaigns
        self.email_campaigns_price_per_day = 20
        self.email_campaigns_days_in_month = 20

        # SEO
        self.seo_price_per_day = 30
        self.seo_days_in_month = 30

        # Content Marketing (Blogs/Videos)
        self.content_marketing_price_per_day = 50
        self.content_marketing_days_in_month = 15

    def get_avg_daily_price(self):
        return (
            (
                self.online_advertising_price_per_day
                * self.online_advertising_days_in_month
                + self.influencer_marketing_price_per_day
                * self.influencer_marketing_days_in_month
                + self.email_campaigns_price_per_day
                * self.email_campaigns_days_in_month
                + self.seo_price_per_day * self.seo_days_in_month
                + self.content_marketing_price_per_day
                * self.content_marketing_days_in_month
            )
        ) / DAYS_IN_MONTH

    def get_avg_monthly_price(self):
        return self.get_avg_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self, marketing_days_in_month=DAYS_IN_MONTH):
        return (
            (
                self.online_advertising_price_per_day * marketing_days_in_month
                + self.influencer_marketing_price_per_day * marketing_days_in_month
                + self.email_campaigns_price_per_day * marketing_days_in_month
                + self.seo_price_per_day * marketing_days_in_month
                + self.content_marketing_price_per_day * marketing_days_in_month
            )
        ) / DAYS_IN_MONTH

    def get_worst_monthly_price(self):
        return self.get_worst_daily_price() * DAYS_IN_MONTH


class WebsiteCost(CostComponent):
    def __init__(
        self, number_of_clients, number_of_cameras_per_client, domain_yearly_price=55
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.domain_yearly_price = domain_yearly_price

    def get_daily_price(self):
        days_in_year = DAYS_IN_MONTH * MONTH_IN_YEAR
        return self.domain_yearly_price / days_in_year

    def get_avg_daily_price(self):
        return self.get_daily_price()

    def get_avg_monthly_price(self):
        return self.get_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self):
        return self.get_avg_daily_price()

    def get_worst_monthly_price(self):
        return self.get_avg_monthly_price()


class WhatsAppCost(CostComponent):
    def __init__(self, number_of_clients, number_of_cameras_per_client):
        # Call the superclass constructor with the necessary parameters
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.utility_conversation_price = 0.0053
        self.utility_message_price = 0.005
        self.avg_alerts_per_camera_per_day = 1
        self.worst_alerts_per_camera_per_day = 1 * HOURS_IN_DAY

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


class AWSCost(CostComponent):
    def __init__(self, number_of_clients, number_of_cameras_per_client):
        # Call the superclass constructor with the necessary parameters
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.avg_storage_cost = 10
        self.avg_data_transfer_cost = 15
        self.worst_storage_cost = 50
        self.worst_data_transfer_cost = 100

    def get_avg_daily_price(self):
        return (self.avg_storage_cost + self.avg_data_transfer_cost) / DAYS_IN_MONTH

    def get_avg_monthly_price(self):
        return self.avg_storage_cost + self.avg_data_transfer_cost

    def get_worst_daily_price(self):
        return (self.worst_storage_cost + self.worst_data_transfer_cost) / DAYS_IN_MONTH

    def get_worst_monthly_price(self):
        return self.worst_storage_cost + self.worst_data_transfer_cost


class GPUPerHourCost(CostComponent):
    def __init__(
        self,
        number_of_clients,
        number_of_cameras_per_client,
        _model_name,
        _avg_working_hours=HOURS_IN_DAY,
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.model_name = _model_name
        self.target_gpu_cost_per_hour = 0.37
        self.number_of_parallel_workers = 10
        self.avg_working_hours = _avg_working_hours

    def get_avg_daily_price(self):
        number_of_instances = math.ceil(self.total_number_of_cameras / self.number_of_parallel_workers)
        return number_of_instances * self.target_gpu_cost_per_hour * self.avg_working_hours

    def get_avg_monthly_price(self):
        return self.get_avg_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self):
        number_of_instances = math.ceil(self.total_number_of_cameras / self.number_of_parallel_workers)
        return number_of_instances * self.target_gpu_cost_per_hour * HOURS_IN_DAY

    def get_worst_monthly_price(self):
        return self.get_worst_daily_price() * DAYS_IN_MONTH



class GeminiCost(CostComponent):
    def __init__(
        self,
        number_of_clients,
        number_of_cameras_per_client,
        _model_name,
        _avg_working_hours=HOURS_IN_DAY,
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.model_name = _model_name
        self.price_per_image = self.get_price_per_image()
        self.avg_working_hours = _avg_working_hours

    def get_price_per_image(self):
        if self.model_name == "Gemini_1.5_Flash":
            return 0.00002
        else:
            raise NotImplemented("get_price_per_image")

    def calculate_daily_cost_per_camera(self, working_hours, image_per_hour):

        price_per_hour = image_per_hour * self.price_per_image
        daily_cost = price_per_hour * working_hours
        return daily_cost

    def get_avg_daily_price(self):
        image_per_hour = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        return (
            self.calculate_daily_cost_per_camera(
                working_hours=self.avg_working_hours, image_per_hour=image_per_hour
            )
            * self.total_number_of_cameras
        )

    def get_avg_monthly_price(self):
        return self.get_avg_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self):
        image_per_hour = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        return (
            self.calculate_daily_cost_per_camera(
                working_hours=HOURS_IN_DAY, image_per_hour=image_per_hour
            )
            * self.total_number_of_cameras
        )

    def get_worst_monthly_price(self):
        return self.get_worst_daily_price() * DAYS_IN_MONTH


class GPTCost(CostComponent):
    def __init__(
        self,
        number_of_clients,
        number_of_cameras_per_client,
        _model_name,
        _cost_per_million_tokens,
        _avg_working_hours=HOURS_IN_DAY,
        _image_size=(512, 512),
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.image_size = _image_size
        self.model_name = _model_name
        self.cost_per_million_tokens = _cost_per_million_tokens
        self.tokens_per_image = self.get_tokens_per_image()
        self.avg_working_hours = _avg_working_hours

    def get_tokens_per_image(self):
        if self.model_name == "gpt-4o-mini-2024-07-18" and self.image_size == (
            512,
            512,
        ):
            return 8500
        else:
            raise NotImplemented("get_tokens_per_image")

    def get_cost_per_token(self):
        return self.cost_per_million_tokens / 1_000_000

    def calculate_daily_cost_per_camera(self, working_hours, image_per_hour):
        tokens_per_hour = image_per_hour * self.tokens_per_image
        tokens_per_day = tokens_per_hour * working_hours
        cost_per_token = self.get_cost_per_token()
        daily_cost = tokens_per_day * cost_per_token
        return daily_cost

    def get_avg_daily_price(self):
        image_per_hour = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        return (
            self.calculate_daily_cost_per_camera(
                working_hours=self.avg_working_hours, image_per_hour=image_per_hour
            )
            * self.total_number_of_cameras
        )

    def get_avg_monthly_price(self):
        return self.get_avg_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self):
        image_per_hour = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        return (
            self.calculate_daily_cost_per_camera(
                working_hours=HOURS_IN_DAY, image_per_hour=image_per_hour
            )
            * self.total_number_of_cameras
        )

    def get_worst_monthly_price(self):
        return self.get_worst_daily_price() * DAYS_IN_MONTH


class ClaudeCost(CostComponent):
    def __init__(
        self,
        number_of_clients,
        number_of_cameras_per_client,
        _model_name,
        _cost_per_million_tokens,
        _avg_working_hours=HOURS_IN_DAY,
        _image_size=(512, 512),
    ):
        super().__init__(number_of_clients, number_of_cameras_per_client)
        self.image_size = _image_size
        self.model_name = _model_name
        self.cost_per_million_tokens = _cost_per_million_tokens
        self.tokens_per_image = self.get_tokens_per_image()
        self.avg_working_hours = _avg_working_hours

    def get_tokens_per_image(self):
        # https://docs.anthropic.com/en/docs/build-with-claude/vision
        if self.model_name == "claude-3-5-sonnet-20240620":
            return self.image_size[0] * self.image_size[1] / 750
        else:
            raise NotImplemented("get_tokens_per_image")

    def get_cost_per_token(self):
        return self.cost_per_million_tokens / 1_000_000

    def calculate_daily_cost_per_camera(self, working_hours, image_per_hour):
        tokens_per_hour = image_per_hour * self.tokens_per_image
        tokens_per_day = tokens_per_hour * working_hours
        cost_per_token = self.get_cost_per_token()
        daily_cost = tokens_per_day * cost_per_token
        return daily_cost

    def get_avg_daily_price(self):
        image_per_hour = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        return (
            self.calculate_daily_cost_per_camera(
                working_hours=self.avg_working_hours, image_per_hour=image_per_hour
            )
            * self.total_number_of_cameras
        )

    def get_avg_monthly_price(self):
        return self.get_avg_daily_price() * DAYS_IN_MONTH

    def get_worst_daily_price(self):
        image_per_hour = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        return (
            self.calculate_daily_cost_per_camera(
                working_hours=HOURS_IN_DAY, image_per_hour=image_per_hour
            )
            * self.total_number_of_cameras
        )

    def get_worst_monthly_price(self):
        return self.get_worst_daily_price() * DAYS_IN_MONTH


class StartupCostCalculator:
    def __init__(self, _number_of_clients, _number_of_cameras_per_client):
        self.number_of_clients = _number_of_clients
        self.number_of_cameras_per_client = _number_of_cameras_per_client
        self.number_of_cameras_per_client = _number_of_cameras_per_client
        # self.marketing = MarketingCost(
        #     number_of_clients=self.number_of_clients,
        #     number_of_cameras_per_client=self.number_of_cameras_per_client,
        # )
        self.whatsapp = WhatsAppCost(
            number_of_clients=self.number_of_clients,
            number_of_cameras_per_client=self.number_of_cameras_per_client,
        )
        self.website = WebsiteCost(
            number_of_clients=self.number_of_clients,
            number_of_cameras_per_client=self.number_of_cameras_per_client,
        )
        # self.aws = AWSCost(
        #     number_of_clients=self.number_of_clients,
        #     number_of_cameras_per_client=self.number_of_cameras_per_client,
        # )
        # self.llm = GPTCost(
        #     number_of_clients=self.number_of_clients,
        #     number_of_cameras_per_client=self.number_of_cameras_per_client,
        #     _model_name="gpt-4o-mini-2024-07-18",
        #     _cost_per_million_tokens=0.15,
        #     _avg_working_hours=12,
        #     _image_size=(512, 512),
        # )
        # self.llm = ClaudeCost(
        #     number_of_clients=self.number_of_clients,
        #     number_of_cameras_per_client=self.number_of_cameras_per_client,
        #     _model_name="claude-3-5-sonnet-20240620",
        #     _cost_per_million_tokens=3,
        #     _avg_working_hours=12,
        #     _image_size=(512, 512),
        # )
        # self.llm = GeminiCost(
        #     number_of_clients=self.number_of_clients,
        #     number_of_cameras_per_client=self.number_of_cameras_per_client,
        #     _model_name="Gemini_1.5_Flash",
        #     _avg_working_hours=12,
        # )
        self.llm = GPUPerHourCost(
            number_of_clients=self.number_of_clients,
            number_of_cameras_per_client=self.number_of_cameras_per_client,
            _model_name="openbmb/MiniCPM-V-2_6-int4",
            _avg_working_hours=12,
        )

    def generate_cost_report(self):
        report = "Startup Cost Estimate Report\n"
        report += "-" * 40 + "\n"

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

                # Generate the report lines with two decimal places
                report += f"{component_name} Costs:\n"
                report += f"  Average Monthly Cost: ${avg_monthly_price:.2f}\n"
                report += f"  Worst Case Monthly Cost: ${worst_monthly_price:.2f}\n"
                report += f"  Average Daily Cost: ${avg_daily_price:.2f}\n"
                report += f"  Worst Case Daily Cost: ${worst_daily_price:.2f}\n"
                report += "-" * 40 + "\n"

        # Add total costs to the report
        report += "Total Costs:\n"
        report += f"  Total Average Monthly Cost: ${total_avg_monthly_cost:.2f}\n"
        report += f"  Total Worst Case Monthly Cost: ${total_worst_monthly_cost:.2f}\n"
        report += f"  Total Average Daily Cost: ${total_avg_daily_cost:.2f}\n"
        report += f"  Total Worst Case Daily Cost: ${total_worst_daily_cost:.2f}\n"
        report += "-" * 40 + "\n"

        total_number_of_cameras = (
            self.number_of_clients * self.number_of_cameras_per_client
        )
        report += "Cost per Camera:\n"
        report += f"  Total Average Monthly Cost: ${total_avg_monthly_cost / total_number_of_cameras:.2f}\n"
        report += f"  Total Worst Case Monthly Cost: ${total_worst_monthly_cost / total_number_of_cameras:.2f}\n"
        report += f"  Total Average Daily Cost: ${total_avg_daily_cost / total_number_of_cameras:.2f}\n"
        report += f"  Total Worst Case Daily Cost: ${total_worst_daily_cost / total_number_of_cameras:.2f}\n"
        report += "-" * 40 + "\n"

        return report


def main():
    number_of_clients = 2
    number_of_cameras_per_client = 10
    calculator = StartupCostCalculator(
        _number_of_clients=number_of_clients,
        _number_of_cameras_per_client=number_of_cameras_per_client,
    )
    cost_report = calculator.generate_cost_report()
    print(cost_report)


if __name__ == "__main__":
    main()
