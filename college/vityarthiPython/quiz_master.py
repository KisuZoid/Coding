import random

questions = [
    {
        "question": "Which Python data structure stores data in key-value pairs?",
        "options": ["List", "Tuple", "Dictionary", "Set"],
        "answer": 3
    },
    {
        "question": "Which keyword is used to make a decision in Python?",
        "options": ["repeat", "if", "define", "input"],
        "answer": 2
    },
    {
        "question": "Which loop is useful when the number of repetitions is known?",
        "options": ["for", "if", "else", "pass"],
        "answer": 1
    },
    {
        "question": "What is the largest value in the list [4, 9, 2, 7]?",
        "options": ["2", "4", "7", "9"],
        "answer": 4
    },
    {
        "question": "Which of the following is a prime number?",
        "options": ["21", "27", "29", "33"],
        "answer": 3
    },
    {
        "question": "What is the GCD of 18 and 24?",
        "options": ["3", "6", "9", "12"],
        "answer": 2
    },
    {
        "question": "Which sequence begins 0, 1, 1, 2, 3, 5?",
        "options": ["Prime sequence", "Fibonacci sequence", "Square sequence", "Even sequence"],
        "answer": 2
    },
    {
        "question": "Which collection does not allow duplicate elements?",
        "options": ["List", "Tuple", "Set", "Dictionary"],
        "answer": 3
    },
    {
        "question": "What is 5 factorial?",
        "options": ["20", "60", "100", "120"],
        "answer": 4
    },
    {
        "question": "Which function can be used to find the largest item in a Python list?",
        "options": ["top()", "max()", "large()", "highest()"],
        "answer": 2
    }
]

score_history = []


def show_title():
    print("=" * 45)
    print("QUIZMASTER".center(45))
    print("QUIZ & SCORE ANALYSIS SYSTEM".center(45))
    print("=" * 45)


def is_prime(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor = divisor + 1
    return True


def prime_factors(number):
    factors = []
    divisor = 2
    while number > 1:
        while number % divisor == 0:
            factors.append(divisor)
            number = number // divisor
        divisor = divisor + 1
    return factors


def gcd(a, b):
    while b != 0:
        old = a % b
        a = b
        b = old
    return a


def fibonacci(n):
    sequence = []
    a = 0
    b = 1
    i = 0
    while i < n:
        sequence.append(a)
        c = a + b
        a = b
        b = c
        i = i + 1
    return sequence


def grade_from_percentage(p):
    if p >= 90:
        return "A+"
    elif p >= 80:
        return "A"
    elif p >= 70:
        return "B"
    elif p >= 60:
        return "C"
    elif p >= 50:
        return "D"
    else:
        return "F"


def performance_message(p):
    if p >= 80:
        return "Very Good"
    elif p >= 60:
        return "Good"
    elif p >= 40:
        return "Needs Improvement"
    else:
        return "Needs More Practice"


def start_quiz():
    print()
    print("=" * 45)
    print("QUIZMASTER".center(45))
    print("QUIZ & SCORE ANALYSIS SYSTEM".center(45))
    print("=" * 45)

    # copy of the list so the original order does not change
    quiz = questions[:]
    random.shuffle(quiz)

    score = 0
    wrong = []
    total = len(quiz)
    print("There are", total, "questions. Choose the correct option.")
    print()

    for i in range(total):
        q = quiz[i]
        print("Question", i + 1, ":", q["question"])
        print("  1.", q["options"][0])
        print("  2.", q["options"][1])
        print("  3.", q["options"][2])
        print("  4.", q["options"][3])

        given = input("Your answer (1-4): ")
        ok = False
        while ok == False:
            try:
                given = int(given)
            except ValueError:
                print("That is not a number. Please type 1, 2, 3 or 4.")
                given = input("Your answer (1-4): ")
            else:
                if given < 1 or given > 4:
                    print("Wrong option number. It must be between 1 and 4.")
                    given = input("Your answer (1-4): ")
                else:
                    ok = True

        if given == q["answer"]:
            print("Correct answer.")
            score = score + 1
        else:
            print("Wrong answer. Correct option was", q["answer"], "-", q["options"][q["answer"] - 1])
            wrong.append(q["question"])
        print()

    score_history.append(score)
    wrong_count = total - score
    percentage = round(score / total * 100, 2)
    grade = grade_from_percentage(percentage)
    message = performance_message(percentage)

    print("=" * 45)
    print("QUIZ RESULT".center(45))
    print("=" * 45)
    print("Correct answers :", score)
    print("Wrong answers   :", wrong_count)
    print("Total questions :", total)
    print("Score           :", str(score) + "/" + str(total))
    print("Percentage      :", str(percentage) + " %")
    print("Grade           :", grade)
    print("Performance     :", message)
    print()
    if wrong_count == 0:
        print("All questions were answered correctly.")
    else:
        print("Questions answered wrongly:")
        for i in range(len(wrong)):
            print("  ", i + 1, ")", wrong[i])
    print("=" * 45)


def score_analysis():
    print()
    print("=" * 45)
    print("SCORE ANALYSIS".center(45))
    print("=" * 45)

    if len(score_history) == 0:
        print("No scores are available yet. Take the quiz first.")
        return

    print("Total quizzes taken :", len(score_history))
    print("All scores          :", score_history)
    print("Highest score       :", max(score_history))
    print("Lowest score        :", min(score_history))
    print("Average score       :", round(sum(score_history) / len(score_history), 2))
    print("Unique scores       :", list(set(score_history)))
    print()
    print("Score frequency:")
    unique = list(set(score_history))
    unique.sort()
    for i in range(len(unique)):
        print("  Score", unique[i], "->", score_history.count(unique[i]), "time(s)")


def number_analysis():
    print()
    print("=" * 45)
    print("NUMBER ANALYSIS".center(45))
    print("=" * 45)

    given = input("Enter a positive integer: ")
    while True:
        try:
            number = int(given)
            if number < 1:
                print("Number should be greater than 0.")
                given = input("Enter a positive integer: ")
            else:
                break
        except ValueError:
            print("That is not a number. Please enter a whole number.")
            given = input("Enter a positive integer: ")

    print()
    print("Number            :", number)
    if is_prime(number):
        print(number, "is a prime number.")
    else:
        print(number, "is not a prime number.")
        print("Prime factors     :", prime_factors(number))

    if len(score_history) > 0:
        last = score_history[len(score_history) - 1]
        print("Latest quiz score :", last)
        print("GCD of", number, "and", last, ":", gcd(number, last))

    print("First 10 Fibonacci numbers:")
    print(fibonacci(10))


def main():
    show_title()
    while True:
        print()
        print("1. Start Quiz")
        print("2. View Score Analysis")
        print("3. Number Analysis")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            start_quiz()
        elif choice == "2":
            score_analysis()
        elif choice == "3":
            number_analysis()
        elif choice == "4":
            print()
            print()
            print("=" * 45)
            print("Quizenjoy".center(45))
            print("Thanks for playing. Bye bye!")
            print("=" * 45)
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
