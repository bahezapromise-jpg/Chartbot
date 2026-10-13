# Week 5: Library Chatbot v2

**Name:** Isezerano Theophile · **GitHub:** bahezapromise-jpg · **Course:** Chatbots Development (AITCD001), Assignment 5

## Overview

The campus library chatbot from Assignment 4 now answers through a router of handler functions instead of giving every message one tag. It can answer several requests in one message (in the order asked, with a booking question always last), and it remembers the reader's name and the last intent across turns. A side question during a room booking is answered and the booking question is asked again.

## Intents and handlers

| **Intent** | **Handler** | **Fixed reply, or worked out from the message?** |
| --- | --- | --- |
| name | handle_name | Worked out from the message: reads the name after "my name is" and stores it in `context` with a capital letter. |
| rooms | handle_rooms | Neither: starts the booking flow (`start_booking()`), or says a booking is already under way. |
| hours | handle_hours | Fixed reply from `RESPONSES`. |
| borrow | handle_borrow | Fixed reply from `RESPONSES`. |
| renew | handle_renew | Fixed reply from `RESPONSES`. |
| fines | handle_fines | Worked out from the message: finds the number of days and calculates the fine. |
| printing | handle_printing | Fixed reply from `RESPONSES`. |
| greeting | handle_greeting | Fixed reply: says it is an automated service, not a librarian. |

## How the fines handler works

It searches the message for a number followed by "day" or "days" (the pattern `LATE`, `\b(\d+) days?\b`). If it finds one, it turns the number into an integer, multiplies it by 200 RWF (the fine per book per day) and uses `min()` so the result never goes above the 5,000 RWF cap. The reply then states that figure, for example 3 days gives 600 RWF and 40 days gives 5,000 RWF. If the message names no number of days, it returns the general fines reply from `RESPONSES`.

## Several requests in one message

`split_requests` lowers the message and cuts it at the connectors *and*, *but*, *also*, *then* and a question mark (a comma does not cut). Each piece is tidied with `normalise()` and empty pieces are dropped. `route` then matches each piece with `match()`, skips pieces that match nothing, and skips an intent already found, so the result is one (intent, request) pair per understood request, in order. An overlap inside one request is settled by the rule table: the first rule that matches wins, so "can i renew a late book" is a renewal, because renew is above fines in the table.

`ASKS` holds `rooms`. The reply of the rooms handler is a question ("Which day would you like the room?") that the reader has to answer next, so `respond` puts it last. If it came first, the reader would answer the other replies' content with the booking question already behind them, and the next message would be taken as an answer to the wrong thing.

## Memory

