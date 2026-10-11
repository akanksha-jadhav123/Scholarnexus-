"""
AI Chatbot — retrieval-based Q&A grounded in verified scholarship data.
No external LLM required. Answers from the project's own database.
"""
import re
from database import db
from services.eligibility_service import EligibilityChecker


class ChatbotService:

    INTENTS = [
        ("greeting", ["hi", "hello", "hey", "namaste"]),
        ("help", ["help", "what can you do", "how to use"]),
        ("eligibility", ["eligible", "eligibility", "qualify", "am i", "can i apply"]),
        ("deadline", ["deadline", "last date", "due", "when is the last"]),
        ("documents", ["document", "certificate", "papers", "requirement"]),
        ("amount", ["amount", "how much", "money", "rupees", "₹", "stipend"]),
        ("count", ["how many", "total scholarships", "list all"]),
        ("category", ["sc", "st", "obc", "minority", "general", "category"]),
        ("income", ["income limit", "family income", "earn"]),
        ("apply", ["how to apply", "apply for", "application process"]),
        ("compare", ["compare", "difference between", "which is better"]),
    ]

    @classmethod
    def answer(cls, question, user_id=None):
        q = (question or "").lower().strip()
        if not q:
            return {"answer": "Please ask a question about scholarships.", "type": "empty"}

        # 1. Detect intent
        intent = cls._detect_intent(q)

        # 2. Route to handler
        handlers = {
            "greeting": cls._handle_greeting,
            "help": cls._handle_help,
            "eligibility": lambda q: cls._handle_eligibility(q, user_id),
            "deadline": cls._handle_deadline,
            "documents": cls._handle_documents,
            "amount": cls._handle_amount,
            "count": cls._handle_count,
            "category": cls._handle_category,
            "income": cls._handle_income,
            "apply": cls._handle_apply,
            "compare": cls._handle_compare,
            "fallback": lambda q: cls._handle_lookup(q, user_id),
        }
        handler = handlers.get(intent, handlers["fallback"])
        result = handler(q)
        result["intent"] = intent
        return result

    @classmethod
    def _detect_intent(cls, q):
        """Use word-boundary matching to avoid 'hi' inside 'this'."""
        import re
        # Check intents in priority order (more specific first)
        priority_order = ["count", "eligibility", "deadline", "documents",
                          "amount", "category", "income", "apply", "compare",
                          "help", "greeting"]
        intent_map = {name: kws for name, kws in cls.INTENTS}

        for intent_name in priority_order:
            keywords = intent_map.get(intent_name, [])
            for kw in keywords:
                # Word-boundary regex: match whole words only
                if re.search(rf"\b{re.escape(kw)}\b", q):
                    return intent_name

        return "fallback"

    # ---------- Handlers ----------

    @classmethod
    def _handle_greeting(cls, q):
        return {
            "answer": "Hello! 👋 I'm the ScholarNexus assistant. I can help you with:\n"
                      "• Eligibility checks\n"
                      "• Deadlines\n"
                      "• Required documents\n"
                      "• Scholarship amounts\n"
                      "Ask me anything!"
        }

    @classmethod
    def _handle_help(cls, q):
        return {
            "answer": "I can answer questions like:\n"
                      "• \"Am I eligible for National Merit Scholarship?\"\n"
                      "• \"What's the deadline for OBC Scholarship?\"\n"
                      "• \"What documents do I need?\"\n"
                      "• \"How much is the Post Matric scholarship?\"\n"
                      "• \"How many scholarships are available?\""
        }

    @classmethod
    def _find_scholarship(cls, q):
        """Find best matching scholarship by name substring."""
        words = [w for w in re.findall(r"[a-z]{4,}", q)]
        if not words:
            return None

        best, best_score = None, 0
        for sc in db.Scholarships.find({"status": "Active"}, {"_id": 0}):
            name = (sc.get("scholarship_name") or "").lower()
            score = sum(1 for w in words if w in name)
            if score > best_score:
                best, best_score = sc, score
        return best if best_score > 0 else None

    @classmethod
    def _handle_eligibility(cls, q, user_id):
        if not user_id:
            return {"answer": "Please log in to check your eligibility.", "type": "auth"}
        profile = db.StudentProfiles.find_one({"user_id": user_id}) or {}
        if not profile:
            return {"answer": "Please complete your profile first.", "type": "profile"}

        sc = cls._find_scholarship(q)
        if not sc:
            return {"answer": "Which scholarship are you asking about? Try mentioning its name.", "type": "clarify"}

        result = EligibilityChecker.check(profile, sc)
        ans = f"**{sc['scholarship_name']}** — Status: **{result['status'].upper()}**\n"
        ans += f"{result['reason']}\n"
        if result["matched"]:
            ans += "\n✅ Matched:\n" + "\n".join(f"  • {m}" for m in result["matched"])
        if result["failed"]:
            ans += "\n❌ Not matched:\n" + "\n".join(f"  • {f}" for f in result["failed"])
        return {"answer": ans, "type": "eligibility", "detail": result}

    @classmethod
    def _handle_deadline(cls, q):
        sc = cls._find_scholarship(q)
        if sc:
            return {"answer": f"The deadline for **{sc['scholarship_name']}** is **{sc.get('application_deadline', 'not specified')}**."}
        items = list(db.Scholarships.find(
            {"status": "Active", "application_deadline": {"$ne": None}},
            {"_id": 0}
        ).sort("application_deadline", 1).limit(5))
        if not items:
            return {"answer": "No upcoming deadlines found."}
        lines = [f"• {s['scholarship_name']}: {s['application_deadline']}" for s in items]
        return {"answer": "Upcoming deadlines:\n" + "\n".join(lines)}

    @classmethod
    def _handle_documents(cls, q):
        sc = cls._find_scholarship(q)
        if sc:
            docs = sc.get("required_documents", [])
            if not docs:
                return {"answer": f"No documents listed for {sc['scholarship_name']}."}
            return {"answer": f"Documents for **{sc['scholarship_name']}**:\n" +
                              "\n".join(f"  • {d}" for d in docs)}
        return {"answer": "Which scholarship's documents are you asking about?"}

    @classmethod
    def _handle_amount(cls, q):
        sc = cls._find_scholarship(q)
        if sc:
            amt = sc.get("scholarship_amount", 0)
            return {"answer": f"**{sc['scholarship_name']}** provides **₹{amt:,}**."}
        return {"answer": "Which scholarship's amount are you asking about?"}

    @classmethod
    def _handle_count(cls, q):
        count = db.Scholarships.count_documents({"status": "Active"})
        return {"answer": f"There are **{count} active scholarships** in ScholarNexus right now."}

    @classmethod
    def _handle_category(cls, q):
        for cat in ["SC", "ST", "OBC", "Minority", "General"]:
            if cat.lower() in q:
                items = list(db.Scholarships.find(
                    {"status": "Active", "category": {"$in": [cat, "All"]}},
                    {"_id": 0}
                ).limit(5))
                if not items:
                    return {"answer": f"No scholarships found for {cat}."}
                lines = [f"• {s['scholarship_name']}" for s in items]
                return {"answer": f"Scholarships for **{cat}** category:\n" + "\n".join(lines)}
        return {"answer": "Which category? Try SC, ST, OBC, Minority, or General."}

    @classmethod
    def _handle_income(cls, q):
        items = list(db.Scholarships.find(
            {"status": "Active", "max_family_income": {"$lte": 500000}},
            {"_id": 0}
        ).limit(5))
        if not items:
            return {"answer": "No scholarships with income under ₹5L found."}
        lines = [f"• {s['scholarship_name']} — ₹{s.get('max_family_income', 0):,}" for s in items]
        return {"answer": "Scholarships with low income limits:\n" + "\n".join(lines)}

    @classmethod
    def _handle_apply(cls, q):
        sc = cls._find_scholarship(q)
        if sc:
            return {"answer": f"To apply for **{sc['scholarship_name']}**, visit:\n{sc.get('application_url')}\n\n"
                              f"Deadline: {sc.get('application_deadline')}"}
        return {"answer": "Which scholarship are you asking about?"}

    @classmethod
    def _handle_compare(cls, q):
        return {"answer": "To compare scholarships, go to the Compare page and select 2–5 scholarships. "
                          "The system will show them side-by-side with the best value highlighted."}

    @classmethod
    def _handle_lookup(cls, q, user_id):
        sc = cls._find_scholarship(q)
        if sc:
            return {"answer": (
                f"**{sc['scholarship_name']}**\n"
                f"• Provider: {sc.get('provider')}\n"
                f"• Amount: ₹{sc.get('scholarship_amount', 0):,}\n"
                f"• Deadline: {sc.get('application_deadline')}\n"
                f"• Course: {sc.get('course')}\n"
                f"• Category: {sc.get('category')}\n"
                f"• Apply: {sc.get('application_url')}"
            )}
        return {"answer": "I can help with eligibility, deadlines, documents, and amounts. "
                          "Try: *Am I eligible for National Merit Scholarship?*"}


def answer(question, user_id=None):
    return ChatbotService.answer(question, user_id)