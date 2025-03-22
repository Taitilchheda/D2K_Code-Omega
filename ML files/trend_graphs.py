import pandas as pd
from datetime import datetime
import random
import matplotlib.pyplot as plt
import seaborn as sns

def generate_event_data(num_events=50):
    """Generates a sample event data CSV for Mumbai, India.

    Args:
        num_events (int): The number of sample events to generate.

    Returns:
        pandas.DataFrame: A DataFrame containing the sample event data.
    """

    event_names = [
        "Mumbai Music Fest", "Bollywood Dance Workshop", "Street Food Festival",
        "Yoga & Meditation Retreat", "Cricket Match - Local League", "Art Exhibition",
        "Cooking Class - Indian Cuisine", "Stand-up Comedy Night", "Marathi Natak Festival",
        "Kids' Carnival", "Tech Workshop", "Book Launch Event", "Fitness Bootcamp",
        "Fashion Show", "Photography Exhibition", "Craft Fair", "Wine Tasting",
        "Live Music Night", "Sports Coaching Camp", "Cultural Performance",
        "Diwali Dhamaka", "Christmas Carol Concert", "New Year's Eve Party",
        "Monsoon Film Festival", "Summer Pool Party", "Heritage Walk",
        "Marathi Film Screening", "Street Art Workshop", "Marathon Training Session",
        "Food Truck Festival", "Bollywood Movie Night", "Pottery Workshop",
        "Salsa Dance Class", "Weekend Trek", "Kids' Playdate", "Business Seminar",
        "Travel Expo", "Pet Adoption Drive", "Music Workshop for Beginners",
        "Art Therapy Session", "Comedy Open Mic", "Yoga in the Park",
        "Cycling Tour", "Cooking Competition", "Dance Performance",
        "Science Exhibition", "Book Reading Session", "Gourmet Food Tasting"
    ]

    event_types = [
        "Music Concert", "Workshop", "Food & Drink", "Workshop", "Sports Event",
        "Workshop", "Workshop", "Music Concert", "Festival", "Festival",
        "Workshop", "Workshop", "Workshop", "Festival", "Workshop",
        "Festival", "Food & Drink", "Music Concert", "Sports Event", "Festival",
        "Festival", "Music Concert", "Music Concert", "Festival", "Party",
        "Workshop", "Workshop", "Workshop", "Sports Event", "Food & Drink",
        "Workshop", "Workshop", "Workshop", "Sports Event", "Festival",
        "Workshop", "Workshop", "Festival", "Workshop", "Music Concert",
        "Workshop", "Sports Event", "Workshop", "Food & Drink", "Workshop",
        "Music Concert", "Workshop", "Food & Drink"
    ]

    locations = [
        "Bandra", "Andheri", "Bandra", "Lonavala", "Churchgate", "Colaba",
        "Matunga", "Lower Parel", "Prabhadevi", "Juhu", "BKC", "Fort",
        "Powai", "Worli", "Bandra", "Borivali", "Bandra", "Khar",
        "Bandra", "Ghatkopar", "Various", "Colaba", "Various",
        "Juhu", "Various", "Fort", "Dadar", "Bandra", "Marine Drive",
        "Various", "Andheri", "Vile Parle", "Vasai", "Various",
        "BKC", "Various", "Various", "Bandra", "Andheri", "Lower Parel",
        "Marine Drive", "Bandra", "Matunga", "Borivali", "Bandra", "Churchgate",
        "Bandra", "Worli"
    ]

    seasons = {
        "Summer": [3, 4, 5],  # March, April, May
        "Monsoon": [6, 7, 8, 9],  # June, July, August, September
        "Autumn/Festival": [10, 11],  # October, November
        "Winter": [12, 1, 2]  # December, January, February
    }

    data = []
    start_date = datetime(2024, 3, 1)  # Start generating from March 2024

    for i in range(num_events):
        event_name = random.choice(event_names) + f" - {random.choice(['Edition', 'Special'])}" if random.random() < 0.3 else random.choice(event_names)
        event_type = random.choice(event_types)
        location = random.choice(locations)
        engagement_score = random.randint(60, 95)

        # Randomly select a month and day within a reasonable range
        year = random.randint(2024, 2025)
        month = random.randint(1, 12)
        if month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        elif month == 2:
            day = random.randint(1, 28) if year % 4 != 0 else random.randint(1, 29)
        else:
            day = random.randint(1, 31)

        event_date = datetime(year, month, day).strftime('%Y-%m-%d')
        dt_object = datetime.strptime(event_date, '%Y-%m-%d')
        day_name = dt_object.strftime('%A')
        month_num = dt_object.month

        season = ""
        for s, months in seasons.items():
            if month_num in months:
                season = s
                break

        data.append([
            event_name, event_type, event_date, day_name, month_num, season, location, engagement_score
        ])

    df = pd.DataFrame(data, columns=[
        "Event Name", "Event Type", "Event Date", "Day", "Month", "Season", "Location", "Engagement Score"
    ])
    return df

