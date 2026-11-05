# The Week 9 pizza chatbot as a web page (Week 10 Streamlit demo).
# app.py, requirements.txt and intent_classifier.joblib go together in one GitHub repository.
# share.streamlit.io: Create app, choose the repository, main file app.py, Deploy.

# ---------------------------------------------------------------------------
# PROVIDED: the Week 6 chatbot, complete, as it stood at the end of Week 6.
# Run this cell. Nothing in it needs changing today.
# ---------------------------------------------------------------------------


# ============================== Week 4: cleaning, the pattern table, the matcher, the order flow


import re


def normalise_v2(text):
    """Remove punctuation (keeping the colon of 21:00), lowercase, trim."""
    return re.sub(r"[^\w\s:]", "", text).lower().strip()


RULES = [
    ('cancel'  , r"\bcancel\w*\b|\brefund\w*\b|\bcall it off\b|\bchanged my mind\b"),
    ('hours'   , r"\bhours?\b|\bopen\w*\b|\bclos\w*\b|\bwhat ?time\b|\bstill (open|trading)\b|\bshut\b|\b\d{1,2}\s?[ap]m\b|\b\d{1,2}:\d{2}\b|\bthere at\b"),
    ('delivery', r"\bdeliver\w*\b|\bdelivary\b|\bdelivr\b|\bbring\b|\bdrop it\b|\bcome to\b|\bsend\b|\bkg ?\d+\b"),
    ('price'   , r"\bprices?\b|\bpricing\b|\bcosts?\b|\bhow ?much\b|\bhw ?mch\b|\brwf\b|\bfrancs?\b|\bdamage\b|\brates?\b|\bpirce\b|\b\d{4,}\b"),
    ('menu'    , r"\bmenu\w*\b|\bmnu\b|\boptions?\b|\btoppings?\b|\bwhat do you (got|have|sell)\b|\bshow me the list\b"),
    ('vegan'   , r"\bvegan\w*\b|\bvegetar\w*\b|\bveggie\b|\bvegetarain\b"),
    ('order'   , r"\border\b|\bordering\b|\bbuy\b|\bwant\b|\bcan i get\b|\bid like\b|\b\d+ pizzas?\b|\b\d+ for \d"),
]


def match_week4(message):
    """Return the tag of the first pattern that matches, or the fallback."""
    text = normalise_v2(message)
    for tag, pattern in RULES:
        if re.search(pattern, text):
            return tag
    return "fallback"


flow = {"step": None, "collected": {}}
SIZES   = r"small|medium|large|big|regular"
METHODS = r"deliver\w*|collect|pick\s?up"


def start_order():
    flow["step"] = "size"
    flow["collected"] = {}
    return "Small, medium or large?"


def reset_flow():
    flow["step"] = None
    flow["collected"] = {}


EXIT_WORDS = ("bye", "goodbye", "exit", "quit", "thanks", "murakoze")


# ============================== Week 5, Part 1: handlers, the router, several requests in one message


def handle_hours(text):
    return "We are open 10:00 to 22:00, every day."


def handle_delivery(text):
    return "We deliver anywhere inside Kigali. Delivery is 1,500 RWF."


PRICES = {"small": "6,000 RWF", "medium": "9,000 RWF", "large": "12,000 RWF"}
SIZE = r"\b(small|medium|large)\b"


def handle_price(text):
    """A reply worked out from the message: the price of the size named, if any."""
    found = re.search(SIZE, text)
    if found:
        size = found.group(1)
        return f"A {size} pizza is {PRICES[size]}."
    return "A small pizza is 6,000 RWF, a medium 9,000 and a large 12,000."


def handle_menu(text):
    return "Margherita, pepperoni, mushroom, vegan and BBQ chicken."


def handle_vegan(text):
    return "Yes, any pizza can be made with vegan cheese."


def handle_order(text):
    """Starting an order changes the chatbot's state, which a fixed reply cannot do."""
    if flow["step"] is not None:
        return "Your order is already under way."
    return start_order()


def handle_cancel(text):
    """The right reply depends on whether an order is in progress."""
    if flow["step"] is not None:
        reset_flow()
        return "Your order has been cancelled."
    return "There is no order in progress to cancel."


HANDLERS = {
    "cancel":   handle_cancel,
    "hours":    handle_hours,
    "delivery": handle_delivery,
    "price":    handle_price,
    "menu":     handle_menu,
    "vegan":    handle_vegan,
    "order":    handle_order,
}
RULES.append(("greeting", r"\bhello\b|\bhi\b|\bhey\b|\bmuraho\b|\bmwaramutse\b|\bmwiriwe\b"))
CONNECTORS = r"\band\b|\bbut\b|\balso\b|\bthen\b|[?]"


