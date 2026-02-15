import Foundation

/// Represents the overall burnout risk assessment
struct BurnoutScore: Codable, Identifiable {
    let id: UUID
    let date: Date
    let score: Double // 0–100
    let sleepScore: Double
    let screenTimeScore: Double
    let moodScore: Double
    let activityScore: Double
    let workloadScore: Double
    let riskLevel: RiskLevel

    init(
        id: UUID = UUID(),
        date: Date = Date(),
        score: Double,
        sleepScore: Double,
        screenTimeScore: Double,
        moodScore: Double,
        activityScore: Double,
        workloadScore: Double
    ) {
        self.id = id
        self.date = date
        self.score = score
        self.sleepScore = sleepScore
        self.screenTimeScore = screenTimeScore
        self.moodScore = moodScore
        self.activityScore = activityScore
        self.workloadScore = workloadScore
        self.riskLevel = RiskLevel.from(score: score)
    }
}

enum RiskLevel: String, Codable, CaseIterable {
    case stable = "Stable"
    case atRisk = "At Risk"
    case burnoutLikely = "Burnout Likely"

    var color: String {
        switch self {
        case .stable: return "green"
        case .atRisk: return "yellow"
        case .burnoutLikely: return "red"
        }
    }

    var emoji: String {
        switch self {
        case .stable: return "🟢"
        case .atRisk: return "🟡"
        case .burnoutLikely: return "🔴"
        }
    }

    static func from(score: Double) -> RiskLevel {
        switch score {
        case 0..<40: return .stable
        case 40..<70: return .atRisk
        default: return .burnoutLikely
        }
    }
}