`context` is a dictionary with two entries for the whole conversation: `name` (the reader's name, stored with a capital first letter) and `last_intent` (the last intent answered). "bye" clears both `context` and the booking flow, and the goodbye uses the name if there is one.

The follow-up rule: if a message matches no intent, `follow_up` checks whether the last intent answered was `fines` and whether the message names a number of days. If both are true it is answered as a fines question ("and for 10 days?" gives 2,000 RWF). After any other answer it returns nothing, so the message falls to the fallback.

During a booking, the flow sees each message first. If the flow does not move on, the message was not an answer: it is routed and answered, and the booking question is asked again after the answer. If nothing is found in it, only the booking question is asked again. The booking is kept either way.

## Test results

- Assignment 4 test set, one tag per message: **32** of 35
- Assignment 4 test set, routed: **33** of 35

Routing fixes `'how many books can i take and what are the fines'` (expected borrow+fines). Still failing: `'rnw my bk'` (expected renew, got fallback) and `'can i extend my deadline'` (expected fallback, got renew).

## Test conversations

| **#** | **What it tests** | **Expected** | **What the chatbot did** | **Pass or fail** | **If it failed: cause and part responsible** |
| --- | --- | --- | --- | --- | --- |
| 1 | Two requests joined by "and" | Both answered, in the order asked: the opening hours, then the printing prices. | Gave the opening hours, then the printing prices, in that order. | Pass | |
| 2 | One request that matches two intents | The renewal reply only. "late" also matches fines, but renew is higher in the table, and the reader asked one thing. | Gave only the renewal reply. | Pass | |
| 3 | The question goes last | The opening hours first. The reply ends with the booking question (which day), because that is what the reader must answer next. | Gave the opening hours, then "Which day would you like the room? Monday to Saturday." | Pass | |
| 4 | Remembering a name | A greeting, the name acknowledged, the printing prices, and a goodbye that uses the name Grace. | Greeting, "Nice to meet you, Grace.", the printing prices, then "Thank you, Grace. Murakoze." | Pass | |
| 5 | A follow-up with no intent of its own | The fine for 3 days (600 RWF), then the second message answered as a fines question: the fine for 10 days (2,000 RWF). | "For 3 days late, the fine is 600 RWF per book." then "For 10 days late, the fine is 2,000 RWF per book." | Pass | |
| 6 | A side question during a booking | The hours are given and the time question asked again. The booking then completes with a confirmation for Friday afternoon, 4 people. | Gave the hours and asked "Morning, afternoon or evening?" again. The booking then completed: "A room on fri, afternoon, for 4 people. Is that correct?" (the flow stores the day as the three letters "fri"). | Pass | |
| 7 | Two questions with no connecting word | Both answered: the borrowing limit, then the fines. | Answered only the borrowing limit. The fines question was never answered. | Fail | No connector between the two questions, so `split_requests` returned one piece, and in it the first rule to match (borrow) won. Part responsible: the split (`split_requests`). |
| 8 | An answer that is also a question | The evening slot is taken, and the closing time on Saturday is given as well. | Replied only "How many people? Between 1 and 8." The closing time was not given, and nothing was said about the evening slot being taken. | Fail | `reply_to` gives the message to the flow first; `continue_booking` accepted "evening", moved on, and its reply was returned at once, so the rest of the message was never routed. The chatbot also has no data on which slots are taken. Part responsible: the flow (`continue_booking`, and the order in `reply_to`). |
| 9 | A conversation that tests memory | "my name is theophile" gives "Nice to meet you, Theophile." "i am 5 days late what is the fine" gives 1,000 RWF. "and for 30 days?" has no intent of its own, but after a fines answer it is a fines question: 6,000 RWF, capped at 5,000 RWF. "bye" gives "Thank you, Theophile. Murakoze." | Exactly that: "Nice to meet you, Theophile.", 1,000 RWF for 5 days, 5,000 RWF for 30 days, "Thank you, Theophile. Murakoze." | Pass | |
| 10 | A conversation designed to break the chatbot | "i do not want to book a study room": the reader refuses, so the chatbot should not start a booking (a polite fallback would be fine). I expected it to start one anyway, because the rules only read words. | Started the booking: "Which day would you like the room? Monday to Saturday." | Fail | The rule table matches the words "study room" and has no way to read the negation "do not want to". Part responsible: the rule table (`RULES`). |

## Known limitations

- Conversation 7: two questions with no connector are read as one request and only the first matching intent is answered (cause: the split).
- Conversation 8: an answer that also contains a question is taken as an answer only; the question is lost, and the chatbot has no availability data (cause: the flow, which sees the message before the router).
- Conversation 10: a refusal such as "i do not want to book a study room" starts a booking (cause: the rule table matches words, not meaning).
- `'rnw my bk'` returns the fallback (cause: no pattern in the rule table contains these abbreviations).
- `'can i extend my deadline'` is answered as a renewal (cause: "extend" is in the renew pattern whatever is being extended).
- Conversation 6 shows the day in the booking confirmation as "fri" (cause: the provided booking flow stores the first three letters of the day).

## Running this notebook

- Open Isezerano_Theophile_Assignment_5.ipynb in Google Colab.
- Run the cells in order. The chat cell waits for input, so do not use Run all.

## What was learned

A router with one handler per intent makes the chatbot easier to extend: a new intent needs a rule, a handler and one entry in `HANDLERS`. Splitting a message at connectors lets one message get several answers, but only where the reader actually wrote a connector, and the order of the rule table and of the reply still decides what the reader sees. Memory helps with follow-ups and side questions, but it needs care about which part sees a message first, because that is what broke conversation 8.
