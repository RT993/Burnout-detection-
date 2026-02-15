import Foundation

/// Daily health data collected from HealthKit and Screen Time
struct HealthMetrics: Codable, Identifiable {
    let id: UUID
    let date: Date
    var sleepHours: Double?
    var sleepConsistency: Double? // 0.0–1.0, how consistent sleep schedule is
    var stepCount: Int?
    var activeMinutes: Double?
    var screenTimeMinutes: Double?
    var screenTimeChange: Double? // % change from baseline
    var calendarEventCount: Int?
    var workAppMinutes: Double?
    var entertainmentAppMinutes: Double?

    init(
        id: UUID = UUID(),
        date: Date = Date(),
        sleepHours: Double? = nil,
        sleepConsistency: Double? = nil,
        stepCount: Int? = nil,
        activeMinutes: Double? = nil,
        screenTimeMinutes: Double? = nil,
        screenTimeChange: Double? = nil,
        calendarEventCount: Int? = nil,
        workAppMinutes: Double? = nil,
        entertainmentAppMinutes: Double? = nil
    ) {
        self.id = id
        self.date = date
        self.sleepHours = sleepHours
        self.sleepConsistency = sleepConsistency
        self.stepCount = stepCount
        self.activeMinutes = activeMinutes
        self.screenTimeMinutes = screenTimeMinutes
        self.screenTimeChange = screenTimeChange
        self.calendarEventCount = calendarEventCount
        self.workAppMinutes = workAppMinutes
        self.entertainmentAppMinutes = entertainmentAppMinutes
    }
}

/// Aggregated metrics over a period for trend analysis
struct MetricsTrend: Codable {
    let metric: String
    let currentValue: Double
    let baselineValue: Double
    let percentChange: Double
    let direction: TrendDirection
}

enum TrendDirection: String, Codable {
    case up = "up"
    case down = "down"
    case stable = "stable"

    var arrow: String {
        switch self {
        case .up: return "↑"
        case .down: return "↓"
        case .stable: return "→"
        }
    }
}
