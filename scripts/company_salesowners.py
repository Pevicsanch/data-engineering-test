import re
import os
import pandas as pd
import logging
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import pdist, squareform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

def normalize_company_name(name):
    """
    Normalize company names by converting to lowercase, removing unwanted suffixes,
    punctuation, and applying lemmatization.
    """
    try:
        if pd.isna(name):
            return ""
        
        name = name.lower()
        name = re.sub(r'\b(co|inc|ltd|gmbh|c\.o|limited|corporation|s\.a\.r\.l)\b', '', name)
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        words = sorted(name.split())
        lemmatized_words = [lemmatizer.lemmatize(word, pos='n') for word in words]
        normalized_name = ' '.join(lemmatized_words)
        
        return normalized_name
    except Exception as e:
        logging.error(f"Error normalizing company name '{name}': {e}")
        return ""

def load_orders_data(filepath):
    """
    Load orders data from CSV file.
    """
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        return None
    try:
        df = pd.read_csv(filepath, delimiter=';')
        logging.info("Data loaded successfully.")
        return df
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return None

def assign_similarity_groups(df, threshold=0.7):
    """
    Assign similarity groups based on Jaccard similarity.
    """
    count_vectorizer = CountVectorizer(analyzer='word', binary=True)
    count_matrix = count_vectorizer.fit_transform(df['normalized_company_name'])
    jaccard_distances = pdist(count_matrix.toarray(), metric='jaccard')
    jaccard_sim_matrix = 1 - squareform(jaccard_distances)

    group_counter = 0
    df['similarity_group'] = None
    for i in range(len(jaccard_sim_matrix)):
        if df.loc[i, 'similarity_group'] is None:
            group_counter += 1
            df.loc[i, 'similarity_group'] = group_counter
        for j in range(i + 1, len(jaccard_sim_matrix)):
            if jaccard_sim_matrix[i, j] >= threshold:
                df.loc[j, 'similarity_group'] = df.loc[i, 'similarity_group']
    logging.info("Similarity groups assigned.")
    return df

def consolidate_salesowners(df):
    """
    Consolidate salesowners into unique, sorted lists by similarity group.
    """
    try:
        df_3 = df.groupby('similarity_group').agg({
            'company_id': 'first',
            'normalized_company_name': 'first',
            'salesowners': lambda x: ', '.join(sorted(set(', '.join(x).split(', '))))
        }).reset_index(drop=True)
        
        df_3.rename(columns={'normalized_company_name': 'company_name', 'salesowners': 'list_salesowners'}, inplace=True)
        logging.info("Salesowners consolidated successfully.")
        return df_3
    except Exception as e:
        logging.error(f"Error consolidating salesowners: {e}")
        return None

def save_to_csv(df, output_path):
    """
    Save the final DataFrame to a CSV file.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info(f"Data saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")

def main():
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, '..', 'data', 'orders.csv')
    output_path = os.path.join(script_dir, '..', 'output', 'final_company_salesowners.csv')

    # Log paths
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Input path: {input_path}")
    logging.info(f"Output path: {output_path}")

    # Load data
    orders_df = load_orders_data(input_path)
    if orders_df is None:
        logging.error("Failed to load orders data. Exiting.")
        return

    # Normalize company names
    orders_df['normalized_company_name'] = orders_df['company_name'].apply(normalize_company_name)
    
    # Assign similarity groups
    orders_df = assign_similarity_groups(orders_df)

    # Consolidate salesowners
    final_df = consolidate_salesowners(orders_df)
    if final_df is None:
        logging.error("Failed to consolidate salesowners. Exiting.")
        return

    # Save to CSV
    save_to_csv(final_df, output_path)

if __name__ == "__main__":
    main()