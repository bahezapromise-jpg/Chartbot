# Week 4 — Rule-Based Chatbot for the Campus Library

Name: Isezerano Theophile · GitHub: GitHub: bahezapromise-jpg

## Overview

This is a rule-based chatbot for the campus library. It uses one regular expression per intent to answer questions about opening hours, borrowing, renewals, fines and printing, and a multi-turn flow to book a study room. Anything it does not understand gets a fallback message that points the reader to the desk.

## Intents

| Tag | Request | Example phrasing |
| --- | --- | --- |
| rooms | Book a study room (multi-turn flow) | i want to book a study room |
| hours | Opening hours | what time do you open |
| borrow | How many books, and for how long | how many books can i take |
| renew | Renewing a loan | can i renew |
| fines | Overdue charges | how much is the fine |
| printing | Printing and photocopying | how much per page |

## Rule ordering

Order used: rooms, hours, renew, borrow, fines, printing. The first pattern that matches answers, so order decides collisions.

**rooms** and **borrow** collided. "i want to book a study room" contains the whole word "book", which borrow also uses ("how long can i keep a book"). rooms is checked first because it is more specific. If the order were reversed, a room request would be answered with the borrowing limit and the booking flow would never start.

A second collision is **renew** and **borrow**: "i want to extend my book" also contains "book", so renew is placed before borrow too. borrow has the broadest keyword, so it is checked after the more specific intents.

## The booking flow

Three values are collected one at a time: the day (mon–sat), then the time (morning, afternoon or evening), then the party size (a number from 1 to 8, matched with `\b([1-8])\b`, so 0, 9 and 12 are rejected). If an answer is not recognised, the same question is asked again and nothing is stored or skipped. After the third value the bot restates all three ("A room on thu, afternoon, for 4 people. Is that correct?") and clears the stored values. Saying "bye" (or exit, quit, goodbye, thanks, murakoze) at any step cancels the booking and clears the collected values.

## Test results

- Test messages: 35
- Returned the expected tag: 32

Failures and their causes:

- `how many books can i take and what are the fines` (expected borrow+fines, got borrow): a genuine overlap, because the message holds two requests and the first match wins. This is routing, not matching.
- `rnw my bk` (expected renew, got fallback): keyword too short. The reader used abbreviations that no sensible keyword matches.
- `can i extend my deadline` (expected fallback, got renew): a word genuinely shared between two intents. "extend" is a renew keyword but here refers to a deadline. No pattern can fix this; it needs intent classification (Week 9).

## Running this notebook

- Open Isezerano_Theophile_Assignment_4.ipynb in Google Colab.
- Run the cells in order. **Do not use Run all** — the chat cell waits for input.

## What was learned

Regular expressions with `\b` let one pattern replace a whole keyword list and stop matches inside longer words such as "bookshop". The order of the rules matters as much as the patterns themselves, because the first match wins. Some failures, such as shared words and two requests in one message, cannot be fixed by patterns and need routing or classification later in the module.

