import Foundation
import Combine

/// The core burnout scoring engine
/// Calculates a 0–100 burnout risk score based on weighted metrics
final class BurnoutEngine: ObservableObject {
    // Weights for each factor (must sum to 1.0)
    struct Weights {
        var sleep: Double = 0.25
        var screenTime: Double = 0.20
        var mood: Double = 0.25
        var activity: Double = 0.15
        var workload: Double = 0.15
    }

    // Baseline thresholds for scoring
    struct Baselines {
        var idealSleepHours: Double = 7.5
        var maxScreenTimeMinutes: Double = 480 // 8 hours
        var idealSteps: Int = 8000
        var idealActiveMinutes: Double = 30
        var maxCalendarEvents: Int = 8
    }

    let weights: Weights
    let baselines: Baselines

    init(weights: Weights = Weights(), baselines: Baselines = Baselines()) {
        self.weights = weights
        self.baselines = baselines
    }

    // MARK: - Score Calculation

    /// Calculate the overall burnout score from current data
    func calculateScore(
        metrics: HealthMetrics,
        recentMoods: [MoodEntry],
        screenTimeMinutes: Double?,
        screenTimeChange: Double?
    ) -> BurnoutScore {
        let sleepScore = calculateSleepScore(metrics: metrics)
        let screenScore = calculateScreenTimeScore(
            minutes: screenTimeMinutes,
            change: screenTimeChange
        )
        let moodScore = calculateMoodScore(entries: recentMoods)
        let activityScore = calculateActivityScore(metrics: metrics)
        let workloadScore = calculateWorkloadScore(metrics: metrics)

        let totalScore = (sleepScore * weights.sleep +
                         screenScore * weights.screenTime +
                         moodScore * weights.mood +
                         activityScore * weights.activity +
                         workloadScore * weights.workload)

        // Clamp to 0–100
        let clampedScore = min(100, max(0, totalScore))

        return BurnoutScore(
            score: clampedScore,
            sleepScore: sleepScore,
            screenTimeScore: screenScore,
            moodScore: moodScore,
            activityScore: activityScore,
            workloadScore: workloadScore
        )
    }

    // MARK: - Individual Score Components

    /// Sleep score: higher = more burned out
    /// Factors: hours below ideal + inconsistency
    func calculateSleepScore(metrics: HealthMetrics) -> Double {
        var score: Double = 50 // default if no data

        if let hours = metrics.sleepHours {
            // Score based on deviation from ideal
            let deficit = max(0, baselines.idealSleepHours - hours)
            // Each hour of deficit = ~15 points of burnout risk
            let deficitScore = min(60, deficit * 15)

            // Consistency factor
            let consistencyPenalty: Double
            if let consistency = metrics.sleepConsistency {
                // Lower consistency = higher penalty
                consistencyPenalty = (1.0 - consistency) * 40
            } else {
                consistencyPenalty = 0
            }

            score = deficitScore + consistencyPenalty
        }

        return min(100, max(0, score))
    }

    /// Screen time score: higher = more burned out
    /// Factors: absolute time + increase from baseline
    func calculateScreenTimeScore(minutes: Double?, change: Double?) -> Double {
        var score: Double = 50

        if let minutes = minutes {
            // Base score from absolute screen time
            let ratio = minutes / baselines.maxScreenTimeMinutes
            let baseScore = min(50, ratio * 50)

            // Spike penalty: if screen time increased significantly
            let spikePenalty: Double
            if let change = change, change > 0 {
                // Each 10% increase = 5 points
                spikePenalty = min(50, (change / 10) * 5)
            } else {
                spikePenalty = 0
            }

            score = baseScore + spikePenalty
        }

        return min(100, max(0, score))
    }

    /// Mood score: higher = more burned out
    /// Based on recent mood trend
    func calculateMoodScore(entries: [MoodEntry]) -> Double {
        guard !entries.isEmpty else { return 50 }

        // Average of recent mood entries (inverted: lower mood = higher burnout)
        let avgMood = entries.reduce(0.0) { $0 + $1.mood.normalizedScore } / Double(entries.count)

        // Invert: great mood (1.0) = low burnout (0), exhausted (0.0) = high burnout (100)
        let moodBurnout = (1.0 - avgMood) * 70

        // Trend penalty: if mood is declining
        let trendPenalty = calculateMoodTrendPenalty(entries: entries)

        return min(100, max(0, moodBurnout + trendPenalty))
    }

    /// Check if mood is trending downward
    private func calculateMoodTrendPenalty(entries: [MoodEntry]) -> Double {
        guard entries.count >= 3 else { return 0 }

        let sorted = entries.sorted { $0.date < $1.date }
        let recentHalf = Array(sorted.suffix(sorted.count / 2))
        let olderHalf = Array(sorted.prefix(sorted.count / 2))

        let recentAvg = recentHalf.reduce(0.0) { $0 + $1.mood.normalizedScore } / Double(recentHalf.count)
        let olderAvg = olderHalf.reduce(0.0) { $0 + $1.mood.normalizedScore } / Double(olderHalf.count)

        // If recent mood is lower than older mood, add penalty
        let decline = olderAvg - recentAvg
        if decline > 0 {
            return decline * 30 // Up to 30 points for sharp decline
        }
        return 0
    }

