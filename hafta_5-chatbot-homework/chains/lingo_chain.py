# chains/lingo_chain.py
from langchain_openai import ChatOpenAI
import json
import re
from typing import List, Dict, Any

class LingoChain:
    """
    Basit LingoChain wrapper.
    Varsayılan olarak ChatOpenAI (langchain_openai) kullanır.
    Sahip olması gereken basit metodlar:
    - suggest_words(level, interest, n)
    - teach_word(word, level)
    - correct_answer(expected, user_input)
    - mini_speaking(word, level)
    - generate_quiz(words, n_questions)
    - llm(prompt)  # raw prompt call
    """

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=model, temperature=temperature)

    def _call_llm(self, prompt: str, max_tokens: int = 300) -> str:
        """
        Call the LLM safely and return text.
        Attempts different call styles depending on installed langchain version.
        """
        try:
            # LangChain ChatOpenAI usually supports __call__ returning text
            out = self.llm(prompt)
            # If object-like, try to get .content
            if hasattr(out, "content"):
                return str(out.content)
            return str(out)
        except Exception:
            try:
                # Some versions expose generate or create; try generate -> returns object with generations
                resp = self.llm.generate([prompt])
                # Try to extract text
                try:
                    gen = resp.generations[0][0].text
                    return gen
                except Exception:
                    return str(resp)
            except Exception:
                # ultimate fallback
                return str(prompt)

    # --- existing helper methods (simple) ---
    def suggest_words(self, level: str = "B1", interest: str = "general", n: int = 1) -> List[Dict[str, Any]]:
        """
        Ask LLM for n words for given level/interest. Returns normalized list of dicts:
        [{word, meaning, example}, ...]
        """
        prompt = (
            f"Suggest {n} English vocabulary words for a learner level {level} "
            f"interested in {interest}. For each word return short fields: Word, Meaning (Turkish short), Example sentence. "
            "Return as a short numbered list or JSON. Be concise."
        )
        raw = self._call_llm(prompt)
        # Try to find JSON first
        json_obj = None
        try:
            # extract {...} or [...]
            m = re.search(r'(\[.*\]|\{.*\})', raw, re.S)
            if m:
                jtxt = m.group(1)
                json_obj = json.loads(jtxt)
                if isinstance(json_obj, dict):
                    # convert to list
                    json_obj = [json_obj]
            else:
                # try to parse line blocks into list
                parsed = []
                blocks = [b.strip() for b in re.split(r'\n\s*\n', raw) if b.strip()]
                for blk in blocks:
                    # each block may contain "Word: X" lines
                    word = re.search(r'(?:Word|word|Kelime|term)[:\s-]+(.+)', blk)
                    meaning = re.search(r'(?:Meaning|meaning|Anlam|Türkçe)[:\s-]+(.+)', blk)
                    example = re.search(r'(?:Example|example|Örnek)[:\s-]+(.+)', blk)
                    parsed.append({
                        "word": (word.group(1).strip() if word else blk.splitlines()[0].strip()),
                        "meaning": (meaning.group(1).strip() if meaning else ""),
                        "example": (example.group(1).strip() if example else "")
                    })
                json_obj = parsed
        except Exception:
            # fallback: produce very small structured output
            items = []
            lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            for ln in lines[:n]:
                items.append({"word": ln, "meaning": "", "example": ""})
            json_obj = items
        return json_obj or []

    def teach_word(self, word: str, level: str = "B1") -> str:
        prompt = (
            f"Give a short teaching snippet for the word '{word}' for level {level}.\n"
            "One-line definition, one short example sentence, one quick tip to remember."
        )
        return self._call_llm(prompt)

    def correct_answer(self, expected: str, user_input: str) -> str:
        prompt = (
            f"You are a concise English tutor. The target word is '{expected}'. "
            f"User sentence: \"{user_input}\". If there is a mistake, return a corrected full sentence "
            "and a short explanation. If it's correct, say 'No change needed' or 'Correct as is'. Keep short."
        )
        return self._call_llm(prompt)

    def mini_speaking(self, word: str, level: str = "B1") -> str:
        prompt = (
            f"Provide a one-sentence speaking prompt using the word '{word}' for level {level}, "
            "a one-line pronounciation / IPA, and a one-line tip. Return 3 short lines labeled Example, Pronunciation, Tip."
        )
        return self._call_llm(prompt)

    def llm_call(self, prompt: str) -> str:
        """Expose generic LLM call"""
        return self._call_llm(prompt)

    # --- NEW: generate_quiz ---
    def generate_quiz(self, words: List[Dict[str, Any]], n_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a quiz from a list of words.
        words: list of dicts: {word, meaning, example}
        Returns: list of question dicts:
        {
            "type": "mcq" or "fill",
            "question": "Which is the correct meaning of 'resilience'?",
            "options": ["A", "B", "C", "D"],  # for mcq
            "answer": 1,  # index of correct option (0-based)
            "word": "resilience",
            "explanation": "short explanation (optional)"
        }
        Strategy:
        - For each word create either 4-choice MCQ (meaning-based) or fill-in (cloze).
        - Ask LLM to return JSON. If JSON parse fails, try fallback heuristics.
        """
        # prepare short words list up to n_questions
        pool = words[:n_questions] if len(words) >= n_questions else words
        if not pool:
            return []

        # Build prompt asking for structured JSON
        examples = []
        for w in pool:
            word = w.get("word") or w.get("term") or w.get("Word") or ""
            meaning = w.get("meaning") or w.get("definition") or ""
            examples.append({"word": word, "meaning": meaning})

        prompt = (
            "Create a short quiz with the following words. For each word return either a multiple-choice question (mcq) "
            "with 4 choices (one correct) or a fill-in (cloze) question. Return valid JSON array only. "
            "Format example for each question:\n"
            "{\n"
            '  "type": "mcq",\n'
            '  "word": "WORD",\n'
            '  "question": "QUESTION TEXT",\n'
            '  "options": ["opt1","opt2","opt3","opt4"],\n'
            '  "answer": 2,    # index 0-based\n'
            '  "explanation": "short explanation"\n'
            "}\n\n"
            "Or for fill:\n"
            '{ "type":"fill", "word":"WORD", "question":"Fill the blank: ...", "answer":"full correct sentence", "explanation":"..." }\n\n'
            "Use the meanings to craft plausible distractors. Return a JSON array of questions.\n\n"
            f"INPUT WORDS: {json.dumps(examples, ensure_ascii=False)}\n"
            "Be concise."
        )

        raw = self._call_llm(prompt, max_tokens=800)
        # Try to extract JSON block
        try:
            m = re.search(r'(\[.*\])', raw, re.S)
            if m:
                jtxt = m.group(1)
            else:
                # maybe LLM used single quotes; normalize
                jtxt = raw.strip()
            # replace trailing commas etc — attempt to parse robustly
            # sanitize smart quotes
            jtxt = jtxt.replace("“", '"').replace("”", '"').replace("’", "'")
            # if single quotes used for keys, try to convert to double quotes
            # naive replace only when it appears like a JSON object
            if "'" in jtxt and '"' not in jtxt:
                jtxt = jtxt.replace("'", '"')
            quiz = json.loads(jtxt)
            # validate each item
            result = []
            for q in quiz:
                if not isinstance(q, dict):
                    continue
                # normalize keys
                qtype = q.get("type", "mcq")
                question = q.get("question") or q.get("q") or ""
                options = q.get("options") or []
                answer = q.get("answer")
                explanation = q.get("explanation") or ""
                word = q.get("word") or ""
                # ensure options is list
                if qtype == "mcq" and (not isinstance(options, list) or len(options) < 2):
                    # skip or convert => try to create options heuristically
                    continue
                result.append({
                    "type": qtype,
                    "word": word,
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                })
            if result:
                return result
        except Exception:
            pass

        # Fallback: simple MCQ generation heuristics (meaning-based)
        fallback = []
        for w in pool:
            word = (w.get("word") or "").strip()
            meaning = (w.get("meaning") or "").strip()
            # build three distractors by modifying the meaning or using placeholders
            distractors = []
            if meaning:
                distractors.append(meaning)
                distractors.append("something similar") 
                distractors.append("opposite meaning")
                distractors.append("another meaning")
                # make options unique and shuffle
                opts = list(dict.fromkeys(distractors))[:4]
                # ensure correct included (put at index 0)
                if meaning in opts:
                    correct_index = opts.index(meaning)
                else:
                    opts[0] = meaning
                    correct_index = 0
            else:
                opts = ["option1", "option2", "option3", "option4"]
                correct_index = 0
            fallback.append({
                "type": "mcq",
                "word": word,
                "question": f"What is the meaning of '{word}'?",
                "options": opts,
                "answer": correct_index,
                "explanation": f"The correct meaning is: {meaning}" if meaning else ""
            })
        return fallback
