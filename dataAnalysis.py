import json
import arrow
import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt

df = pd.read_json("data.json")

# explode cmp_name into its components and get a separate DataFrame
def unpack_campaign_name(cmp_name):
    # assumes data in campaign name
    # is in good state
    type_, start, end, age, gender, currency = cmp_name.split('_')
    start = arrow.get(start, 'YYYYMMDD').date()
    end = arrow.get(end, 'YYYYMMDD').date()

    # return the new object based on how they were split above
    return type_, start, end, age, gender, currency


campaign_data = df['cmp_name'].apply(unpack_campaign_name)

campaign_cols = ['Type', 'Start', 'End', 'Target Age', 'Target Gender', 'Currency']

campaign_df = DataFrame(campaign_data.tolist(), columns=campaign_cols, index=df.index)

# join the df dataframe to the campaign_df as cdf
cdf = df.join(campaign_df)

# explode json object into it components and get a separate DataFrame for those
def unpack_user_json(user):
    # very optimistic as well, expects user objects
    # to have all attributes
    user = json.loads(user.strip())
    return [
        user['username'],
        user['email'],
        user['name'],
        user['gender'],
        user['age'],
        user['address'],
    ]

user_data = cdf['user'].apply(unpack_user_json)

user_cols = ['Username', 'Email', 'Name', 'Gender', 'Age', 'Address']

user_cdf = DataFrame(user_data.tolist(), columns=user_cols, index=cdf.index)

# join the two dataframes cdf and user_cdf
ucdf = cdf.join(user_cdf)

# rename and add 3 columns per ipyb
new_column_names = {
    'cmp_age': 'Age',
    'cmp_spent': 'Spent',
    'cmp_clicks': 'Clicks',
    'cmp_impr': 'Impressions',
}

ucdf.rename(columns=new_column_names, inplace=True)

# calculates and creates columns for this data
def calculate_extra_columns(df):
    # Click Through Rate
    df['CTR'] = df['Clicks'] / df['Impressions']
    # Cost Per Click
    df['CPC'] = df['Spent'] / df['Clicks']
    # Cost Per Impression
    df['CPI'] = df['Spent'] / df['Impressions']

# pass in the entire data frame
# apply calculate_extra_columns function
calculate_extra_columns(ucdf)


# add the name of the Day when campaign starts
def get_day_of_the_week(day):
    return day.strftime("%A")

def get_duration(row):
    return (row['End'] - row['Start']).days


ucdf['Day of Week'] = ucdf['Start'].apply(get_day_of_the_week)
ucdf['Duration'] = ucdf.apply(get_duration, axis=1)

# apply final_columns per ipyb to ucdf
final_columns = [
    'Type', 'Start', 'End', 'Duration', 'Day of Week',
    'Currency', 'Clicks', 'Impressions', 'Spent', 'CTR', 'CPC',
    'CPI', 'Target Age', 'Target Gender', 'Username', 'Email',
    'Name', 'Gender', 'Age'
]

ucdf = ucdf[final_columns]

# save ucdf dataframe to df.xlsx excel file
ucdf.to_excel('df.xlsx')

# plot a histogram from ucdf that consist of 'Age' 'Spent' 'Clicks' 'Impressions
# save to result.png
plt.style.use(['classic', 'ggplot'])
plt.rc('font', family='serif')

ucdf[['Age', 'Spent', 'Clicks', 'Impressions']].hist(bins=16, figsize=(16, 6))

plt.savefig("result.png")

# create a pivot table and save plot ot pivot_data.png

pivot = ucdf.pivot_table(values = ['Impressions', 'Clicks'],
                         index = ['Age'],
                         columns = ['Target Gender'],
                         aggfunc = np.sum
)

plt.savefig("pivot_table.png")
print(pivot)

pivot.plot(kind='bar', stacked=True)
plt.title('Pivot Table Example')
plt.xlabel('Age')
plt.ylabel('Count')
plt.legend(title='Gender')
plt.show()






