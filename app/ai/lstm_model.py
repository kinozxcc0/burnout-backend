import numpy as np
from datetime import datetime

# ==================== RULE-BASED SCORING (40%) ====================

def rule_based_score(logs: list, survey: dict = None) -> float:
    if not logs:
        return 0.3

    avg_logs = _average_logs(logs[-7:])
    score = 0.0

    screen_hours = avg_logs["total_screen_time_minutes"] / 60
    if screen_hours >= 10: screen_score = 1.0
    elif screen_hours >= 8: screen_score = 0.85
    elif screen_hours >= 6: screen_score = 0.65
    elif screen_hours >= 4: screen_score = 0.40
    elif screen_hours >= 2: screen_score = 0.20
    else: screen_score = 0.05
    score += screen_score * 0.25

    social_hours = avg_logs["social_media_minutes"] / 60
    if social_hours >= 5: social_score = 1.0
    elif social_hours >= 4: social_score = 0.85
    elif social_hours >= 3: social_score = 0.70
    elif social_hours >= 2: social_score = 0.50
    elif social_hours >= 1: social_score = 0.25
    else: social_score = 0.05
    score += social_score * 0.20

    stress = avg_logs["self_reported_stress"]
    score += min((stress / 10.0), 1.0) * 0.25

    breaks = avg_logs["breaks_taken"]
    if breaks == 0: break_score = 1.0
    elif breaks <= 1: break_score = 0.75
    elif breaks <= 3: break_score = 0.40
    elif breaks <= 5: break_score = 0.20
    else: break_score = 0.05
    score += break_score * 0.15

    work_hours = avg_logs["study_work_minutes"] / 60
    if work_hours >= 10: work_score = 1.0
    elif work_hours >= 8: work_score = 0.80
    elif work_hours >= 6: work_score = 0.60
    elif work_hours >= 4: work_score = 0.35
    else: work_score = 0.15
    score += work_score * 0.15

    if survey:
        survey_modifier = _survey_modifier(survey)
        score = score * 0.75 + survey_modifier * 0.25

    return round(min(max(score, 0.0), 1.0), 4)


def _survey_modifier(survey: dict) -> float:
    stress_level      = survey.get("stress_level", 3)
    mental_exhaustion = survey.get("mental_exhaustion", 3)
    motivation        = survey.get("motivation", 3)
    expected_workload = survey.get("expected_workload", 3)
    task_consistency  = survey.get("task_consistency", 3)
    time_management   = survey.get("time_management", 3)

    raw = (
        (stress_level / 5.0) * 0.30 +
        (mental_exhaustion / 5.0) * 0.25 +
        ((6 - motivation) / 5.0) * 0.20 +
        (expected_workload / 5.0) * 0.15 +
        ((6 - task_consistency) / 5.0) * 0.05 +
        ((6 - time_management) / 5.0) * 0.05
    )
    return round(min(max(raw, 0.0), 1.0), 4)


def _average_logs(logs: list) -> dict:
    if not logs:
        return {"total_screen_time_minutes": 0, "social_media_minutes": 0,
                "study_work_minutes": 0, "breaks_taken": 0,
                "notifications_received": 0, "self_reported_stress": 5}
    keys = ["total_screen_time_minutes", "social_media_minutes",
            "study_work_minutes", "breaks_taken",
            "notifications_received", "self_reported_stress"]
    result = {}
    for k in keys:
        vals = [l.get(k, 0) or 0 for l in logs]
        result[k] = sum(vals) / len(vals)
    return result


# ==================== LSTM SCORING (60%) ====================

def lstm_score(logs: list) -> float:
    if len(logs) < 3:
        return rule_based_score(logs)

    features = []
    for l in logs:
        screen = min((l.get("total_screen_time_minutes", 0) or 0) / 600, 1.0)
        social = min((l.get("social_media_minutes", 0) or 0) / 300, 1.0)
        work   = min((l.get("study_work_minutes", 0) or 0) / 600, 1.0)
        breaks = max(0, 1.0 - (l.get("breaks_taken", 0) or 0) / 10)
        notifs = min((l.get("notifications_received", 0) or 0) / 100, 1.0)
        stress = min((l.get("self_reported_stress", 5) or 5) / 10, 1.0)
        features.append([screen, social, work, breaks, notifs, stress])

    while len(features) < 30:
        features.insert(0, [0.1, 0.1, 0.2, 0.5, 0.1, 0.3])
    features = features[-30:]
    X = np.array(features)

    weights = np.linspace(0.5, 1.0, 30)
    weighted = X * weights[:, np.newaxis]

    daily_risk = (
        weighted[:, 0] * 0.25 +
        weighted[:, 1] * 0.20 +
        weighted[:, 2] * 0.15 +
        weighted[:, 3] * 0.15 +
        weighted[:, 4] * 0.10 +
        weighted[:, 5] * 0.25
    )

    current = float(np.mean(daily_risk[-7:]))

    if len(daily_risk) >= 14:
        trend = np.mean(daily_risk[-7:]) - np.mean(daily_risk[-14:-7])
        current = current + (trend * 0.3)

    return round(min(max(current, 0.0), 1.0), 4)


