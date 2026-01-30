import random

def test_shuffle_uniqueness():
    prompt = list(range(10))  # simple prompt: [0, 1, 2, ..., 9]

    results = []
    for i in range(5):  # shuffle 5 times
        shuffled = prompt[:]  # copy
        random.shuffle(shuffled)
        results.append(shuffled)
        print(f"Shuffle {i+1}: {shuffled}")

    # check for duplicates
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            if results[i] == results[j]:
                print(f"[Collision] Shuffle {i+1} == Shuffle {j+1}")

test_shuffle_uniqueness()