    /// Activity score: higher = more burned out
    /// Based on step count and active minutes relative to baseline
    func calculateActivityScore(metrics: HealthMetrics) -> Double {
        var score: Double = 50

        if let steps = metrics.stepCount {
            let stepRatio = Double(steps) / Double(baselines.idealSteps)
            // Fewer steps = higher burnout risk
            let stepScore = (1.0 - min(1.0, stepRatio)) * 60

            if let activeMinutes = metrics.activeMinutes {
                let activeRatio = activeMinutes / baselines.idealActiveMinutes
                let activeScore = (1.0 - min(1.0, activeRatio)) * 40
                score = stepScore + activeScore
            } else {
                score = stepScore + 20 // assume some penalty if no data
            }
        }

        return min(100, max(0, score))
    }

    /// Workload score: higher = more burned out
    /// Based on calendar density
    func calculateWorkloadScore(metrics: HealthMetrics) -> Double {
        guard let eventCount = metrics.calendarEventCount else { return 30 }

        let ratio = Double(eventCount) / Double(baselines.maxCalendarEvents)
        let score = min(100, ratio * 80)

        // Weekend penalty: working on weekends is a red flag
        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: metrics.date)
        let isWeekend = weekday == 1 || weekday == 7

        if isWeekend && eventCount > 2 {
            return min(100, score + 20) // Extra penalty for busy weekends
        }

        return max(0, score)
    }

    // MARK: - Risk Triggers

    /// Identify which factors are driving the burnout score
    func identifyRiskTriggers(score: BurnoutScore) -> [RiskTrigger] {
        var triggers: [RiskTrigger] = []

        if score.sleepScore > 60 {
            triggers.append(RiskTrigger(
                metric: "Sleep",
                severity: score.sleepScore > 80 ? .high : .medium,
                message: "Your sleep quality has been declining"
            ))
        }

        if score.screenTimeScore > 60 {
            triggers.append(RiskTrigger(
                metric: "Screen Time",
                severity: score.screenTimeScore > 80 ? .high : .medium,
                message: "Screen time is above your baseline"
            ))
        }

        if score.moodScore > 60 {
            triggers.append(RiskTrigger(
                metric: "Mood",
                severity: score.moodScore > 80 ? .high : .medium,
                message: "Your mood has been trending down"
            ))
        }

        if score.activityScore > 60 {
            triggers.append(RiskTrigger(
                metric: "Activity",
                severity: score.activityScore > 80 ? .high : .medium,
                message: "Physical activity has dropped"
            ))
        }

        if score.workloadScore > 60 {
            triggers.append(RiskTrigger(
                metric: "Workload",
                severity: score.workloadScore > 80 ? .high : .medium,
                message: "Your schedule is overloaded"
            ))
        }

        return triggers.sorted { $0.severity.rawValue > $1.severity.rawValue }
    }

    /// Suggest an intervention based on the highest risk factor
    func suggestIntervention(score: BurnoutScore) -> Intervention {
        let triggers = identifyRiskTriggers(score: score)

        if score.riskLevel == .burnoutLikely {
            return InterventionLibrary.all.first { $0.category == .emergency }
                ?? InterventionLibrary.all[0]
        }

        guard let topTrigger = triggers.first else {
            return InterventionLibrary.all[0] // Default to breathing
        }

        switch topTrigger.metric {
        case "Sleep":
            return InterventionLibrary.all.first { $0.category == .breathing }
                ?? InterventionLibrary.all[0]
        case "Screen Time":
            return InterventionLibrary.all.first { $0.category == .digital }
                ?? InterventionLibrary.all[0]
        case "Mood":
            return InterventionLibrary.all.first { $0.category == .social }
                ?? InterventionLibrary.all[0]
        case "Activity":
            return InterventionLibrary.all.first { $0.category == .movement }
                ?? InterventionLibrary.all[0]
        case "Workload":
            return InterventionLibrary.all.first { $0.category == .sound }
                ?? InterventionLibrary.all[0]
        default:
            return InterventionLibrary.all[0]
        }
    }
}

// MARK: - Risk Trigger Model

struct RiskTrigger: Identifiable {
    let id = UUID()
    let metric: String
    let severity: Severity
    let message: String

    enum Severity: Int, Comparable {
        case low = 1
        case medium = 2
        case high = 3

        static func < (lhs: Severity, rhs: Severity) -> Bool {
            lhs.rawValue < rhs.rawValue
        }

        var color: String {
            switch self {
            case .low: return "yellow"
            case .medium: return "orange"
            case .high: return "red"
            }
        }
    }
}