def display_analysis_menu(df):
    """Displays the analysis menu and performs selected visualizations."""
    while True:
        print("\n--- Event Data Analysis ---")
        print("Choose an analysis option:")
        print("1. Event Count by Season (Bar Chart)")
        print("2. Event Count by Event Type (Bar Chart)")
        print("3. Frequency of Event Types in a Specific Month (Bar Chart)")
        print("4. Exit")

        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            plt.figure(figsize=(8, 6))
            sns.countplot(x='Season', data=df, order=['Summer', 'Monsoon', 'Autumn/Festival', 'Winter'])
            plt.title('Event Count by Season')
            plt.xlabel('Season')
            plt.ylabel('Number of Events')
            plt.grid(axis='y')
            plt.tight_layout()
            plt.show()
        elif choice == '2':
            plt.figure(figsize=(10, 6))
            sns.countplot(y='Event Type', data=df, order=df['Event Type'].value_counts().index)
            plt.title('Event Count by Event Type')
            plt.xlabel('Number of Events')
            plt.ylabel('Event Type')
            plt.tight_layout()
            plt.show()
        elif choice == '3':
            try:
                month_num_str = input("Enter the month number (1-12): ")
                month_num = int(month_num_str)
                if 1 <= month_num <= 12:
                    month_name = datetime(2024, month_num, 1).strftime('%B')
                    month_df = df[df['Month'] == month_num].copy()  # Create a copy to avoid SettingWithCopyWarning
                    if not month_df.empty:
                        plt.figure(figsize=(10, 6))
                        sns.countplot(y='Event Type', data=month_df, order=month_df['Event Type'].value_counts().index)
                        plt.title(f'Frequency of Event Types in {month_name}')
                        plt.xlabel('Number of Events')
                        plt.ylabel('Event Type')
                        plt.tight_layout()
                        plt.show()
                    else:
                        print(f"No events found for the month of {month_name}.")
                else:
                    print("Invalid month number. Please enter a number between 1 and 12.")
            except ValueError:
                print("Invalid input. Please enter a valid month number.")
        elif choice == '4':
            print("Exiting the analysis.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    num_events_to_generate = 60
    sample_df = generate_event_data(num_events=num_events_to_generate)
    sample_df.to_csv("event_data.csv", index=False)
    print(f"Generated {num_events_to_generate} sample events and saved them to 'event_data.csv'")
    print("\nFirst few rows of the generated data:")
    print(sample_df.head())

    # Perform analysis after generating the data
    display_analysis_menu(sample_df)

# ... (rest of the code) ...

if __name__ == "__main__":
    num_events_to_generate = 60
    sample_df = generate_event_data(num_events=num_events_to_generate)
    sample_df.to_csv("event_data.csv", index=False)
    print(f"Generated {num_events_to_generate} sample events and saved them to 'event_data.csv'")
    print("\nFirst few rows of the generated data:")
    print(sample_df.head())

    # Simple test plot
    plt.figure(figsize=(4, 3))
    plt.plot([1, 2, 3], [4, 5, 6])
    plt.title("Test Plot")
    plt.show()

    # Perform analysis after generating the data
    display_analysis_menu(sample_df)    