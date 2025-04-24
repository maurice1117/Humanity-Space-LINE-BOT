def enrich_with_rag(reservation: dict, rag_file="data/人性空間資訊.txt") -> dict:
    try:
        with open(rag_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return reservation

    user_name = reservation.get("name", "")
    user_tel = reservation.get("tel", "")
    enriched_note = reservation.get("memo", "")

    for line in lines:
        if user_name in line or user_tel in line:
            enriched_note += f"；補充資料：{line.strip()}"

    reservation["memo"] = enriched_note
    return reservation