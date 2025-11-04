# app.py
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from storage.lingo_storage import LingoStorage
from chains.lingo_chain import LingoChain
import uuid
import datetime
import re
import os
import pandas as pd

# TTS için
from gtts import gTTS
import io

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# init storage & LLM chain
storage = LingoStorage(DATA_DIR)
lingo = LingoChain()

st.set_page_config(page_title="LingoMind • Kişisel İngilizce Asistanı", layout="wide")
st.title("🧠 LingoMind — Personal English Vocabulary Coach")
st.caption("Kişisel seviyene ve ilgi alanına göre günlük kelimeler, mini practice ve haftalık raporlar.")

# ---------- Safe rerun helper ----------
def safe_rerun():
    try:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
            return
        if hasattr(st, "rerun"):
            st.rerun()
            return
    except Exception:
        pass
    try:
        params = st.experimental_get_query_params()
        params["_trigger"] = str(uuid.uuid4())
        st.experimental_set_query_params(**params)
    except Exception:
        pass
    st.stop()

# ---------- helpers ----------
def _truncate_metadata(text: str) -> str:
    if not text:
        return ""
    s = str(text)
    markers = [
        "additional_kwargs=", "response_metadata=", "usage_metadata=",
        "token_usage", "completion_tokens", "model_name", "system_fingerprint",
        "finish_reason", "logprobs", "id='run-", "id=\"run-"
    ]
    low = s.lower()
    idxs = [low.find(m) for m in markers if low.find(m) != -1]
    if idxs:
        cut = min(idxs)
        s = s[:cut].rstrip()
    s = s.rstrip(" \n\t'\"\\")
    s = s.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
    return s.strip()

def _unwrap_content(item) -> str:
    if item is None:
        return ""
    if hasattr(item, "content"):
        return _truncate_metadata(str(item.content))
    return _truncate_metadata(str(item))

def _clean_inline(text: str) -> str:
    if not text:
        return ""
    t = str(text).strip()
    t = re.sub(r'^\s*content\s*=\s*[\'"]?', '', t, flags=re.I).strip()
    t = re.sub(r'^(example sentence[:\s]*)', '', t, flags=re.I).strip()
    t = re.sub(r'^(example[:\s]*)', '', t, flags=re.I).strip()
    t = re.sub(r'^(tip[:\s]*)', '', t, flags=re.I).strip()
    t = re.sub(r'^(pronunciation[:\s]*)', '', t, flags=re.I).strip()
    t = t.rstrip("\\'\"\n\r ")
    return t

