
- **A4:** `char_wb` pads each word with a space on both sides (" menu "), then takes every 2-letter piece: ` m`, `me`, `en`, `nu`, `u `.

---

## Part B: Measure by hand
# Week 9 Activity: Predict, Measure and Choose

**Course:** Chatbots Development (AITCD001), Learning Outcome 3
**Name:** Isezerano Theophile
**Date:** ____________

---

## Part A: Predict, then run

| # | Code (summary) | What it prints |
|---|----------------|----------------|
| A1 | `CountVectorizer` fitted on `"I want a pizza"`, `"a large pizza please"`; print feature names | `['large', 'pizza', 'please', 'want']` |
| A2 | `CountVectorizer` `fit_transform` on `"pizza pizza please"`, `"large pizza"`; print `X.toarray()` | `[[0 2 1]` <br> ` [1 1 0]]` |
| A3 | `TfidfVectorizer` fitted on `"pizza pizza please"`, `"large pizza"`; print each word and its idf | `large 1.41` <br> `pizza 1.0` <br> `please 1.41` |
| A4 | `char_wb` analyzer, `ngram_range=(2, 2)`, applied to `"menu"` | `[' m', 'me', 'en', 'nu', 'u ']` |

**Reasoning**

- **A1:** Words are lowercased and sorted alphabetically. One-letter words ("I", "a") are ignored by default, so the vocabulary is `large, pizza, please, want`.
- **A2:** The vocabulary is `large, pizza, please`. "pizza pizza please" gives `[0, 2, 1]` and "large pizza" gives `[1, 1, 0]`.
- **A3:** idf = ln((1 + n) / (1 + df)) + 1, with n = 2 messages.
  - pizza is in 2 of 2 messages: ln(3/3) + 1 = **1.0**
  - large and please are each in 1 of 2 messages: ln(3/2) + 1 = 1.405, which rounds to **1.41**
Confusion matrix (rows = real label, columns = guess):

| real label | guessed hours | guessed price | guessed menu | total |
|------------|:---:|:---:|:---:|:---:|
| hours | 8 | 1 | 1 | 10 |
| price | 2 | 7 | 1 | 10 |
| menu  | 0 | 3 | 7 | 10 |

**1. Correct answers and accuracy**

The correct answers are on the diagonal: 8 + 7 + 7 = **22 of 30**.
Accuracy = 22 / 30 = **0.733 (about 73%)**.

**2. Precision of price**

Messages the classifier called price (price column): 1 + 7 + 3 = 11. Of these, 7 really were price.
Precision = 7 / 11 = **0.64**.

**3. Recall of price**

Of the 10 messages that really were price, the classifier found 7.
Recall = 7 / 10 = **0.70**.

**4. F1 of price**

F1 = 2 × precision × recall / (precision + recall)
F1 = 2 × 0.64 × 0.70 / (0.64 + 0.70) = 0.896 / 1.34 ≈ **0.67**
(Exact fractions: 14 / 21 = 0.667.)

**5. Most frequent mistake**

The most frequent mistake is **menu classified as price**, which happened **3 times** (the next most frequent is price classified as hours, 2 times).

To reduce it, add training messages for **menu that ask about items without price words**, for example "what pizzas do you sell" and "do you have vegan options". Pairing them with clear price messages such as "how much is a large" helps the classifier tell the two intents apart.

---

## Part C: Choose a threshold

**1. Confident wrong answers with no threshold (0.0)**

With no threshold, **17** test messages get a confident wrong answer. The rules gave **5**.

**2. Best threshold**

**Threshold 0.2.** It keeps 72 right answers (the same as 0.0 and 0.1) but cuts the confident wrong answers from 17 to 4. Higher thresholds lose right answers (63 at 0.25, 55 at 0.3).

**3. Fallback rate at 0.2**

23 of the 90 test messages fell back: 23 / 90 ≈ **26%**.
14 of those fallbacks were missed real requests, so 23 − 14 = **9** were out-of-scope messages, where falling back is the right reply.

**4. Clinic chatbot**

The clinic should use a **higher threshold**. A wrong answer can send a patient to the wrong appointment, so the chatbot should answer only when it is very sure.

**The cost:** more fallbacks and more missed real requests, so more patients are passed to a person and the chatbot automates less. For example, at 0.4 in the table there are 0 wrong answers, but 50 messages are missed.

---

## Part D: The classifier on my own dataset

**My chatbot's domain:** ______________________________  
☐ pizza dataset used instead (repeat Part D at home once `intents.csv` exists)

| # | What to record | Result |
|---|----------------|--------|
| 1 | Rows, training and test; number of labels | ___ training, ___ test, ___ labels |
| 2 | Accuracy with words, and with characters | words ___%, characters ___% |
| 3 | Fallback rate at 0.2 | ___% |
| 4 | Weakest intent (lowest F1), and one reason | intent: ______ (F1 ___); reason: ______ |
| 5 | Baseline of the rule table of the same chatbot (Assignment 8, Step 6) | ___ |

**Does the classifier beat the rules on this dataset?**

Classifier accuracy (characters): ___%. Rule table baseline: ___%.
Answer: ______________________________

**One change to the dataset that would help the weakest intent:**

______________________________
