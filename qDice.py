import re
import requests
import json

class DiceRoller:
    def __init__(self, skipFetch=False):
        self.math_operators_pattern = re.compile(r'[-\*/\^%]')
        self.dice_roll_pattern = re.compile(r"(?i)(?:(?P<dice>\d+)\s*d\s*(?P<sides>\d+)(?P<advantage>[ad])?)|(?P<modifier>[+\-*/]\s*\d+)(?!d)")
        self.randomness = []
        if not skipFetch:
            self.fetch_randomness()

    def flush_randomness(self, verify=False):
        if verify:
            self.fetch_randomness = []
            return True
        return False

    def fetch_randomness(self):
        url = "https://qrng.anu.edu.au/API/jsonI.php?length=1024&type=uint16"
        # url = "https://qrng.anu.edu.au/API/jsonI.php?length=20&type=uint16"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.randomness = data.get('data', [])
            if not self.randomness:
                print("Failed to fetch randomness. Please check your connection or the API status.")
                return False
            else:
                print("Randomness fetched successfully.")
                return True
        except requests.RequestException as e:
            print(f"An error occurred while fetching randomness: {e}")
            return False

    def get_random_int(self, min_val, max_val):
        if not self.randomness:
            return None, "Randomness pool is exhausted. Please fetch more randomness."
        # Use a random number from the pool and scale it to the desired range
        raw_random = self.randomness.pop(0)
        # Scale the uint16 random number to the desired range
        scaled_random = min_val + raw_random % (max_val - min_val + 1)
        return scaled_random, None

    def roll_single_die(self, num_sides, advantage=None):
        if advantage == 'a':
            roll1, msg = self.get_random_int(1, num_sides)
            roll2, _ = self.get_random_int(1, num_sides)
            if msg:
                return None, msg
            roll = max(roll1, roll2)
            return roll, "Advantage"
        elif advantage == 'd':
            roll1, msg = self.get_random_int(1, num_sides)
            roll2, _ = self.get_random_int(1, num_sides)
            if msg:
                return None, msg
            roll = min(roll1, roll2)
            return roll, "Disadvantage"
        else:
            roll, msg = self.get_random_int(1, num_sides)
            if msg:
                return None, msg
            return roll, "Normal"
    
    def contains_math_operators(self, s):
        match = self.math_operators_pattern.search(s)
        return bool(match), match.group() if match else None

    def _roll_dice(self, input_string, verbose=False):
        if not input_string:
            return "Input string is empty"

        matches = self.dice_roll_pattern.finditer(input_string)
        total = 0
        full_expr = []

        for match in matches:
            groups = match.groupdict()

            # Handling standalone numbers and modifiers
            if groups['modifier']:
                operator = groups['modifier'][0]
                value = int(groups['modifier'][1:].strip())

                if operator == '+':
                    total += value
                elif operator == '-':
                    total -= value
                elif operator == '*':
                    total *= value
                elif operator == '/':
                    total //= value

                if full_expr:
                    mod_str = f"{operator}{value}"
                else:
                    mod_str = str(value)

                full_expr.append(f"{mod_str} (Modifier)" if verbose else mod_str)
                continue

            # Handling dice rolls
            num_dice = int(groups['dice'])
            num_sides = int(groups['sides'])
            advantage = groups['advantage']

            rolls = []
            roll_types = []

            for _ in range(num_dice):
                roll, roll_type = self.roll_single_die(num_sides, advantage)
                rolls.append(roll)
                roll_types.append(roll_type)

            total += sum(rolls)
            roll_type_str = roll_types[0] if roll_types else ""
            roll_str = f"({'+'.join(map(str, rolls))}) [{roll_type_str}]"
            
            if full_expr:
                roll_str = '+' + roll_str

            full_expr.append(roll_str)

        if not full_expr:
            return "No valid dice notations found"

        return f"Rolls: {''.join(full_expr)}, Total: {total}"

    def roll_dice(self, input_string):
        try:
            return self._roll_dice(input_string)
        except:
            return "Quantum Entropy Exceeded. Please make a new API request."

    def verbose_roll_dice(self, input_string):
        try:
            return self._roll_dice(input_string, verbose=True)
        except:
            return "Quantum Entropy Exceeded. Please make a new API request."

if __name__ == '__main__':
    dice_roller = DiceRoller()
    while True:
        print(dice_roller.roll_dice(str(input("Enter: "))))
        print(dice_roller.verbose_roll_dice(str(input("Enter: "))))
