from flask import Flask, render_template, jsonify, request
import qDice

app = Flask(__name__)
qDiceRoller = qDice.DiceRoller(skipFetch=False)

@app.route('/')
def home():
    return render_template('index.html', randomness=len(qDiceRoller.randomness))

@app.route('/roll', methods=['POST'])
def roll():
    data = request.json
    str_expression = data.get('expression', '1d6')
    rolls = qDiceRoller.roll_dice(str_expression)
    return jsonify({'rolls': rolls, 'randomness': len(qDiceRoller.randomness)})

@app.route('/fetch_randomness', methods=['POST'])
def fetch_randomness():
    success = qDiceRoller.fetch_randomness()
    status = 'Randomness replenished' if success else 'Failed to replenish randomness. Please try again later.'
    return jsonify({'status': status, 'success': success, 'randomness': len(qDiceRoller.randomness)})

if __name__ == '__main__':
    from waitress import serve
    # print("Fetching randomness")
    # qDiceRoller.fetch_randomness()
    # print("Fetched")
    serve(app, host='0.0.0.0', port=5050)