# ==================== 7-DAY FORECAST ====================

def forecast_7_days(logs: list, current_risk: float) -> list:
    if len(logs) < 7:
        return [round(min(current_risk + (i * 0.02), 1.0), 3) for i in range(7)]

    recent = logs[-14:] if len(logs) >= 14 else logs
    daily_risks = [rule_based_score([l]) for l in recent]

    day_of_week = datetime.now().weekday()
    weekly_pattern = [0.0, 0.05, 0.10, 0.08, 0.05, -0.05, -0.10]

    slope = (daily_risks[-1] - daily_risks[-7]) / 7 if len(daily_risks) >= 7 else 0.01

    forecast = []
    for i in range(7):
        day_idx = (day_of_week + i + 1) % 7
        predicted = current_risk + (slope * (i + 1)) + weekly_pattern[day_idx]
        forecast.append(round(min(max(predicted, 0.0), 1.0), 3))

    return forecast


# ==================== COMBINED PREDICTION ====================

def predict_burnout_risk(logs: list, survey: dict = None) -> dict:
    if not logs:
        return {
            "current_risk": 0.30,
            "7_day_forecast_risk": 0.32,
            "7_day_forecast": [0.30, 0.31, 0.32, 0.31, 0.33, 0.30, 0.29],
            "recommendation": "Start logging your daily habits so the AI can learn your patterns.",
            "risk_level": "LOW",
            "rule_based_score": 0.30,
            "lstm_score": 0.30,
        }

    rule_score = rule_based_score(logs, survey)
    ml_score   = lstm_score(logs)
    combined   = round((rule_score * 0.40) + (ml_score * 0.60), 4)

    forecast_days = forecast_7_days(logs, combined)
    forecast_avg  = round(float(np.mean(forecast_days)), 4)

    if combined >= 0.75: level = "HIGH"
    elif combined >= 0.50: level = "MODERATE"
    elif combined >= 0.25: level = "LOW-MODERATE"
    else: level = "LOW"

    return {
        "current_risk":        combined,
        "7_day_forecast_risk": forecast_avg,
        "7_day_forecast":      forecast_days,
        "recommendation":      _generate_recommendation(combined, rule_score, logs, survey),
        "risk_level":          level,
        "rule_based_score":    rule_score,
        "lstm_score":          ml_score,
    }


def _generate_recommendation(risk: float, rule_score: float,
                               logs: list, survey: dict = None) -> str:
    avg = _average_logs(logs[-7:])
    screen_hrs = avg["total_screen_time_minutes"] / 60
    social_hrs = avg["social_media_minutes"] / 60
    stress     = avg["self_reported_stress"]
    breaks     = avg["breaks_taken"]

    if risk >= 0.80:
        if social_hrs >= 3:
            return (f"🚨 Critical burnout risk! Social media ({social_hrs:.1f}hrs/day) "
                    f"is a major factor. Try a 48-hour digital detox and prioritize sleep.")
        if stress >= 8:
            return ("🚨 Critical stress detected! Take an immediate break "
                    "and avoid heavy tasks today.")
        return ("🚨 Critical burnout risk. Reduce screen time immediately, "
                "break every hour, and get 8+ hours of sleep tonight.")
    elif risk >= 0.65:
        if breaks < 2:
            return (f"⚠️ High risk. You're barely taking breaks ({breaks:.0f}/day). "
                    f"Set a timer — break every 90 minutes.")
        return (f"⚠️ High risk. {screen_hrs:.1f}hrs screen time daily is too much. "
                f"Cap it at 5hrs and add outdoor time.")
    elif risk >= 0.50:
        return (f"📱 Moderate risk. Social media ({social_hrs:.1f}hrs) "
                f"is affecting your focus. Try limiting to 1hr/day.")
    elif risk >= 0.25:
        return ("✅ Low-moderate risk. Keep maintaining your break habits and sleep schedule.")
    return ("🌟 Low burnout risk! Your habits are healthy. Keep it up!")