def split_requests(message):
    """Break one message into the separate requests it contains."""
    requests = []
    for part in re.split(CONNECTORS, message.lower()):
        part = normalise_v2(part)
        if part != "":
            requests.append(part)
    return requests


def route(message):
    """Return one (intent, request) pair for each request the chatbot understood."""
    found = []
    seen = []
    for request in split_requests(message):
        tag = match_week4(request)          # first match wins, inside ONE request
        if tag != "fallback" and tag not in seen:
            seen.append(tag)
            found.append((tag, request))
    return found


ASKS = ["order"]
UNMATCHED = []
FALLBACK = ("Sorry, I did not understand. I can help with hours, delivery, prices, "
            "the menu, vegan options and orders.")


# ============================== Week 5, Part 2: context, names, values, follow-ups, the complete turn


context = {"name": None, "last_intent": None}
NAME = r"\bmy name is (\w+)"


def handle_name(text):
    found = re.search(NAME, text)
    if found:
        context["name"] = found.group(1).capitalize()
        return f"Nice to meet you, {context['name']}."
    return "Sorry, I did not catch your name."


RULES.insert(0, ("name", r"\bmy name is\b"))
HANDLERS["name"] = handle_name


def handle_greeting(text):
    """The greeting now uses what the context holds."""
    if context["name"] is not None:
        return f"Muraho, {context['name']}! How can I help?"
    return "Muraho! I am the Kigali Pizza assistant, a computer program. How can I help?"


HANDLERS["greeting"] = handle_greeting
TOPPINGS = r"margherita|pepperoni|mushroom|vegan|chicken"


def continue_order(message):
    """Week 4's flow, now storing the VALUE that matched rather than the whole message."""
    text = normalise_v2(message)

    if flow["step"] == "size":
        found = re.search(SIZES, text)
        if found:
            flow["collected"]["size"] = found.group()
            flow["step"] = "topping"
            return "Which topping? Margherita, pepperoni, mushroom or vegan."
        return "Small, medium or large?"

    if flow["step"] == "topping":
        found = re.search(TOPPINGS, text)
        if found:
            flow["collected"]["topping"] = found.group()
            flow["step"] = "method"
            return "Deliver or collect?"
        return "Margherita, pepperoni, mushroom or vegan?"

    if flow["step"] == "method":
        found = re.search(METHODS, text)
        if found:
            flow["collected"]["method"] = found.group()
            c = flow["collected"]
            reset_flow()
            return (f"A {c['size']} {c['topping']}, {c['method']}. "
                    "Is that correct?")
        return "Deliver or collect?"

    return "Sorry, something went wrong. Starting again."


def follow_up(text):
    """A message with no intent of its own, read in the light of the previous one."""
    if context["last_intent"] == "price" and re.search(SIZE, text):
        return [("price", text)]
    return []


def run_conversation(turns):
    """Play a scripted conversation from a clean start, printing both sides."""
    reset_flow()
    reset_context()
    for message in turns:
        print("You:", message)
        print("Bot:", reply_to(message))
    print()


# ============================== Week 6: validation, errors, the counted fallback, a person, local phrasing


MAX_LENGTH = 300
ASK_AGAIN = ("Please type a question. I can help with hours, "
             "delivery, prices, the menu and orders.")
IN_WORDS = "Please type your question in words."
TOO_LONG = "That is a long message. Could you ask one thing at a time?"


def validate(message):
    """Return a reply if the message cannot be used; None if it can."""
    if message is None:
        return ASK_AGAIN
    text = message.strip()
    if text == "":
        return ASK_AGAIN
    if normalise_v2(text) == "":
        return IN_WORDS
    if len(text) > MAX_LENGTH:
        return TOO_LONG
    return None


AREAS = {"kicukiro": "1,500 RWF", "remera": "1,000 RWF",
         "kimihurura": "1,000 RWF", "nyamirambo": "2,000 RWF"}
AREA = r"\bto (\w+)"
from datetime import datetime
ERROR_LOG = []


def log_error(message, error):
    ERROR_LOG.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "error": type(error).__name__ + ": " + str(error),
    })


SORRY = "Sorry, something went wrong on my side. Please try again, or type 'human'."


def safe_handle(tag, request):
    """Run one handler. If it raises an error, log it and apologise instead of crashing."""
    try:
        return HANDLERS[tag](request)
    except Exception as error:
        log_error(request, error)
        return SORRY


def respond(found):
    """Week 5's respond, now calling every handler through safe_handle."""
    answers = []
    questions = []
    for tag, request in found:
        reply = safe_handle(tag, request)
        if tag in ASKS:
            questions.append(reply)
        else:
            answers.append(reply)
    return " ".join(answers + questions)


