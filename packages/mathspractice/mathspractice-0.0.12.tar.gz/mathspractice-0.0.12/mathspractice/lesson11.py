import math
import random
import time
from decimal import Decimal, ROUND_FLOOR
from typing import Tuple

from flask import Blueprint, render_template, request, flash

from .stats import Statistics

bp = Blueprint('lesson11', __name__)

@bp.route('/')
def index():
    statistics = Statistics()
    return render_template(
        'lesson11/index.html',
        statistics=statistics,
    )


@bp.route('/percent/problems', methods=['GET', 'POST'])
def percent_problems():
    when = time.time()
    statistics = Statistics()
    stats = statistics.get_stats('lesson11', 'percent_problems')
    if request.method == 'POST':
        try:
            if not request.form.get('answer'):
                raise ValueError('Sorry. You needed to provide an answer. Please try again.')
            first = Decimal(request.form.get('first'))
            second = Decimal(request.form.get('second'))
            problem = request.form.get('problem')
            answer = Decimal(request.form.get('answer'))
            now = float(request.form.get('now'))
            elapsed = when - now
            real_answer = calculate_answer(problem, first, second)
            stats['seconds'] += elapsed
            if answer == real_answer:
                flash(f"Correct. Well done! {real_answer} is correct.", category='correct')
                stats['correct'] += 1
            else:
                flash(f"Incorrect. I'm sorry but {answer} is not correct. It is {real_answer}", category='incorrect')
                stats['incorrect'] += 1
            statistics.save()
        except Exception as e:
            flash(str(e), category='error')
    max_value = int(math.pow(10, 4 + stats['correct'] // 20))
    problem, first, second = determine_problem(max_value)
    now = int(time.time())
    return render_template(
        'lesson11/percent_problems.html',
        first=first, second=second, problem=problem, now=now, statistics=statistics
    )

def determine_problem(max_value: int) -> Tuple[str, Decimal, Decimal]:
    which = random.randint(1, 5)
    if which == 1:
        first = Decimal(random.randint(10, 50))
        second = Decimal(random.randint(1, max_value)) / Decimal(100)
        problem = f'What is an {first}% tip on a ${second} restaurant bill?'
        return problem, first, second
    if which == 2:
        what = random.choice([('dealer', 'car'), ('agent', 'house')])
        first = Decimal(random.randint(1, max_value))
        second = Decimal(random.randint(10, 50))
        problem = (f'The original price of a {what[1]} was ${first}. '
                   f'Then, the {what[0]} decided to give a {second}% discount off the price of the {what[1]}. '
                   f'What is the price of the {what[1]} now?')
        return problem, first, second
    if which == 3:
        what = random.choice(['electric', 'gas', 'phone', 'water'])
        first = Decimal(random.randint(1, max_value)) / Decimal(100)
        second = Decimal(random.randint(5, 50))
        problem = (f"Last month’s {what} bill was ${first}. "
                   f"Then, the company decided to give a {second}% discount to its customers. "
                   f"How much is the bill now?")
        return problem, first, second
    if which == 4:
        what = random.choice([
            ('restaurant', 'students', 'lunch'),
            ('dry cleaners', 'office workers', 'laundry'),
            ('golf club', 'players', 'golfing')
        ])
        first = Decimal(random.randint(1, max_value)) / Decimal(100)
        second = Decimal(random.randint(5, 20))
        problem = (f"A {what[0]} offers a {second}% discount to all {what[1]}, "
                   f"including your friend. Their recent {what[2]} bill "
                   f"should have cost ${first}. "
                   f"What was the actual cost once the {second}% discount was taken?")
        return problem, first, second
    if which == 5:
        first = Decimal(random.randint(40, 180)) / Decimal(4)
        second = Decimal(random.randint(1, max_value)) * Decimal(10)
        problem = (f"The federal income tax is {first}%. "
                   f"You earned ${second:,} last year. "
                   f"How much tax will you have to pay?")
        return problem, first, second
    return '', Decimal(0), Decimal(0)


def calculate_answer(problem: str, first: Decimal, second: Decimal) -> Decimal:
    answer = Decimal(0)
    if problem.startswith('What is an'):
        answer = first * second / Decimal(100)
    if problem.startswith('The original price of'):
        answer = first - first * second / Decimal(100)
    if problem.startswith("Last month"):
        answer = first - first * second / Decimal(100)
    if problem.startswith("A "):
        answer = first - first * second / Decimal(100)
    if problem.startswith("The federal income tax"):
        answer = second * first / Decimal(100)
    answer = answer.quantize(Decimal('0.01'))
    return answer
