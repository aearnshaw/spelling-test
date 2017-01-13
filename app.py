import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def launch():
    msg = render_template('welcome')
    return question(msg)


@ask.intent("AMAZON.CancelIntent")
def cancel():
    return statement('')


@ask.intent("AMAZON.StopIntent")
def stop():
    return statement('')


@ask.intent("NumberWordsIntent", convert={'now': int})
def get_now(now):
    session.attributes['now'] = now
    session.attributes['w'] = 1
    session.attributes['words'] = [None] * now
    session.attributes['spelling'] = False
    session.attributes['correct'] = 0
    msg = render_template('word', w=1)
    return question(msg)


@ask.intent("LetterIntent")
def get_letters(a, b, c, d, e, f, g, h, i, j):
    letters = [a, b, c, d, e, f, g, h, i, j]
    new_letters = [letter for letter in letters if letter is not None]
    word = ''.join(new_letters).replace('.', '').lower()
    if not session.attributes['spelling']:
        w = session.attributes['w']
        session.attributes['words'][w - 1] = word
        # go on to next word
        w = w + 1
        now = session.attributes['now']
        if w <= now:
            session.attributes['w'] = w
            msg = render_template('word', w=w)
        else:
            session.attributes['spelling'] = True
            session.attributes['w'] = 1
            msg1 = render_template('repeat', words=session.attributes['words'])
            msg2 = render_template('spell', word=session.attributes['words'][0])
            msg = msg1 + ' ' + msg2
        return question(msg)
    else:
        w = session.attributes['w']
        now = session.attributes['now']
        if session.attributes['words'][w - 1] == word:
            msg1 = render_template('win')
            session.attributes['correct'] += 1 
        else:
            msg1 = render_template('lose')
        w = w + 1
        if w <= now:
            session.attributes['w'] = w
            msg2 = render_template('spell', word=session.attributes['words'][w - 1]) 
            msg = msg1 + " " + msg2
            return question(msg)
        else:
            msg2 = render_template('end', correct=session.attributes['correct'], now=now)
            msg = msg1 + " " + msg2
            return statement(msg).simple_card("Spelling Test", msg)


if __name__ == '__main__':
    app.run(debug=True)

