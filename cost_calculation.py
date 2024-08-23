from abc import ABC, abstractmethod


class CostComponent(ABC):

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
    def __init__(self):
        # Online Advertising (Google/Facebook)
        self.online_advertising_price_per_day = 100  # Cost per day for Google/Facebook ads
        self.online_advertising_days_in_month = 10  # Days in month where online ads are active

        # Influencer Marketing
        self.influencer_marketing_price_per_day = 150  # Cost per day for influencer campaigns
        self.influencer_marketing_days_in_month = 5  # Days in month where influencer campaigns are active

        # Email Campaigns
        self.email_campaigns_price_per_day = 20  # Cost per day for email campaigns
        self.email_campaigns_days_in_month = 20  # Days in month where email campaigns are active

        # SEO
        self.seo_price_per_day = 30  # Cost per day for SEO optimization
        self.seo_days_in_month = 30  # Days in month where SEO optimization is active

        # Content Marketing (Blogs/Videos)
        self.content_marketing_price_per_day = 50  # Cost per day for content marketing
        self.content_marketing_days_in_month = 15  # Days in month where content marketing is active

    def get_avg_price(self):
        # Calculate total average cost by multiplying price per day by days active per month
        total_avg_price = (
            self.online_advertising_price_per_day * self.online_advertising_days_in_month
            + self.influencer_marketing_price_per_day * self.influencer_marketing_days_in_month
            + self.email_campaigns_price_per_day * self.email_campaigns_days_in_month
            + self.seo_price_per_day * self.seo_days_in_month
            + self.content_marketing_price_per_day * self.content_marketing_days_in_month
        )
        return total_avg_price

    def get_worst_price(self, default_days_in_month=30):
        # Worst-case scenario where all campaigns are assumed to run for the full 30 days in the month
        total_worst_price = (
            self.online_advertising_price_per_day * default_days_in_month
            + self.influencer_marketing_price_per_day * default_days_in_month
            + self.email_campaigns_price_per_day * default_days_in_month
            + self.seo_price_per_day * default_days_in_month
            + self.content_marketing_price_per_day * default_days_in_month
        )
        return total_worst_price


class WebsiteCost(CostComponent):
    def __init__(self, domain_yearly_price=55):
        self.domain_yearly_price = domain_yearly_price

    def get_avg_price(self):
        return self.domain_yearly_price

    def get_worst_price(self):
        return self.get_avg_price()


class WhatsAppCost(CostComponent):
    def __init__(self):
        self.avg_price = 5  # Average monthly WhatsApp cost
        self.worst_price = 20  # Worst-case monthly WhatsApp cost

    def get_avg_price(self):
        return self.avg_price

    def get_worst_price(self):
        return self.worst_price


# AWS cost class
class AWSCost(CostComponent):
    def __init__(self):
        self.avg_storage_cost = 10  # Average AWS storage cost
        self.avg_data_transfer_cost = 15  # Average AWS data transfer cost
        self.worst_storage_cost = 50  # Worst-case AWS storage cost
        self.worst_data_transfer_cost = 100  # Worst-case AWS data transfer cost

    def get_avg_price(self):
        # Total average AWS cost
        return self.avg_storage_cost + self.avg_data_transfer_cost

    def get_worst_price(self):
        # Total worst-case AWS cost
        return self.worst_storage_cost + self.worst_data_transfer_cost


# GPU cost class
class GPUCost(CostComponent):
    def __init__(self):
        self.avg_price = 200  # Average monthly GPU cost
        self.worst_price = 1000  # Worst-case monthly GPU cost

    def get_avg_price(self):
        return self.avg_price

    def get_worst_price(self):
        return self.worst_price

class LLMCost(CostComponent):
    def __init__(
        self,
        _model_name,
        _cost_per_million_tokens,
        _avg_working_hours=24,
        _image_per_second=1,
        _image_size=(512, 512),
    ):
        self._image_per_second = _image_per_second
        self.image_size = _image_size
        self.model_name = _model_name
        self.cost_per_million_tokens = _cost_per_million_tokens
        self.tokens_per_image = self.get_tokens_per_image()
        self.tokens_per_second = self._image_per_second * self.tokens_per_image
        self.avg_working_hours = _avg_working_hours

    def get_tokens_per_image(self):
        if self.model_name == "gpt-4o-mini-2024-07-18" and self.image_size == (
            512,
            512,
        ):
            return 8500

    def get_cost_per_token(self):
        return self.cost_per_million_tokens / 1_000_000

    def calculate_daily_cost(self, working_hours):
        tokens_per_day = self.tokens_per_second * 60 * 60 * working_hours
        cost_per_token = self.get_cost_per_token()
        daily_cost = tokens_per_day * cost_per_token
        return daily_cost

    def calculate_monthly_cost(self, daily_cost, days_in_month=30):
        return daily_cost * days_in_month

    def get_avg_price(self):
        daily_cost = self.calculate_daily_cost(working_hours=self.avg_working_hours)
        return self.calculate_monthly_cost(daily_cost)

    def get_worst_price(self):
        daily_cost = self.calculate_daily_cost(working_hours=24)
        return self.calculate_monthly_cost(daily_cost)


# Startup cost calculator class
class StartupCostCalculator:
    def __init__(self):
        self.number_of_clients = 2
        self.number_of_cameras_per_client = 10
        # self.camera = CameraCost()
        # self.marketing = MarketingCost()
        self.whatsapp = WhatsAppCost()
        self.aws = AWSCost()
        # self.gpu = GPUCost()
        self.llm = LLMCost(
            _model_name="gpt-4o-mini-2024-07-18",
            _cost_per_million_tokens=0.15,
            _avg_working_hours=12,
            _image_per_second=1,
            _image_size=(512, 512),
        )

    def generate_cost_report(self):
        report = "Startup Cost Estimate Report\n"
        report += "-" * 40 + "\n"

        total_avg_cost = 0
        total_worst_cost = 0

        # Iterate over class attributes and calculate total costs
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, CostComponent):
                # Get the class name without "Cost" suffix for a cleaner report
                component_name = attr_value.__class__.__name__.replace("Cost", "")

                # Get the costs
                avg_price = attr_value.get_avg_price()
                worst_price = attr_value.get_worst_price()

                # Accumulate the total costs
                total_avg_cost += avg_price
                total_worst_cost += worst_price

                # Generate the report lines with two decimal places
                report += f"{component_name} Costs:\n"
                report += f"  Average: ${avg_price:.2f}\n"
                report += f"  Worst Case: ${worst_price:.2f}\n"
                report += "-" * 40 + "\n"

        # Calculate total daily costs assuming 30 days in a month
        total_avg_daily_cost = total_avg_cost / 30
        total_worst_daily_cost = total_worst_cost / 30

        # Add total costs to the report
        report += "Total Costs:\n"
        report += f"  Total Average Monthly Cost: ${total_avg_cost:.2f}\n"
        report += f"  Total Worst Case Monthly Cost: ${total_worst_cost:.2f}\n"
        report += f"  Total Average Daily Cost: ${total_avg_daily_cost:.2f}\n"
        report += f"  Total Worst Case Daily Cost: ${total_worst_daily_cost:.2f}\n"
        report += "-" * 40 + "\n"

        return report


if __name__ == "__main__":
    calculator = StartupCostCalculator()
    cost_report = calculator.generate_cost_report()
    print(cost_report)
