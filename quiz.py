#!/usr/bin/env python3

import sys
import random
import string

class Answer:
    def __init__(self, answer: str, correct: bool):
        self.answer = answer
        self.correct = correct

    @classmethod
    def from_string(cls, string: str):
        """Parse an answer string."""

        correct = string.startswith('*')
        answer = string[1:] if correct else string
        return cls(answer, correct)

    def __str__(self):
        return ('*' if self.correct else '') + self.answer

class Question:
    def __init__(self, question: str, answers: list):
        self.question = question
        self.answers = answers

    @classmethod
    def from_string(cls, string: str):
        """Parse a question string."""

        lines = string.split('\n')
        question = lines[0]
        answers = list(map(Answer.from_string, lines[1:]))
        return cls(question, answers)

    def __str__(self):
        return '\n'.join([self.question] + list(map(str, self.answers)))

class Quiz:
    def __init__(self, questions: list):
        self.questions = questions

    @classmethod
    def run_from_file(cls, path: str, *args, **kwargs):
        cls.from_file(path).run(*args, **kwargs)

    def run(self, shuffle_questions=True, shuffle_answers=True, feedback=True, requiz=True):
        """Interactively quiz the user via CLI."""

        keys = string.ascii_uppercase
        questions = random.sample(self.questions, len(self.questions)) if shuffle_questions else self.questions
        print(f'Beginning quiz with {len(questions)} questions.')

        def read_answer_indices(num_answers: int) -> list:
            """Prompt user for their answers to the question."""

            answers = list(filter(lambda x: not x.isspace(), input('Enter all of your answers: ').upper()))
            for answer in answers:
                if answer not in list(keys[:num_answers]):
                    print(f'{answer} is not a valid choice. Try again.')
                    return read_answer_indices(num_answers) # tail recurse pls
            return [keys.index(key) for key in answers]

        def ask_question(question: Question) -> bool:
            """Ask a question and return whether the user provided exactly all of the correct answers."""

            print(question.question)
            answers = random.sample(question.answers, len(question.answers)) if shuffle_answers else question.answers
            for key, answer in zip(keys, answers):
                print(f'({key}) {answer.answer}')
            answer_indices = set(read_answer_indices(len(answers)))
            correct_indices = set(filter(lambda i: answers[i].correct, range(len(answers))))
            correct = answer_indices == correct_indices
            if feedback:
                if correct:
                    print("That's right!")
                else:
                    correct_answer_string = ', '. join([keys[i] for i in correct_indices])
                    print(f'Nope. The correct answer was {correct_answer_string}.')
            return correct

        results = list(map(ask_question, questions))
        num_correct = results.count(True)
        num_questions = len(results)
        score = num_correct / num_questions
        print(f'Your score is {num_correct}/{num_questions} ({score * 100:.2f}%)')

        if requiz and num_correct < num_questions:
            print("Now I'll quiz you on the ones you got wrong!")
            Quiz([questions[i] for i in filter(lambda i: not results[i], range(num_questions))]).run(shuffle_questions, shuffle_answers, feedback, requiz)

    @classmethod
    def from_string(cls, string: str):
        """Parse a quiz string."""

        return cls(list(map(Question.from_string, string.split('\n\n'))))

    @classmethod
    def from_file(cls, path: str):
        with open(path) as file_handle:
            return cls.from_string(file_handle.read().strip())

    def __str__(self):
        return '\n\n'.join(list(map(str, self.questions)))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} (quiz_file.txt) [-q]')
        exit(1)
    if len(sys.argv) > 2 and sys.argv[2] == '-q':
        for question in Quiz.from_file(sys.argv[1]).questions:
            print(question.question)
            for answer in question.answers:
                print(answer.answer)
            print()
    else:
        Quiz.run_from_file(sys.argv[1])