HUMAN_WORDS = ("human", "staff", "agent", "person")
HANDOVER = "Connecting you to a member of staff. They can see this conversation."
STILL_LOST = ("Sorry, I still did not understand. Type 'human' to reach a member of staff, "
              "or ask about hours, delivery, prices, the menu or orders.")
context["fallbacks"] = 0


def fallback(message):
    """Week 3's fallback, now counting: the second miss in a row offers a person."""
    UNMATCHED.append(message)
    context["fallbacks"] = context["fallbacks"] + 1
    if context["fallbacks"] >= 2:
        return STILL_LOST
    return FALLBACK


def reset_context():
    context["name"] = None
    context["last_intent"] = None
    context["fallbacks"] = 0


def reply_to(message):
    """One turn of the Week 6 chatbot."""
    # 0. Validate before anything else: the message must be usable at all.
    problem = validate(message)
    if problem is not None:
        return problem
    text = normalise_v2(message)

    # 1. The exit (Week 4). Leaving clears both memories.
    if text in EXIT_WORDS:
        name = context["name"]
        reset_flow()
        reset_context()
        if name is not None:
            return f"Thank you, {name}. Murakoze."
        return "Thank you for contacting us. Murakoze."

    # 2. A person, on request, at any point.
    if text in HUMAN_WORDS:
        reset_flow()
        return HANDOVER

    # 3. Inside an order, the flow sees the message first (Week 5).
    if flow["step"] is not None:
        step_before = flow["step"]
        flow_reply = continue_order(message)
        if flow["step"] != step_before:
            return flow_reply
        found = route(message)
        if len(found) == 0:
            return flow_reply
        reply = respond(found)
        if flow["step"] is not None:
            reply = reply + " " + flow_reply
        return reply

    # 4. Route; then the context; then the fallback, which now counts.
    found = route(message)
    if len(found) == 0:
        found = follow_up(text)
    if len(found) == 0:
        return fallback(message)

    context["fallbacks"] = 0                # understood: the count starts again
    last_tag, last_request = found[-1]
    context["last_intent"] = last_tag
    return respond(found)


SERVED = "We deliver to Kicukiro, Remera, Kimihurura and Nyamirambo."


def handle_delivery(text):
    """The repaired version: check the area is known BEFORE looking it up."""
    found = re.search(AREA, text)
    if found:
        area = found.group(1)
        place = area.capitalize()
        if area in AREAS:
            return f"Delivery to {place} is {AREAS[area]}."
        return f"Sorry, we do not deliver to {place} yet. " + SERVED
    return "We deliver anywhere inside Kigali. Delivery is 1,500 RWF."


HANDLERS["delivery"] = handle_delivery
PHRASING = [
    'whats the damage',
    'are you still trading',
    'can you drop it at my place',
    'do you come to kicukiro',
    'id like two pizzas',
    'can i get a pizza',
    'what do you got',
    'show me the list',
    'i changed my mind',
    'call it off',
    'are you shut',
    'what are the rates',
    'do u delivr',
    'hw mch',
    'vegetarain',
    'pirce list',
    'mnu',
    'delivary',
    'wat tym u opn',
    'cancle',
    'muraho',
    'ni angahe',
    'ndashaka pizza',
    'murakoze',
    'mwaramutse',
]


def not_understood(messages):
    """Run each message from a clean start. Return the ones that ended up in UNMATCHED."""
    missed = []
    for message in messages:
        reset_flow()
        reset_context()
        before = len(UNMATCHED)
        reply_to(message)
        if len(UNMATCHED) > before:
            missed.append(message)
    reset_context()
    return missed


def add_phrasing(tag, pattern):
    """Add phrasing to an intent's OWN rule, so the intent keeps its place in the table."""
    for i in range(len(RULES)):
        if RULES[i][0] == tag:
            RULES[i] = (tag, RULES[i][1] + "|" + pattern)


add_phrasing("price", r"\bangahe\b")
add_phrasing("order", r"\bndashaka\b")


print(f"Week 6 chatbot loaded: {len(RULES)} rules, {len(HANDLERS)} intents routed")


# ---------------------------------------------------------------------------
# PROVIDED: what Week 8 added. spaCy with the entity ruler for Kigali areas, sizes and
# toppings; extract(), which reads the details of a message as slots; the delivery handler
# that reads the AREA entity; and rule_intent(), the rule table used as an intent detector.
# Run this cell. Nothing in it needs changing today.
# ---------------------------------------------------------------------------
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:                  # not installed yet: install it once
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

AREA_NAMES = ["kicukiro", "remera", "kimihurura", "nyamirambo",
              "gisozi", "kacyiru", "kimironko", "nyarutarama",
              "gikondo", "kanombe", "kibagabaga", "nyabugogo",
              "kiyovu", "kagugu", "nyarugenge"]
