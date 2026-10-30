import streamlit as st
import random
import json
import html
import urllib.request
import urllib.error

# ------------------------------------------------------------
# QUIZLAB - Streamlit version of the original Tkinter quiz
# ------------------------------------------------------------

st.set_page_config(
    page_title="QuizLab | Online Quiz",
    page_icon="✦",
    layout="centered",
)

LETTERS = ["A", "B", "C", "D"]

CATEGORIES = {
    "Any Category": None,
    "General Knowledge": 9,
    "Science & Nature": 17,
    "Computers": 18,
    "Mathematics": 19,
    "Sports": 21,
    "Geography": 22,
    "History": 23,
    "Vehicles": 28,
    "Animals": 27,
}

BACKUP_QUESTIONS = [
    {
        "question": "Which keyword is used to define a function in Python?",
        "options": ["A. function", "B. def", "C. define", "D. fun"],
        "answer": "B", "correct_text": "def", "category": "Computers"
    },
    {
        "question": "Which data type stores True or False?",
        "options": ["A. int", "B. str", "C. bool", "D. list"],
        "answer": "C", "correct_text": "bool", "category": "Computers"
    },
    {
        "question": "What is the result of 5 // 2 in Python?",
        "options": ["A. 2.5", "B. 3", "C. 2", "D. 1"],
        "answer": "C", "correct_text": "2", "category": "Computers"
    },
    {
        "question": "Which symbol starts a single-line comment in Python?",
        "options": ["A. //", "B. #", "C. /*", "D. &"],
        "answer": "B", "correct_text": "#", "category": "Computers"
    },
    {
        "question": "Which function displays output in Python?",
        "options": ["A. input()", "B. show()", "C. print()", "D. display()"],
        "answer": "C", "correct_text": "print()", "category": "Computers"
    },
    {
        "question": "Which Python data structure stores key-value pairs?",
        "options": ["A. List", "B. Tuple", "C. Set", "D. Dictionary"],
        "answer": "D", "correct_text": "Dictionary", "category": "Computers"
    },
    {
        "question": "Which loop is commonly used to iterate over a list?",
        "options": ["A. for", "B. switch", "C. case", "D. repeat"],
        "answer": "A", "correct_text": "for", "category": "Computers"
    },
    {
        "question": "What is the result of len('Python')?",
        "options": ["A. 5", "B. 6", "C. 7", "D. 8"],
        "answer": "B", "correct_text": "6", "category": "Computers"
    },
    {
        "question": "Which operator checks equality in Python?",
        "options": ["A. =", "B. !=", "C. ==", "D. >="],
        "answer": "C", "correct_text": "==", "category": "Computers"
    },
    {
        "question": "Which method adds an item to the end of a Python list?",
        "options": ["A. add()", "B. insert_end()", "C. push()", "D. append()"],
        "answer": "D", "correct_text": "append()", "category": "Computers"
    },
]


def fetch_questions(amount, category_name):
    """Get multiple-choice questions from Open Trivia Database."""
    params = [f"amount={amount}", "type=multiple"]
    category_id = CATEGORIES.get(category_name)
    if category_id is not None:
        params.append(f"category={category_id}")

    url = "https://opentdb.com/api.php?" + "&".join(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "StudentQuizApp/1.0"}
    )

    with urllib.request.urlopen(request, timeout=12) as response:
        data = json.loads(response.read().decode("utf-8"))

    if data.get("response_code") != 0 or not data.get("results"):
        raise ValueError("No questions were returned for this selection.")

    questions = []
    for item in data["results"]:
        correct = html.unescape(item["correct_answer"])
        options = [html.unescape(x) for x in item["incorrect_answers"]]
        options.append(correct)
        random.shuffle(options)

        questions.append({
            "question": html.unescape(item["question"]),
            "options": [
                f"{letter}. {option}"
                for letter, option in zip(LETTERS, options)
            ],
            "answer": LETTERS[options.index(correct)],
            "correct_text": correct,
            "category": html.unescape(item.get("category", category_name)),
        })

    return questions


