import pandas as pd
from sklearn.preprocessing import LabelEncoder
import requests
from bs4 import BeautifulSoup

def load_and_preprocess_data(raw_df: pd.DataFrame, is_fake: int) -> pd.DataFrame:
    """
    Preprocess the raw fake news dataset.

    Steps:
    - Combine 'title' and 'text' into 'content'
    - Handle missing values
    - Encode 'subject' as a categorical variable
    - Extract year from 'date'
    - Add column with a flag indicating whether the news is fake

    Args:
        raw_df: Raw input DataFrame.
        is_fake: Binary flag indicating whether the data is fake.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """

    # Combine title and text
    raw_df['title'] = raw_df['title'].fillna('')
    raw_df['text'] = raw_df['text'].fillna('')
    raw_df['content'] = raw_df['title'] + ' ' + raw_df['text']

    ## Encode subject
    #raw_df['subject'] = raw_df['subject'].fillna('unknown')
    #subject_encoder = LabelEncoder()
    #raw_df['subject_encoded'] = subject_encoder.fit_transform(raw_df['subject'])

    ## Extract year from date
    #raw_df['year'] = pd.to_datetime(raw_df['date'], errors='coerce').dt.year.fillna(0).astype(int)

    # Add fake news indicator
    if is_fake not in (0, 1):
        raise ValueError(f"is_fake parameter '{is_fake}' needs to be either 0 or 1.")
    raw_df['is_fake'] = is_fake

    return raw_df

def join_fake_and_true_data(fake_df: pd.DataFrame, true_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine two labeled DataFrames (fake and true news) into a single dataset.

    Assumes both DataFrames contain an 'is_fake' boolean column.

    Steps:
    - Ensures both inputs have the 'is_fake' column
    - Concatenates the DataFrames
    - Fills missing values in key text fields (title, text, subject, date)

    Args:
        fake_df (pd.DataFrame): DataFrame containing fake news, with 'is_fake' column equal to 1 for all rows.
        true_df (pd.DataFrame): DataFrame containing true news, with 'is_fake' column equal to 0 for all rows.

    Returns:
        pd.DataFrame: Combined and cleaned DataFrame with integer 'label' column.
    """

    # Validate presence of 'is_fake' column
    if 'is_fake' not in fake_df.columns or 'is_fake' not in true_df.columns:
        raise ValueError("Both DataFrames must contain an 'is_fake' column.")

    # Concatenate
    combined_df = pd.concat([fake_df, true_df], ignore_index=True)

    return combined_df

def onion_renaming(raw_df: pd.DataFrame, mapping_dict: dict) -> pd.DataFrame:
    renamed_df = pd.DataFrame()
    renamed_df['title'] = raw_df[mapping_dict['title']]
    renamed_df['text'] = raw_df[mapping_dict['text']]
    renamed_df['date'] = raw_df[mapping_dict['date']]

    return renamed_df


def fetch_text_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad responses
        soup = BeautifulSoup(response.content, "html.parser")
        body = soup.body
        if body:
            return body.get_text(separator=' ', strip=True)
        else:
            return ''
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ''

def add_text_column(df: pd.DataFrame) -> pd.DataFrame:
    if 'url' not in df.columns:
        raise ValueError("DataFrame must have a 'url' column.")
    df['text'] = df['url'].apply(fetch_text_from_url)
    return df

import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        body = soup.body
        return body.get_text(separator=' ', strip=True) if body else ''
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ''

def add_text_column_fast(df, max_workers=50):
    if 'url' not in df.columns:
        raise ValueError("DataFrame must have a 'url' column.")

    texts = [''] * len(df)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {executor.submit(fetch_text, url): idx for idx, url in enumerate(df['url'])}
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                texts[idx] = future.result()
            except Exception as e:
                print(f"Error fetching index {idx}: {e}")

    df['text'] = texts
    return df
