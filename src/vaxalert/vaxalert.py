# %%
import requests
import pandas as pd
from io import StringIO
import json
from typing import Union
import os
from schedule import every, repeat, run_pending
import time
import datetime


# %%

def get_vaccine_availability_data_by_pincode_date(
    pincode: str,
    date: datetime.date = datetime.date.today()
) -> dict:

    api = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin'
    params = {'pincode': pincode, 'date': date.strftime("%d-%m-%Y")}
    api_response = requests.get(api, params=params)

    assert api_response.status_code == 200, 'COWIN API call did not return with success code 200'

    return api_response.json()


# %%
def flatten_response_data(
    response_json: dict,
    cast_to_pandas_df: bool = True
) -> Union[list, pd.DataFrame]:
    flattened = []
    center_data = response_json['centers']

    common_keys = [
        'center_id',
        'name',
        'state_name',
        'district_name',
        'block_name',
        'pincode',
        'fee_type'
    ]

    session_keys = [
        'session_id',
        'date',
        'available_capacity',
        'min_age_limit',
        'vaccine',
    ]

    for sessions_data in center_data:
        sessions = sessions_data['sessions']
        # is_paid = True if sessions_data['fee_type'] else False
        for s in sessions:
            slots = s['slots']
            vaccine = s['vaccine']
            for slot in slots:
                add = dict((k,sessions_data.get(k, '')) for k in common_keys)
                for k in session_keys:
                    add[k] = s[k]
                add['slot'] = slot
                flattened.append(add)

    if(cast_to_pandas_df):
        return pd.read_json(json.dumps(flattened))

    return flattened



# %%
def filter_slots_with_availability(
    availability_data: pd.DataFrame,
    min_age_limit_filter: list = [18, 45]
) -> pd.DataFrame:

    return availability_data.loc[
        (availability_data['available_capacity'] > 0) \
        & (availability_data.min_age_limit.isin(min_age_limit_filter))]

# %%

def post_message_to_telegram(
    message: str
):
    token = os.environ.get('TELERGAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_BOT_CHAT_ID')
    
    send_url = 'https://api.telegram.org/bot' + token + '/sendMessage'
    params = {'chat_id': chat_id, 'parse_mode': 'Markdown', 'text': message}
    response = requests.get(send_url, params=params)

    return response

# %%
def generate_available_appointments_message(
    pincode: str,
    num_days_to_lookup: int,
    min_age_limit_filter: list = [18,45]
) -> str:

    today = datetime.date.today()
    dates_array = pd.date_range(today, periods=num_days_to_lookup).to_pydatetime().tolist()
    dates_array = list(map(lambda x: x.date(), dates_array))

    appointments_data_array = []

    for date in dates_array:
        response = get_vaccine_availability_data_by_pincode_date(pincode, date)
        df = flatten_response_data(response)
        appointments_data_array.append(df)

    appointments_data = pd.concat(appointments_data_array)
    appointments_data.drop_duplicates(inplace=True)
    availability_data = filter_slots_with_availability(appointments_data, min_age_limit_filter=min_age_limit_filter)

    if(len(availability_data) == 0):
        return f'[{str(datetime.datetime.now())}]No available slots found'

    '''
    project_cols = [
        'name',
        'date',
        'vaccine',
        'min_age_limit',
        'available_capacity'
    ]
    
    availability_data = availability_data[project_cols]
    message = ''
    '''
    available_at = list(availability_data.name.unique())
    return f"[{str(datetime.datetime.now())}] Appointments available at {','.join(available_at)}\nHURRY!!!"


# %%
@repeat(every(5).minutes)
def run_vaccine_slot_alert():
    print(f"Running alert at {datetime.datetime.now()}\n\n")
    post_message_to_telegram(
        generate_available_appointments_message(
            '560066',
            5,
            [18,45]
        )
    )

# %%
if __name__ == "__main__":
    while True:
        run_pending()
        time.sleep(10)