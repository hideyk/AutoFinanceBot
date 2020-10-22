import random

someRandomText = [
    "Sorry (user), we didn't catch that! 🤦🏻‍♂️🤦🏻‍♀️",
    "They're taking the hobbits to Isengard, (user)!🧙‍♂️",
    "I love you 4000, (user) 💓",
    "That's one small step for my savings, one giant leap for my future portfolio 👨‍🚀",
    'A Mexican magician says he will disappear on the count of 3. He says "uno, dos..." poof. He disappeared without a tres.',
    '''"I'm gonna ask you this one time, *where is (user)?*"\n"Yea I'll do you one better, *who's (user)?*"\n"I'll do you one better, *why is (user)?!?!*"''',
    "We're still pioneers, we've barely begun. Our greatest accomplishments cannot be behind us, because our destiny lies above us 🌟",
    "I'll see you in the beginning, (user) ⏳"
]


def catchRandomText(first_name):
    return someRandomText[random.randint(0, len(someRandomText)-1)].replace("(user)", first_name)
