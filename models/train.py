import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout, LSTM
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Load the data
df = pd.read_csv('C:/Users/hp/Desktop/project/data/stock_data_with_sentiment.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['volume'] = np.log(df['volume'] + 1)
df['rolling_close'] = df['close'].rolling(window=5).mean()
df['rolling_open'] = df['open'].rolling(window=5).mean()
df['rolling_volume'] = df['volume'].rolling(window=5).mean()

# Lag Features
df['sentiment_lag1'] = df['sentiment_score'].shift(1)
df['close_lag1'] = df['close'].shift(1)

# Volatility Measures
df['daily_return'] = df['close'].pct_change()
df['volatility'] = df['daily_return'].rolling(window=5).std()

df['mid_range'] = (df['high'] - df['low']) / 2 + df['low']

# Drop the 'high' and 'low' columns
df = df.drop(columns=['high', 'low'])

average_volume = df['volume'].mean()

# Create the volume-weighted mid-range feature
df['volume_weighted_mid_range'] = (df['mid_range'] * df['volume']) / average_volume

# Optionally, create other features as needed
# Example: Mid Range Change Ratio
df['previous_mid_range'] = df['mid_range'].shift(1)  # Shift to get the previous day's mid_range
df['mid_range_change_ratio'] = (df['mid_range'] - df['previous_mid_range']) / df['previous_mid_range'] * df['volume']

# Function to create datasets
def create_dataset(data, time_step=1):
    X, y = [], []
    for i in range(len(data) - time_step - 1):
        a = data[i:(i + time_step), 0]  # features
        X.append(a)
        y.append(data[i + time_step, 0])  # target
    return np.array(X), np.array(y)

# Initialize results
results = {}

# Loop through each symbol
for symbol in df['symbol'].unique():
    # Filter data for the current symbol and sort by date to ensure chronological order
    symbol_data = df[df['symbol'] == symbol].sort_values(by='timestamp')
    # Use 'close' prices for prediction
    dataset = symbol_data['close'].values.reshape(-1, 1)

    # Scale the data (normalization)
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    print(dataset)
    
    # Split data into training and testing sets by date (80% training)
    train_size = int(len(dataset) * 0.7)
    train, test = dataset[0:train_size], dataset[train_size:len(dataset)]

    # Create the dataset for RNN
    time_step = 8  
    X_train, y_train = create_dataset(train, time_step)
    X_test, y_test = create_dataset(test, time_step)

    # Check if there's enough data to reshape
    if len(X_train) == 0 or len(X_test) == 0:
        print(f"Not enough data for symbol: {symbol}")
        continue

    # Reshape input to be [samples, time steps, features]
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(40, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(30))
    model.add(Dense(1))

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, epochs=30, batch_size=32, verbose=1)

    # Predict using the model
    test_predict = model.predict(X_test)

    # Inverse transform predictions and actual values
    test_predict = scaler.inverse_transform(test_predict)
    y_train_inverse = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_inverse = scaler.inverse_transform(y_test.reshape(-1, 1))

    # # Plotting the results
    # plt.figure(figsize=(14, 5))
    # plt.plot(symbol_data['timestamp'], symbol_data['close'], label='Actual Prices')
    
    # # Plot actual test prices
    # plt.plot(symbol_data['timestamp'][len(symbol_data['timestamp']) - len(test_predict):], y_test_inverse, color='blue', label='Actual Test Prices')
    
    # # Plot predicted test prices
    # plt.plot(symbol_data['timestamp'][len(symbol_data['timestamp']) - len(test_predict):], test_predict, color='red', label='Predicted Prices')

    # plt.title(f'{symbol} Stock Price Prediction')
    # plt.xlabel('Time')
    # plt.ylabel('Price')
    # plt.legend()
    # plt.show()
    
    # Optionally, you can calculate evaluation metrics like MAE and RMSE
    rmse = np.sqrt(mean_squared_error(y_test_inverse, test_predict))
    mae = mean_absolute_error(y_test_inverse, test_predict)
    print(f'RMSE for {symbol}: {rmse}')
    print(f'MAE for {symbol}: {mae}')