SIZE_NAMES = ["small", "medium", "large"]
TOPPING_NAMES = ["margherita", "pepperoni", "mushroom",
                 "vegan", "chicken"]

patterns = []
for name in AREA_NAMES:
    patterns.append({"label": "AREA",
                     "pattern": [{"LOWER": name}]})
for name in SIZE_NAMES:
    patterns.append({"label": "SIZE",
                     "pattern": [{"LOWER": name}]})
for name in TOPPING_NAMES:
    patterns.append({"label": "TOPPING",
                     "pattern": [{"LOWER": name}]})

if "entity_ruler" in nlp.pipe_names:     # run again: start afresh
    nlp.remove_pipe("entity_ruler")
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns(patterns)


SLOTS = ("AREA", "SIZE", "TOPPING", "TIME", "DATE")


def extract(text):
    """Every detail given in one message, as named slots."""
    doc = nlp(text.lower())
    slots = {}
    for ent in doc.ents:
        if ent.label_ in SLOTS:
            slots[ent.label_.lower()] = ent.text
        elif ent.label_ == "CARDINAL":
            slots["quantity"] = ent.text
    return slots


NO_AREA = ("We deliver anywhere inside Kigali. "
           "Delivery is 1,500 RWF.")


def handle_delivery(text):
    """Week 8: read the AREA entity, not the word after to."""
    area = None
    for ent in nlp(text).ents:
        if ent.label_ == "AREA" and area is None:
            area = ent.text.lower()
    if area is None:
        return NO_AREA
    place = area.capitalize()
    if area in AREAS:
        return f"Delivery to {place} is {AREAS[area]}."
    sorry = f"Sorry, we do not deliver to {place} yet. "
    return sorry + SERVED


HANDLERS["delivery"] = handle_delivery


def rule_intent(text):
    """The Week 6 rules as an intent detector."""
    found = route(text)
    if len(found) == 0:
        return "out_of_scope"
    return found[0][0]


print("Week 8 additions loaded:", nlp.pipe_names)


import joblib

classifier = joblib.load("intent_classifier.joblib")


THRESHOLD = 0.2


def classify(text):
    """The intent with the highest score, and that score."""
    scores = classifier.predict_proba([text])[0]
    best = scores.argmax()
    return str(classifier.classes_[best]), float(scores[best])



if "route_rules" not in globals():     # run again safely: keep the original
    route_rules = route


def route(message):
    """Week 9: the classifier picks the intent of each request."""
    found = []
    seen = []
    for request in split_requests(message):
        if re.search(NAME, request):          # a rule, where a rule is certain
            tag = "name"
        else:
            tag, score = classify(request)
            if score < THRESHOLD:
                tag = "out_of_scope"           # not sure: let the fallback decide
        if tag != "out_of_scope" and tag not in seen:
            seen.append(tag)
            found.append((tag, request))
    return found



QUESTION = {"size": "Small, medium or large?",
            "topping": "Which topping? Margherita, pepperoni, mushroom or vegan.",
            "method": "Deliver or collect?"}


def handle_order(text):
    """Week 9: start the order with the details the message already gives."""
    if flow["step"] is not None:
        return "Your order is already under way."
    start_order()
    slots = extract(text)                  # Week 8: the entity ruler
    if "size" in slots:
        flow["collected"]["size"] = slots["size"]
        flow["step"] = "topping"
        if "topping" in slots:
            flow["collected"]["topping"] = slots["topping"]
            flow["step"] = "method"
    return QUESTION[flow["step"]]


HANDLERS["order"] = handle_order


BOT_NAME = "Kigali Pizza Assistant"
TOPICS = "hours, delivery, prices, the menu, vegan options and orders"


# ---------------------------------------------------------------------------
# The web page. Paste this at the END of app.py, below your chatbot's code.
# ---------------------------------------------------------------------------
import streamlit as st

st.title(BOT_NAME)
st.caption(f"An automated assistant: a computer program. It can help with {TOPICS}.")

if "history" not in st.session_state:
    st.session_state.history = []        # this visitor's conversation, and only theirs

message = st.chat_input("Type a message")
if message:
    # Streamlit runs this whole file again for every message, so the chatbot's
    # memory (flow, context) starts empty each time. Replaying THIS visitor's
    # earlier messages rebuilds their conversation, and only theirs.
    reset_flow()
    reset_context()
    for who, text in st.session_state.history:
        if who == "user":
            reply_to(text)
    reply = reply_to(message)
    st.session_state.history.append(("user", message))
    st.session_state.history.append(("assistant", reply))

for who, text in st.session_state.history:
    with st.chat_message(who):
        st.write(text)