# ---------- Sidebar: profile & settings ----------
with st.sidebar:
    st.header("Profil & Ayarlar")
    if "user_id" not in st.session_state:
        username = st.text_input("İsim (takma ad) — kaydetmek için giriş yap", "")
        level = st.selectbox("Seviye (CEFR)", ["A1","A2","B1","B2","C1"])
        interest = st.text_input("İlgi alanı (ör. travel, tech, art)", "general")
        email = st.text_input("E-posta (isteğe bağlı, günlük gönderim için)")
        if st.button("Başlat / Kaydet"):
            if not username:
                st.warning("Lütfen bir isim gir.")
            else:
                user_id = str(uuid.uuid4())
                user = {
                    "id": user_id,
                    "name": username,
                    "level": level,
                    "interest": interest,
                    "email": email,
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
                storage.upsert_user(user)
                st.session_state.user_id = user_id
                st.success("Profil kaydedildi! Sol üstten işlemlere dön.")
                safe_rerun()
    else:
        uid = st.session_state.user_id
        user = storage.get_user(uid)
        st.markdown(f"**Hoş geldin, {user.get('name')}**")
        st.markdown(f"- Seviye: {user.get('level')}")
        st.markdown(f"- İlgi: {user.get('interest')}")
        if st.button("Profil düzenle"):
            del st.session_state["user_id"]
            try:
                st.rerun()
            except Exception:
                pass
        st.markdown("---")
        if st.button("Günün kelimelerini al (1–3)"):
            st.session_state["fetch_words"] = True
            try:
                st.rerun()
            except Exception:
                pass

# ---------- main guard ----------
if "user_id" not in st.session_state:
    st.info("Önce profil oluşturun (sol panel).")
    st.stop()

user = storage.get_user(st.session_state.user_id)
if not user:
    st.error("Kullanıcı bulunamadı; lütfen profili yeniden oluşturun.")
    st.stop()

# Ensure session keys
if "quiz_results" not in st.session_state:
    st.session_state["quiz_results"] = []
if "show_quiz_report" not in st.session_state:
    st.session_state["show_quiz_report"] = False

col1, col2 = st.columns([2,1])

# Left column: tabs
with col1:
    tabs = st.tabs(["📝 Uygulama (Nudge Learning / Düzeltme)", "🗣 Mini Speaking Mode", "🧩 Quiz"])
    # ---------------- PRACTICE ----------------
    with tabs[0]:
        st.header("📝 Uygulama (Nudge Learning / Düzeltme)")
        if st.session_state.get("fetch_words"):
            n = st.slider("Kaç kelime istersin?", 1, 3, 1)
            try:
                raw = lingo.suggest_words(level=user["level"], interest=user["interest"], n=n)
            except Exception:
                raw = None
            suggestions = []
            if isinstance(raw, list):
                for it in raw:
                    if isinstance(it, dict):
                        suggestions.append({"word": it.get("word",""), "meaning": it.get("meaning",""), "example": it.get("example","")})
                    else:
                        suggestions.append({"word": _clean_inline(str(it)), "meaning": "", "example": ""})
            else:
                txt = _unwrap_content(raw)
                lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
                for ln in lines[:n]:
                    suggestions.append({"word": re.sub(r'^\d+[\.\)]\s*', '', ln), "meaning":"", "example":""})
            if not suggestions:
                st.info("Şu anda kelime önerisi alınamadı. Lütfen tekrar deneyin.")
            else:
                st.success(f"{len(suggestions)} kelime önerildi.")
                for s in suggestions:
                    w = s.get("word") or ""
                    meaning = s.get("meaning") or ""
                    example = s.get("example") or ""
                    st.subheader(f"🔹 {w}")
                    if meaning:
                        st.write(f"**Anlam (kısa):** { _clean_inline(meaning) }")
                    if example:
                        st.write(f"**Örnek:** { _clean_inline(example) }")
                    col_a, col_b = st.columns([3,1])
                    with col_a:
                        if st.button(f"Öğren: {w}", key=f"teach_{w}"):
                            try:
                                out = lingo.teach_word(word=w, level=user["level"])
                                st.markdown(_clean_inline(_unwrap_content(out)))
                            except Exception:
                                st.info("Öğretim içeriği alınamadı.")
                            storage.append_word_entry({
                                "user_id": user["id"],
                                "word": w,
                                "meaning": meaning,
                                "example": example,
                                "timestamp": datetime.datetime.utcnow().isoformat(),
                                "result": "presented",
                                "failures": 0
                            })
                    with col_b:
                        st.write("")
            st.session_state["fetch_words"] = False
            safe_rerun()

        st.markdown("---")
        practice_word = st.text_input("Pratik yapmak istediğin kelimeyi yaz (örn: resilience):", key="practice_word")
        user_sentence = st.text_input("Kelimeyi içeren cümleni yaz:", key="user_sentence")

        if practice_word:
            try:
                teach_text = lingo.teach_word(word=practice_word, level=user["level"])
                short = _truncate_metadata(teach_text).splitlines()
                if short:
                    st.markdown(f"**Kelime hakkında (kısa):** {_clean_inline(short[0])}")
            except Exception:
                pass
            try:
                trans_prompt = f'Provide a one-word Turkish translation for the English word \"{practice_word}\". Return only the translation.'
                tur = lingo.llm_call(trans_prompt)
                tur = _clean_inline(_unwrap_content(tur))
                if tur:
                    st.markdown(f"**Türkçe karşılığı:** `{tur}`")
            except Exception:
                pass
            
            
            

        if st.button("Kontrol et & düzelt"):
            if not practice_word or not user_sentence:
                st.warning("Kelime ve örnek cümle girin.")
            else:
                corr = lingo.correct_answer(expected=practice_word, user_input=user_sentence)
                raw = _unwrap_content(corr)
                cleaned = _truncate_metadata(raw).strip()
                lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
                corrected = None
                explanation = None
                # quick parsing (same logic as before but minimal)
                m = re.search(r'["“”\']([^"“”\']+?)["“”\']', cleaned)
                if m:
                    corrected = m.group(1).strip()
                if not corrected:
                    m2 = re.search(r'Correct(?:ed)?(?:\sversion)?(?:\sis|:)\s*(.+)', cleaned, re.I)
                    if m2:
                        corrected = m2.group(1).splitlines()[0].strip()
                if len(lines) >= 2:
                    explanation = lines[1]
                # translate explanation short
                expl_tr = ""
                if explanation:
                    expl_tr = lingo.llm_call("Translate this short sentence into Turkish (one short phrase):\n\n" + explanation)
                    expl_tr = _clean_inline(_unwrap_content(expl_tr))
                if corrected:
                    st.markdown(f"**✅ Düzeltme:** `{corrected}`")
                if explanation:
                    st.markdown(f"**💡 Açıklama (TR):** {expl_tr or explanation}")
                # store
                res = "ok" if ("no change needed" in cleaned.lower() or "correct as" in cleaned.lower()) else "failed"
                storage.append_word_entry({
                    "user_id": user["id"],
                    "word": practice_word,
                    "meaning": "",
                    "example": user_sentence,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "result": res,
                    "failures": 0 if res=="ok" else 1
                })

    # ---------------- SPEAKING ----------------
    with tabs[1]:
        st.header("🗣 Mini Speaking Mode")
        speaking_word = st.text_input("Konuşma için kelime (mini):", key="speaking_word")
        play_audio = st.checkbox("Örnek cümleyi sesli dinle", value=True, help="Örnek cümleyi otomatik olarak sesli çalmak için işaretli bırak.")
        if st.button("Başlat speaking"):
            if not speaking_word:
                st.warning("Kelime gir.")
            else:
                # LLM'den speaking içeriğini al
                sp = lingo.mini_speaking(word=speaking_word, level=user["level"])
                sp_text = _unwrap_content(sp)
                sp_text = _truncate_metadata(sp_text)
                # satırlara ayır
                lines = [ln.strip() for ln in sp_text.splitlines() if ln.strip()]
                # tahmini: lines[0]=örnek, lines[1]=ipucu, lines[2]=telaffuz
                example = lines[0] if len(lines) >= 1 else ""
                tip = lines[1] if len(lines) >= 2 else ""
                pron = lines[2] if len(lines) >= 3 else ""

                # temizle
                example = _clean_inline(example)
                tip = _clean_inline(tip)
                pron = _clean_inline(pron)

                # Ekrana yerleştir 
                if example:
                    st.markdown(f"**Örnek cümle:** {example}")
                if tip:
                    st.markdown(f"**Konuşma ipucu:** {tip}")
                if pron:
                    st.markdown(f"**Telaffuz:** `{pron}`")

                # Sesli oynatma (gTTS -> in-memory mp3 -> st.audio)
                if play_audio and example:
                    try:
                        tts = gTTS(text=example, lang="en")
                        mp3_fp = io.BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)
                        st.audio(mp3_fp.read(), format="audio/mp3")
                    except Exception as e:
                        # Hata olursa sessizce devam et; debug istersen alt satırı aç
                        # st.error(f"TTS oynatma hatası: {e}")
                        pass

                # küçük bilgi notu
                st.info("Kısa cevap yazıp tekrar kontrol ettirebilirsin.")

    # ---------------- QUIZ ----------------
    with tabs[2]:
        st.header("🧩 Quiz — Hızlı test (MCQ + Fill-in)")
        st.markdown("Kısa quiz: kelimeleri hatırlama / anlamaya dayalı sorular. Başarı oranınız Raporlar bölümünde kaydedilir.")

        source = st.radio("Kelime kaynağı:", ("Günün kelimeleri (LLM önerisi)", "Geçmiş kelimelerim (kayıttan)"), index=0)
        qn = st.slider("Kaç soru istersin?", 3, 10, 5)

        if st.button("Quiz oluştur"):
            # reset any previous quiz results shown
            st.session_state["show_quiz_report"] = False
            st.session_state["quiz_results"] = []
            words_list = []
            if source.startswith("Günün"):
                try:
                    raw = lingo.suggest_words(level=user["level"], interest=user["interest"], n=qn)
                except Exception:
                    raw = []
                if isinstance(raw, list):
                    words_list = raw
                else:
                    txt = _unwrap_content(raw)
                    lines = [ln for ln in txt.splitlines() if ln.strip()]
                    for ln in lines[:qn]:
                        words_list.append({"word": re.sub(r'^\d+[\.\)]\s*', '', ln)})
            else:
                entries = []
                if hasattr(storage, "get_user_word_entries"):
                    try:
                        entries = storage.get_user_word_entries(user["id"])
                    except Exception:
                        entries = []
                seen = {}
                for e in entries:
                    w = e.get("word")
                    if w and w not in seen:
                        seen[w] = True
                        words_list.append({"word": w, "meaning": e.get("meaning","")})
                        if len(words_list) >= qn:
                            break

            if not words_list:
                st.info("Kelime listesi oluşturulamadı. Önce birkaç kelime ekleyin veya tekrar deneyin.")
            else:
                quiz = lingo.generate_quiz(words=words_list, n_questions=qn)
                if not quiz:
                    st.info("Quiz oluşturulamadı. Lütfen tekrar deneyin.")
                else:
                    st.session_state.quiz = quiz
                    st.session_state.quiz_idx = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_total = len(quiz)
                    st.session_state.quiz_answered = False
                    # reset results list for this new quiz
                    st.session_state.quiz_results = []
                    safe_rerun()

        # show quiz only if exists and valid
        if st.session_state.get("quiz"):
            quiz = st.session_state.get("quiz", [])
            idx = int(st.session_state.get("quiz_idx", 0))
            total = len(quiz)

            # Guard: if idx out of bounds, finalize quiz gracefully
            if idx >= total:
                score = st.session_state.get("quiz_score", 0)
                st.success(f"Quiz tamamlandı — Skor: {score}/{total}")
                # store summary in storage
                try:
                    storage.append_word_entry({
                        "user_id": user["id"],
                        "word": "__quiz_summary__",
                        "meaning": "",
                        "example": "",
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "result": f"{score}/{total}",
                        "failures": 0,
                        "type": "quiz"
                    })
                except Exception:
                    pass

                # set show_quiz_report True so right column will display the report
                if st.session_state.get("quiz_results"):
                    st.session_state["show_quiz_report"] = True
                else:
                    # even if no session results (fallback) still try to show storage summary
                    st.session_state["show_quiz_report"] = True

                # cleanup only active quiz keys but KEEP quiz_results and show_quiz_report
                for k in ["quiz", "quiz_idx", "quiz_score", "quiz_total", "quiz_answered"]:
                    if k in st.session_state:
                        del st.session_state[k]

                # rerun so right column immediately shows the report
                safe_rerun()

            else:
                q = quiz[idx]
                st.markdown(f"**Soru {idx+1}/{total}**")
                st.markdown(q.get("question") or "")

                # show options or fill-in
                if not st.session_state.get("quiz_answered", False):
                    if q.get("type") == "mcq":
                        opts = q.get("options", [])
                        cols = st.columns(2)
                        for i, opt in enumerate(opts):
                            col = cols[i % 2]
                            if col.button(opt, key=f"q_{idx}_{i}"):
                                correct_idx = int(q.get("answer") or 0)
                                user_ans = opt
                                correct_ans = opts[correct_idx] if opts else ""
                                correct_bool = (i == correct_idx)
                                if correct_bool:
                                    st.success("✅ Doğru!")
                                    st.session_state.quiz_score = st.session_state.get("quiz_score", 0) + 1
                                    result_flag = "quiz_ok"
                                else:
                                    st.error(f"❌ Yanlış. Doğru: `{correct_ans}`")
                                    result_flag = "quiz_fail"

                                # persist to storage
                                try:
                                    storage.append_word_entry({
                                        "user_id": user["id"],
                                        "word": q.get("word",""),
                                        "meaning": q.get("meaning",""),
                                        "example": "",
                                        "timestamp": datetime.datetime.utcnow().isoformat(),
                                        "result": result_flag,
                                        "failures": 0 if result_flag=="quiz_ok" else 1,
                                        "type": "quiz",
                                        "question": q.get("question")
                                    })
                                except Exception:
                                    pass

                                # add to session results for immediate reporting
                                st.session_state.quiz_results.append({
                                    "index": idx,
                                    "question": q.get("question"),
                                    "word": q.get("word",""),
                                    "user_answer": user_ans,
                                    "correct_answer": correct_ans,
                                    "is_correct": correct_bool,
                                    "explanation": q.get("explanation",""),
                                    "meaning": q.get("meaning","")
                                })
                                st.session_state.quiz_answered = True
                    else:
                        resp = st.text_input("Cevabınız:", key=f"fill_{idx}")
                        if st.button("Gönder", key=f"send_{idx}"):
                            ans = (q.get("answer") or "").strip()
                            user_ans = (resp or "").strip()
                            correct_bool = (user_ans.lower() == ans.lower())
                            if correct_bool:
                                st.success("✅ Doğru!")
                                st.session_state.quiz_score = st.session_state.get("quiz_score", 0) + 1
                                result_flag = "quiz_ok"
                            else:
                                st.error(f"❌ Yanlış. Doğru: `{ans}`")
                                result_flag = "quiz_fail"

                            try:
                                storage.append_word_entry({
                                    "user_id": user["id"],
                                    "word": q.get("word",""),
                                    "meaning": q.get("meaning",""),
                                    "example": "",
                                    "timestamp": datetime.datetime.utcnow().isoformat(),
                                    "result": result_flag,
                                    "failures": 0 if result_flag=="quiz_ok" else 1,
                                    "type": "quiz",
                                    "question": q.get("question")
                                })
                            except Exception:
                                pass

                            st.session_state.quiz_results.append({
                                "index": idx,
                                "question": q.get("question"),
                                "word": q.get("word",""),
                                "user_answer": user_ans,
                                "correct_answer": ans,
                                "is_correct": correct_bool,
                                "explanation": q.get("explanation",""),
                                "meaning": q.get("meaning","")
                            })
                            st.session_state.quiz_answered = True

                # After answered: show explanation + Next button
                if st.session_state.get("quiz_answered", False):
                    expl = q.get("explanation") or ""
                    if expl:
                        st.markdown(f"**Açıklama:** {expl}")
                    st.markdown("---")
                    if st.button("Sonraki soru", key=f"next_{idx}"):
                        st.session_state.quiz_idx = st.session_state.get("quiz_idx", 0) + 1
                        st.session_state.quiz_answered = False
                        safe_rerun()

