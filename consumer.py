# import psycopg2
# from confluent_kafka import Consumer, KafkaError
# import json

# # Kafka Consumer configuration
# conf = {
#     'bootstrap.servers': 'localhost:9092',
#     'group.id': 'my-group',
#     'auto.offset.reset': 'earliest'
# }
# consumer = Consumer(**conf)
# consumer.subscribe(['alpha_vantage_data'])

# # PostgreSQL connection setup
# conn = psycopg2.connect(
#     host= 'postgres',
#     database= 'stock_bd',
#     user= 'ilyas',
#     password= 'sh_bd_24'
# )

# cursor = conn.cursor()

# # SQL query to insert or update data
# insert_query = """
#     INSERT INTO stock_data (symbol, timestamp, open, high, low, close, volume, sentiment_score, sentiment_score_nlp)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#     ON CONFLICT (symbol, timestamp) DO UPDATE
#     SET open = EXCLUDED.open,
#         high = EXCLUDED.high,
#         low = EXCLUDED.low,
#         close = EXCLUDED.close,
#         volume = EXCLUDED.volume,
#         sentiment_score = EXCLUDED.sentiment_score,
#         sentiment_score_nlp = EXCLUDED.sentiment_score_nlp;
# """

# def consume_data():
#     while True:
#         msg = consumer.poll(1.0)
#         if msg is None:
#             continue
#         if msg.error():
#             if msg.error().code() == KafkaError._PARTITION_EOF:
#                 continue
#             else:
#                 print(msg.error())
#                 break

#         data = json.loads(msg.value().decode('utf-8'))

#         # Insert data into PostgreSQL
#         cursor.execute(insert_query, (
#             data['symbol'],
#             data['timestamp'],
#             data['open'],
#             data['high'],
#             data['low'],
#             data['close'],
#             data['volume'],
#             data['sentiment_score'],
#             data['sentiment_score_nlp']
#         ))
#         conn.commit()  # Commit the transaction

# if __name__ == '__main__':
#     try:
#         consume_data()
#     except KeyboardInterrupt:
#         print("Consumer shutting down.")
#     finally:
#         consumer.close()
#         cursor.close()
#         conn.close()





from confluent_kafka import Consumer, KafkaError
import pandas as pd
import json
import os

# Kafka Consumer configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(**conf)
consumer.subscribe(['alpha_vantage_data'])

# CSV file path
csv_file_path = 'C:/Users/hp/Desktop/project/data/stock_data_with_sentiment.csv'

# Create a CSV file with headers if it doesn't exist
if not os.path.isfile(csv_file_path):
    with open(csv_file_path, 'w') as f:
        f.write('symbol,timestamp,open,high,low,close,volume,sentiment_score,sentiment_score_nlp\n')  # Write CSV header

def consume_data():
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        data = json.loads(msg.value().decode('utf-8'))
        # Write data to CSV file
        with open(csv_file_path, 'a') as f:  # Open file in append mode
            f.write(f"{data['symbol']},{data['timestamp']},{data['open']},{data['high']},{data['low']},{data['close']},{data['volume']},{data['sentiment_score']},{data['sentiment_score_nlp']}\n")

if __name__ == '__main__':
    try:
        consume_data()
    except KeyboardInterrupt:
        print("Consumer shutting down.")
    finally:
        consumer.close()





# # from confluent_kafka import Consumer, KafkaError
# # import json
# # import os
# # import time

# # # Kafka Consumer configuration
# # conf = {
# #     'bootstrap.servers': 'localhost:9092',
# #     'group.id': 'my-group',
# #     'auto.offset.reset': 'earliest'
# # }
# # consumer = Consumer(**conf)
# # consumer.subscribe(['alpha_vantage_data'])

# # # CSV file path
# # csv_file_path = 'stock_data.csv'

# # # Create a CSV file with headers if it doesn't exist
# # if not os.path.isfile(csv_file_path):
# #     with open(csv_file_path, 'w') as f:
# #         f.write('symbol,timestamp,open,high,low,close,volume\n')  # Write CSV header

# # def consume_data():
# #     start_time = time.time()  # Record the start time
# #     while True:
# #         msg = consumer.poll(1.0)
# #         if msg is None:
# #             continue
# #         if msg.error():
# #             if msg.error().code() == KafkaError._PARTITION_EOF:
# #                 continue
# #             else:
# #                 print(msg.error())
# #                 break

# #         data = json.loads(msg.value().decode('utf-8'))
# #         # Write data to CSV file, now including the stock symbol
# #         with open(csv_file_path, 'a') as f:  # Open file in append mode
# #             f.write(f"{data['symbol']},{data['timestamp']},{data['1. open']},{data['2. high']},{data['3. low']},{data['4. close']},{data['5. volume']}\n")

# #         # Check if 60 seconds have passed
# #         if time.time() - start_time >= 20:
# #             print("20 seconds passed, shutting down...")
# #             break

# # if __name__ == '__main__':
# #     try:
# #         consume_data()
# #     except KeyboardInterrupt:
# #         pass
# #     finally:
# #         consumer.close()
