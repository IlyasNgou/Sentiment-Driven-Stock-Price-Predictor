import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df=pd.read_csv('C:/Users/hp/Desktop/project/data/stock_data_with_sentiment.csv')

# Ensure 'timestamp' is treated as a datetime object
df['timestamp'] = pd.to_datetime(df['timestamp'])

sns.set(style='whitegrid')

symbols = df['symbol'].unique()
features = ['open', 'high', 'low', 'close', 'volume', 'sentiment_score', 'sentiment_score_nlp']

for symbol in symbols:
    symbol_data = df[df['symbol'] == symbol]
    
    # Loop through features and create separate plots
    for feature in features:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))  # Create side-by-side plots
        
        if feature in ['open', 'high', 'low', 'close']:
            # Plot line plot on the left for features like 'open', 'high', 'low', 'close'
            ax1.plot(symbol_data['timestamp'], symbol_data[feature], color='blue', lw=2)
            ax1.set_xlabel('Timestamp')
            ax1.set_ylabel(feature)
            ax1.set_title(f'{symbol} - {feature} Line Plot')
        else:
            # Plot histogram for 'sentiment_score' and 'sentiment_score_nlp'
            ax1.hist(symbol_data[feature], bins=15, alpha=0.7, color='blue', edgecolor='black')
            ax1.set_xlabel(feature)
            ax1.set_ylabel('Frequency')
            ax1.set_title(f'{symbol} - {feature} Histogram')
        
        # Plot boxplot on the right for all features
        sns.boxplot(data=symbol_data[feature], ax=ax2, color='orange', width=0.1)
        ax2.set_title(f'{symbol} - {feature} Boxplot')

        # Adjust layout and display the plot
        plt.tight_layout()
        plt.show()
