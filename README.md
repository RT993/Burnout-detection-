# Burnout Detector

**"We detect burnout before you feel it."**

A predictive early warning system for burnout, built as an iOS app with SwiftUI. This is not a meditation or journaling app — it's a data-driven system that tracks behavioral signals and alerts you before collapse.

## MVP Feature Set

### Passive Data Collection
- Sleep hours and consistency (via HealthKit)
- Step count and active minutes (via HealthKit)
- Screen time tracking (via Screen Time API / DeviceActivity)
- Calendar workload density (optional)

### Micro Mood Check (10 seconds/day)
Daily check-in with 5 levels: Great, Okay, Flat, Stressed, Exhausted. Trains the prediction model over time.

### Burnout Score (0–100)
Weighted algorithm combining:
| Factor | Weight |
|--------|--------|
| Sleep consistency | 25% |
| Screen time spikes | 20% |
| Mood trend | 25% |
| Physical activity | 15% |
| Workload density | 15% |

Risk levels: **Stable** (0–39) | **At Risk** (40–69) | **Burnout Likely** (70–100)

### Micro Intervention Engine
Context-aware suggestions when risk rises:
- Box breathing / 4-7-8 breathing
- 10-minute walk / desk stretches
- Social connection prompts
- Screen break timers
- Nervous system reset audio
- Emergency "Overwhelmed Mode" (5-4-3-2-1 grounding)

## Tech Stack
- **SwiftUI** — declarative UI
- **HealthKit** — sleep, steps, activity data
- **Screen Time API** (DeviceActivity / FamilyControls) — screen usage
- **UserNotifications** — smart alerts
- **Local-first** — all data on-device, no cloud sync

## Project Structure
```
BurnoutDetector/
├── App/
│   ├── BurnoutDetectorApp.swift    # Entry point
│   └── AppState.swift              # Global state
├── Models/
│   ├── BurnoutScore.swift          # Score + risk levels
│   ├── MoodEntry.swift             # Mood check-in data
│   ├── HealthMetrics.swift         # Daily health data
│   └── Intervention.swift          # Intervention library
├── Services/
│   ├── HealthKitService.swift      # HealthKit integration
│   ├── ScreenTimeService.swift     # Screen Time tracking
│   ├── BurnoutEngine.swift         # Scoring algorithm
│   ├── DataStore.swift             # Local persistence
│   └── NotificationService.swift   # Smart notifications
├── Views/
│   ├── MainTabView.swift           # Tab navigation
│   ├── OnboardingView.swift        # First-run flow
│   ├── Dashboard/
│   │   └── DashboardView.swift     # Score ring + metrics
│   ├── MoodCheck/
│   │   └── MoodCheckView.swift     # Daily mood check-in
│   ├── Trends/
│   │   └── TrendsView.swift        # 7-day charts + heatmap
│   ├── Interventions/
│   │   ├── InterventionsView.swift # Intervention library
│   │   └── InterventionDetailView.swift # Guided sessions
│   ├── Settings/
│   │   └── SettingsView.swift      # Permissions + privacy
│   └── Components/
│       ├── ScoreRingView.swift     # Animated score ring
│       ├── MetricCardView.swift    # Metric display card
│       └── MiniChartView.swift     # Sparkline charts
├── Extensions/
│   ├── Date+Extensions.swift
│   └── Color+Extensions.swift
└── Resources/
    └── Assets.xcassets/
```

## Scoring Algorithm
```
SleepScore    = f(sleepDeficit, sleepConsistency) × 0.25
ScreenScore   = f(absoluteTime, spikeFromBaseline) × 0.20
MoodScore     = f(averageMood, moodTrendDecline)   × 0.25
ActivityScore = f(stepDeficit, activeMinuteDeficit) × 0.15
WorkloadScore = f(calendarDensity, weekendWork)     × 0.15

BurnoutScore  = Sum(all weighted scores), clamped 0–100
```

## Phase 2 Roadmap
- AI trend analysis (weekly insights)
- 7-day burnout prediction
- Workplace/team version (anonymous burnout index)
- Apple Watch integration with HRV tracking
- CoreML on-device prediction model
- Freemium monetization (Pro at 4.99/month, B2B dashboard)

## Privacy
All data is stored locally on-device. No cloud sync, no analytics, no tracking. Users can export or delete all data at any time.