def initialize_state():
    defaults = {
        "page": "home",
        "questions": [],
        "current_index": 0,
        "score": 0,
        "answered": False,
        "selected_answer": None,
        "online_mode": True,
        "last_error": None,
        "quiz_category": "Any Category",
        "quiz_amount": 10,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_quiz():
    amount = int(st.session_state.amount_choice)
    category = st.session_state.category_choice

    try:
        with st.spinner("Finding questions and preparing your quiz..."):
            questions = fetch_questions(amount, category)
        st.session_state.online_mode = True
        st.session_state.last_error = None
    except Exception as exc:
        # Preserve the original app's built-in offline fallback.
        questions = [dict(q) for q in BACKUP_QUESTIONS]
        random.shuffle(questions)
        questions = questions[:min(amount, len(questions))]
        st.session_state.online_mode = False
        st.session_state.last_error = str(exc)

    st.session_state.questions = questions
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.selected_answer = None
    st.session_state.quiz_category = category
    st.session_state.quiz_amount = amount
    st.session_state.page = "quiz"


def submit_answer():
    if st.session_state.selected_answer is None:
        return

    question = st.session_state.questions[st.session_state.current_index]
    if st.session_state.selected_answer == question["answer"]:
        st.session_state.score += 1

    st.session_state.answered = True


def next_question():
    if st.session_state.current_index + 1 < len(st.session_state.questions):
        st.session_state.current_index += 1
        st.session_state.answered = False
        st.session_state.selected_answer = None
    else:
        st.session_state.page = "results"


def show_home():
    st.session_state.page = "home"
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.selected_answer = None


initialize_state()

# Dark theme styling, matching the original QuizLab palette.
st.markdown(
    """
    <style>
    .stApp { background: #0b1020; color: #f4f7ff; }
    [data-testid="stHeader"] { background: rgba(11,16,32,0); }
    [data-testid="stSidebar"] { background: #141c31; }
    .block-container { max-width: 900px; padding-top: 2rem; }
    h1, h2, h3, p, label { color: #f4f7ff; }
    .quiz-brand { font-size: 1.35rem; font-weight: 800; letter-spacing: 1px; }
    .quiz-subtitle { color: #a6b2cc; margin-top: -8px; }
    .quiz-panel {
        background: #141c31; border: 1px solid #2b3855;
        border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
    }
    .muted { color: #a6b2cc; }
    .category-pill {
        display: inline-block; background: #1b2740; color: #cfc5ff;
        padding: 6px 12px; border-radius: 7px; font-size: 0.8rem;
        font-weight: 700; margin-bottom: 12px;
    }
    div.stButton > button {
        border-radius: 9px; min-height: 2.8rem; font-weight: 700;
    }
    div[data-testid="stRadio"] label {
        background: #1b2740; border: 1px solid #2b3855;
        border-radius: 9px; padding: 10px 14px; margin-bottom: 8px;
    }
    [data-testid="stProgressBar"] > div > div {
        background-color: #7c5cff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="quiz-brand">✦ QUIZLAB</div>', unsafe_allow_html=True)

if st.session_state.page == "home":
    st.markdown(
        '<div class="quiz-subtitle">A fresh set of questions every round</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="quiz-panel">
            <h1>Challenge your mind.</h1>
            <p class="muted">Learn something new with every attempt.</p>
            <p>↻ &nbsp; Fresh questions &nbsp;&nbsp; ✓ &nbsp; Instant feedback
            &nbsp;&nbsp; ★ &nbsp; Track your score</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "CATEGORY",
            list(CATEGORIES.keys()),
            key="category_choice",
            index=0,
        )
    with col2:
        st.selectbox(
            "NUMBER OF QUESTIONS",
            [5, 10, 15, 20, 25],
            key="amount_choice",
            index=1,
        )

    st.success("🌐 Questions are fetched from the internet")
    st.caption("Requires internet for online questions.")
    if st.button("Start quiz  →", type="primary", use_container_width=True):
        start_quiz()
        st.rerun()

elif st.session_state.page == "quiz":
    questions = st.session_state.questions
    total = len(questions)
    index = st.session_state.current_index
    question = questions[index]

    st.markdown(
        f'<div class="quiz-subtitle">{html.escape(question.get("category", "Quiz in progress"))}</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.online_mode:
        st.warning(
            "The online database could not be reached, so the app is using "
            "its built-in Python questions."
        )

    st.write(f"**QUESTION {index + 1:02d} / {total:02d}**")
    st.progress(index / total if total else 0)
    left, right = st.columns(2)
    with left:
        st.caption(f"Category: {question.get('category', 'General')}")
    with right:
        st.caption(f"Score: {st.session_state.score}")

    st.markdown('<div class="quiz-panel">', unsafe_allow_html=True)
    st.subheader(question["question"])

    option_labels = []
    option_map = {}
    for option in question["options"]:
        letter = option[:1]
        option_text = option[3:] if len(option) > 3 else option
        label = f"{letter}   {option_text}"
        option_labels.append(label)
        option_map[label] = letter

    if not st.session_state.answered:
        selected_label = st.radio(
            "Select your answer:",
            option_labels,
            index=None,
            key=f"answer_{index}",
            label_visibility="collapsed",
        )
        st.session_state.selected_answer = (
            option_map[selected_label] if selected_label else None
        )

        if st.button("Check answer  →", type="primary"):
            if st.session_state.selected_answer is None:
                st.warning("Please select A, B, C, or D first.")
            else:
                submit_answer()
                st.rerun()
    else:
        correct = question["answer"]
        selected = st.session_state.selected_answer
        if selected == correct:
            st.success("✓ Correct! Great work.")
        else:
            correct_text = question.get("correct_text", "")
            if not correct_text:
                correct_text = question["options"][LETTERS.index(correct)][3:]
            st.error(f"✕ Not quite. Correct answer: {correct}. {correct_text}")

        for option in question["options"]:
            letter = option[:1]
            option_text = option[3:] if len(option) > 3 else option
            if letter == correct:
                st.markdown(f"**✓ {letter}. {option_text}**")
            elif letter == selected:
                st.markdown(f"✕ {letter}. {option_text}")
            else:
                st.write(f"{letter}. {option_text}")

        button_text = (
            "See results  →"
            if index == total - 1
            else "Next question  →"
        )
        if st.button(button_text, type="primary"):
            next_question()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "results":
    total = len(st.session_state.questions)
    score = st.session_state.score
    percentage = (score / total * 100) if total else 0

    if percentage >= 80:
        emoji, headline, note = "🏆", "Excellent work!", "You really know your stuff."
    elif percentage >= 60:
        emoji, headline, note = "🎉", "Good job!", "You're making solid progress."
    elif percentage >= 40:
        emoji, headline, note = "💪", "Keep practising!", "A little practice goes a long way."
    else:
        emoji, headline, note = "📘", "Keep learning!", "Review the answers and give it another try."

    st.markdown(
        f"""
        <div class="quiz-panel" style="text-align:center">
            <div style="font-size:3rem">{emoji}</div>
            <h1>{headline}</h1>
            <p class="muted">{note}</p>
            <div style="font-size:3rem;font-weight:800;color:#25c998">
                {percentage:.0f}%
            </div>
            <p>{score} correct out of {total} questions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", score)
    col2.metric("Incorrect", total - score)
    col3.metric("Total", total)

    if st.button("↻  Play again", type="primary", use_container_width=True):
        show_home()
        st.rerun()
