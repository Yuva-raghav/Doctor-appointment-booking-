from fastapi import FastAPI
from main import (
    sessions,
    get_available_doctors,
    deduct_slot,
    save_customer
)

app = FastAPI()

@app.post("/message")
def chat(user_id: str, message: str):
    message = message.strip().lower()
    session = sessions.get(user_id, {})

    # STEP 1: GREETING
    if message in ["hi", "hello"] and not session:
        doctors = get_available_doctors()
        if not doctors:
            return {"reply": "❌ No doctors available at the moment."}

        reply = "👋 Welcome to Diya Hospital 😊\n\nAvailable Doctors:\n"
        for i, d in enumerate(doctors, start=1):
            reply += (
                f"{i}️⃣ {d['doctor_name']} — {d['department']} "
                f"(Slots: {d['available_slots']})\n"
            )

        reply += "\nReply with the option number."
        sessions[user_id] = {"step": "choose", "doctors": doctors}
        return {"reply": reply}

    # STEP 2: DOCTOR SELECTION
    if session.get("step") == "choose" and message.isdigit():
        idx = int(message) - 1
        doctors = session["doctors"]

        if 0 <= idx < len(doctors):
            selected = doctors[idx]
            session["selected"] = selected
            session["step"] = "confirm"
            return {
                "reply":
                f"👨‍⚕️ {selected['doctor_name']}\n"
                f"📌 {selected['department']}\n"
                f"🕒 Slots: {selected['available_slots']}\n\n"
                f"Do you want to book? (yes/no)"
            }

        return {"reply": "❌ Invalid option. Try again."}

    # STEP 3: CONFIRM BOOKING
    if session.get("step") == "confirm":
        if message != "yes":
            sessions.pop(user_id)
            return {"reply": "🙏 No problem. Visit again anytime."}

        selected = session["selected"]
        deduct_slot(selected["row_index"], int(selected["available_slots"]))
        session["step"] = "name"
        return {"reply": "Please enter your full name:"}

    # STEP 4: GET NAME
    if session.get("step") == "name":
        session["name"] = message.title()
        session["step"] = "phone"
        return {"reply": "Please enter your phone number:"}

    # STEP 5: GET PHONE & SAVE
    if session.get("step") == "phone":
        if not message.isdigit() or len(message) != 10:
            return {"reply": "❌ Invalid phone number. Enter 10 digits."}

        selected = session["selected"]
        save_customer(
            session["name"],
            message,
            selected["department"],
            selected["doctor_name"]
        )

        sessions.pop(user_id)

        return {
            "reply":
            "✅ Appointment Confirmed!\n\n"
            f"👨‍⚕️ {selected['doctor_name']}\n"
            f"📌 {selected['department']}\n\n"
            "Thank you for choosing Diya Hospital 😊"
        }

    return {"reply": "Please say *Hi* to start 😊"}
