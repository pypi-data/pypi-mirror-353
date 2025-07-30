import argparse
import logging
import time
import os
import re
from collections import Counter

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='tool.log',
    filemode='a'
)

# Decorator for logging execution time
def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Execution time: {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Function to count words
def process_content(content):
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = Counter(words)
        return '\n'.join([f"{word}: {count}" for word, count in word_count.items()])

# Function to handle file I/O (includes ERROR level logging)
@log_execution_time
def process_files(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            logging.info(f"Reading input file: {input_file}")
            content = infile.read()

        processed_content = process_content(content)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            logging.info(f"Writing output file: {output_file}")
            outfile.write(processed_content)

        logging.info("File processing completed successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {input_file}")
        print(f"Error: File not found - {input_file}")
    except PermissionError:
        logging.error(f"Permission denied for file: {input_file} or {output_file}")
        print(f"Error: Permission denied - {input_file} or {output_file}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description='Process a text file and output word frequencies in it.')
    parser.add_argument('input', help='Path to the input text file')
    parser.add_argument('output', help='Path to the output text file')
    args = parser.parse_args()


    process_files(args.input, args.output)

if __name__ == '__main__':
    main()