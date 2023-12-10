def main():
    n = int(input("Enter the number: "))
    print(fibonacci(n))
    print(fibonacci_reverse(n))

def fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        next_number = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_number)
    return fib_sequence[:n]

def fibonacci_reverse(n):
    fib_rev_sequence = [0, 1]
    while len(fib_rev_sequence) < n:
        next_number = fib_rev_sequence[-1] + fib_rev_sequence[-2]
        fib_rev_sequence.append(next_number)
    return fib_rev_sequence[::-1]

main()


"""
    Define a function named 'fibonacci' that takes an argument 'n'.
    Initialize a list 'fib_sequence' with the first two Fibinacci numbers.
    use a 'while' loop to generate Fibonacci numbers until the desired length is reached.
    caluclate the next Fibonacci number by adding the last two numbers in the sequence
    Append the newly calculated fibonacci number to the sequence
    Return the first 'n' Fibonacci numbers.
    [-1] indicates the 1st numbr from last i.e in [0,1,2,3] -> [-1] means '3', [-2] means '2'
    [::-1] means reverse the list i.e. in [0,1,2,3] -> [::-1] means [3,2,1,0]
    [start_index:end_index] i.e. in [1,3,5,8,2] -> print [:3] means print value from index 0 to 3 ([1,3,5,8]), and print [2:] means print from index 2 to last ([5,8,2]). 
"""