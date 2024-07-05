import pandas as pd
from glob import glob


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def get_best_service(consumption_file_path, providers, kwh_price):
    print(consumption_file_path)
    df = pd.read_csv(consumption_file_path)
    df.columns = ['date', 'time', 'power_consumption']
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'].astype(str), format='%d/%m/%Y %H:%M')
    # Drop the original 'date' and 'time' columns
    df.drop(['date', 'time'], axis=1, inplace=True)

    # Set 'datetime' as the index
    df.set_index('datetime', inplace=True)
    # Extract day of the week and hour from the index
    df['day_of_week'] = df.index.day_name()
    df['hour'] = df.index.hour

    # Group by day of the week and hour, and then sum the power consumption
    aggregated_consumption = df.groupby(['day_of_week', 'hour'])['power_consumption'].sum().unstack()

    for provider_name, discount_df in providers.items():
        discounted_consumption = aggregated_consumption * discount_df
        total_discount = discounted_consumption.sum().sum() * kwh_price
        print(f"Total Discount for {provider_name}:", round(total_discount, 2))


def create_discount_table(discount_schedule, discount_percentage):
    """
    Create a discount table based on the given schedule and discount percentage.

    Parameters:
    - discount_schedule: dict, keys are work days and values are hour ranges in "HH:MM-HH:MM" format.
    - discount_percentage: float, the discount percentage to be applied.

    Returns:
    - discount_df: pd.DataFrame, discount table with 0% for non-discounted hours and the given discount percentage for discounted hours.
    """
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    discount_df = pd.DataFrame(0.0, index=days_of_week, columns=range(24))  # Initialize with 0% discount

    for day, hours in discount_schedule.items():
        start_hour, end_hour = hours.split('-')
        start_hour = int(start_hour.split(':')[0])
        end_hour = int(end_hour.split(':')[0])
        discount_df.loc[day, start_hour:end_hour - 1] = discount_percentage / 100.0

    return discount_df


def generate_discount_providers():
    providers = {}
    providers['Constant Discount 5%'] = create_discount_table(
        discount_schedule={'Sunday': '00:00-24:00',
                           'Monday': '00:00-24:00',
                           'Tuesday': '00:00-24:00',
                           'Wednesday': '00:00-24:00',
                           'Thursday': '00:00-24:00',
                           'Friday': '00:00-24:00',
                           'Saturday': '00:00-24:00'},
        discount_percentage=5)
    providers['Constant Discount 7%'] = create_discount_table(
        discount_schedule={'Sunday': '00:00-24:00',
                           'Monday': '00:00-24:00',
                           'Tuesday': '00:00-24:00',
                           'Wednesday': '00:00-24:00',
                           'Thursday': '00:00-24:00',
                           'Friday': '00:00-24:00',
                           'Saturday': '00:00-24:00'},
        discount_percentage=7)
    providers['Day saving 08:00-17:00 15%'] = create_discount_table(
        discount_schedule={'Sunday': '08:00-17:00',
                           'Monday': '08:00-17:00',
                           'Tuesday': '08:00-17:00',
                           'Wednesday': '08:00-17:00',
                           'Thursday': '08:00-17:00'},
        discount_percentage=15)
    providers['Night saving 00:00-06:00 20%'] = create_discount_table(
        discount_schedule={'Sunday': '00:00-06:00',
                           'Monday': '00:00-06:00',
                           'Tuesday': '00:00-06:00',
                           'Wednesday': '00:00-06:00',
                           'Thursday': '00:00-06:00'},
        discount_percentage=20)
    return providers


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    kwh_price = 0.6145
    providers = generate_discount_providers()
    for file in glob('./resources/*.csv'):
        get_best_service(consumption_file_path=file, providers=providers, kwh_price=kwh_price)
        print('-----')
