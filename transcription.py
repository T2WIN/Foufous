from whisper_timestamped import transcribe_timestamped, load_model
import string

POTENTIAL_FILLERS = [
    "donc",
    "mais",
    "alors",
    "genre",
    "attend",
    "attends",
]

REAL_FILLERS = [
    ["du", "coup"],
    ["en", "fait"],
    ["bah"],
    ["ouais"],
]

def flatten(list_of_lists, key = None):
    for sublist in list_of_lists:
        for item in sublist.get(key, []) if key else sublist:
            yield item

def normalize_text(s):
    return s["text"].lower().translate(str.maketrans("", "", string.punctuation))

model = load_model("base")

def get_fillers_events(words, words_without_pauses):
    events = []
    for i, s in enumerate(words):
        print(s)
        if i > 0 and s["text"] == "[*]" and not words[i - 1]["text"].endswith((".", ",", "!", "?")):
            events.append({
                "timestamp": s["start"],
                "type": "(F)iller",
                "note": "bad",
            })

    i = 0
    while i < len(words_without_pauses):
        t = normalize_text(words_without_pauses[i])
        for f in REAL_FILLERS:
            if t == f[0]:
                j = 1
                while j < len(f) and f[j] == normalize_text(words_without_pauses[i + j]):
                    j += 1
                if j == len(f):
                    events.append({
                        "timestamp": words_without_pauses[i]["start"],
                        "type": "(F)iller",
                        "note": "bad",
                    })
                    i += j - 1
                    break

        if t in POTENTIAL_FILLERS and normalize_text(words_without_pauses[i + 1]) in POTENTIAL_FILLERS:
            events.append({
                "timestamp": words_without_pauses[i]["start"],
                "type": "(F)iller",
                "note": "bad",
            })
            i += 1

        i += 1
    
    return sorted(events, key=lambda e: e["timestamp"])

def get_speed(words_without_pauses):
    t = 5.0
    count = 0
    res = {}
    for s in words_without_pauses:
        if s["start"] < t:
            count += 1
        else:
            res[t] = count
            count = 1
            t += 5.0
    return res
    
result = transcribe_timestamped(
    model, "../content/Video/2023_12_02_22_43_40.m4a",
    language="fr",
    detect_disfluencies=True,
)

words = list(flatten(result["segments"], "words"))
words_without_pauses = list(filter(lambda s: s["text"] != "[*]", words))

print(get_fillers_events(words, words_without_pauses))
print(get_speed(words_without_pauses))