# Right column: reports & export
with col2:
    st.header("📈 Raporlar & Dışa Aktarım")

    # Weekly summary (existing)
    try:
        summary = storage.weekly_summary(user["id"])
    except Exception:
        summary = {"count": 0, "hardest": None}
    st.markdown(f"**Bu hafta öğrenilen kelime sayısı:** {summary.get('count')}")
    st.markdown(f"**En çok zorlanılan kelime:** {summary.get('hardest') or '—'}")

    st.markdown("---")
    st.subheader("Quiz Raporu")

    # If user requested to see the report now (session), show detailed report
    if st.session_state.get("show_quiz_report", False):
        # Prefer session results if available
        if st.session_state.get("quiz_results"):
            st.markdown("**Anlık Quiz Detayları (Bu oturum)**")
            df_rows = []
            for r in st.session_state["quiz_results"]:
                df_rows.append({
                    "Soru #": r["index"] + 1,
                    "Kelime": r["word"],
                    "Cevabın": r["user_answer"],
                    "Doğru Cevap": r["correct_answer"],
                    "Doğru mu?": "Evet" if r["is_correct"] else "Hayır",
                    "Anlam": r.get("meaning",""),
                    "Açıklama": r.get("explanation","")
                })
            df = pd.DataFrame(df_rows)
            st.table(df)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("Raporu CSV indir", csv_bytes, file_name=f"lingomind_quiz_report_{user['id']}.csv")
            if st.button("Raporu kapat"):
                st.session_state["show_quiz_report"] = False
                safe_rerun()
        else:
            # session report requested but no session details — fallback to storage
            try:
                entries = storage.get_user_word_entries(user["id"]) if hasattr(storage, "get_user_word_entries") else []
            except Exception:
                entries = []
            quiz_rows = [e for e in entries if e.get("type") == "quiz" or e.get("word") == "__quiz_summary__"]
            if quiz_rows:
                ok = sum(1 for e in quiz_rows if e.get("result") == "quiz_ok")
                fail = sum(1 for e in quiz_rows if e.get("result") == "quiz_fail")
                total = ok + fail
                if total > 0:
                    rate = int(ok / total * 100)
                    st.markdown(f"**Quiz başarı oranı (tüm kayıtlar):** {rate}% ({ok}/{total})")
                summaries = [e for e in quiz_rows if e.get("word") == "__quiz_summary__"]
                if summaries:
                    st.markdown("**Son quiz sonuçları (özet):**")
                    recent = sorted(summaries, key=lambda x: x.get("timestamp",""), reverse=True)[:10]
                    rows = []
                    for s in recent:
                        rows.append({
                            "Tarih": s.get("timestamp","")[:19],
                            "Sonuç": s.get("result","")
                        })
                    df2 = pd.DataFrame(rows)
                    st.table(df2)
            else:
                st.info("Henüz quiz verisi yok. Quiz yaptıktan sonra burası dolacaktır.")
    else:
        # Not explicitly showing session report — allow manual show if session results present
        if st.session_state.get("quiz_results"):
            if st.button("Son Quiz Raporunu Göster"):
                st.session_state["show_quiz_report"] = True
                safe_rerun()
        else:
            # fallback: show aggregated history from storage if available
            try:
                entries = storage.get_user_word_entries(user["id"]) if hasattr(storage, "get_user_word_entries") else []
            except Exception:
                entries = []
            quiz_rows = [e for e in entries if e.get("type") == "quiz" or e.get("word") == "__quiz_summary__"]
            if quiz_rows:
                ok = sum(1 for e in quiz_rows if e.get("result") == "quiz_ok")
                fail = sum(1 for e in quiz_rows if e.get("result") == "quiz_fail")
                total = ok + fail
                if total > 0:
                    rate = int(ok / total * 100)
                    st.markdown(f"**Quiz başarı oranı (tüm kayıtlar):** {rate}% ({ok}/{total})")
                summaries = [e for e in quiz_rows if e.get("word") == "__quiz_summary__"]
                if summaries:
                    st.markdown("**Son quiz sonuçları (özet):**")
                    recent = sorted(summaries, key=lambda x: x.get("timestamp",""), reverse=True)[:10]
                    rows = []
                    for s in recent:
                        rows.append({
                            "Tarih": s.get("timestamp","")[:19],
                            "Sonuç": s.get("result","")
                        })
                    df2 = pd.DataFrame(rows)
                    st.table(df2)
            else:
                st.info("Henüz quiz verisi yok. Quiz yaptıktan sonra burası dolacaktır.")

    st.markdown("---")
    if st.button("CSV olarak indir (öğrenilenler)"):
        out = storage.export_user_words_csv(user["id"], DATA_DIR / f"{user['id']}_words.csv")
        if out:
            with open(out, "rb") as f:
                st.download_button("İndir CSV", f, file_name=out.name)
        else:
            st.info("Henüz kayıt yok.")

    if st.button("Günlüğü temizle (kullanıcı için)"):
        storage.clear_user_words(user["id"])
        st.success("Kullanıcının kelime günlükleri temizlendi.")

    st.markdown("---")
    st.markdown("📬 Bildirimler (isteğe bağlı)")
    st.markdown("E-posta bildirimleri için SMTP bilgilerini `.env` içine ekleyin. (Bu demo, e-posta göndermeyi sağlamaz.)")

st.markdown("---")
st.caption("LingoMind — Local demo. Not a replacement for formal language teaching.")
