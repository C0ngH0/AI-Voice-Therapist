def decode(message_file):
    with open(message_file, 'r') as file:
        lines = file.readlines()
    
    # Dictionary to hold number-word pairs
    num_word_dict = {}
    for line in lines:
        num, word = line.split()
        num_word_dict[int(num)] = word
    
    # Determine the length of the pyramid's base
    base_length = 1
    while base_length * (base_length + 1) / 2 <= len(num_word_dict):
        base_length += 1
    base_length -= 1
    
    # Extract words at the end of each pyramid line
    decoded_words = []
    end_numbers = [int(i * (i + 1) / 2) for i in range(1, base_length + 1)]
    for num in end_numbers:
        decoded_words.append(num_word_dict[num])
    
    # Return the decoded message
    return ' '.join(decoded_words)
def main():
    message_file = 'text.txt'  # Replace this with the actual file path
    decoded_message = decode(message_file)
    print(decoded_message)

if __name__ == "__main__":
    main()
