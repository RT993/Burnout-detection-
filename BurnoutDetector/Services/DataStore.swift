import Foundation
import Combine

/// Local-first data persistence layer
/// Stores all user data on-device for privacy
final class DataStore: ObservableObject {
    @Published var moodEntries: [MoodEntry] = []
    @Published var burnoutScores: [BurnoutScore] = []
    @Published var healthMetrics: [HealthMetrics] = []
    @Published var latestScore: BurnoutScore?

    private let moodKey = "moodEntries"
    private let scoresKey = "burnoutScores"
    private let metricsKey = "healthMetrics"

    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    init() {
        loadAll()
    }

    // MARK: - Mood Entries

    func saveMoodEntry(_ entry: MoodEntry) {
        moodEntries.append(entry)
        moodEntries.sort { $0.date > $1.date }
        persist(moodEntries, forKey: moodKey)
    }

    func todaysMoodEntry() -> MoodEntry? {
        let today = Calendar.current.startOfDay(for: Date())
        return moodEntries.first { Calendar.current.startOfDay(for: $0.date) == today }
    }

    func recentMoodEntries(days: Int = 7) -> [MoodEntry] {
        let cutoff = Calendar.current.date(byAdding: .day, value: -days, to: Date()) ?? Date()
        return moodEntries.filter { $0.date >= cutoff }.sorted { $0.date < $1.date }
    }

    // MARK: - Burnout Scores

    func saveBurnoutScore(_ score: BurnoutScore) {
        burnoutScores.append(score)
        burnoutScores.sort { $0.date > $1.date }
        latestScore = burnoutScores.first
        persist(burnoutScores, forKey: scoresKey)
    }

    func recentScores(days: Int = 7) -> [BurnoutScore] {
        let cutoff = Calendar.current.date(byAdding: .day, value: -days, to: Date()) ?? Date()
        return burnoutScores.filter { $0.date >= cutoff }.sorted { $0.date < $1.date }
    }

    // MARK: - Health Metrics

    func saveHealthMetrics(_ metrics: HealthMetrics) {
        // Replace if same date exists
        let dateKey = Calendar.current.startOfDay(for: metrics.date)
        healthMetrics.removeAll { Calendar.current.startOfDay(for: $0.date) == dateKey }
        healthMetrics.append(metrics)
        healthMetrics.sort { $0.date > $1.date }
        persist(healthMetrics, forKey: metricsKey)
    }

    func recentMetrics(days: Int = 7) -> [HealthMetrics] {
        let cutoff = Calendar.current.date(byAdding: .day, value: -days, to: Date()) ?? Date()
        return healthMetrics.filter { $0.date >= cutoff }.sorted { $0.date < $1.date }
    }

    // MARK: - Data Export

    /// Export all user data as JSON for privacy/portability
    func exportData() -> Data? {
        let exportPayload: [String: Any] = [
            "exportDate": ISO8601DateFormatter().string(from: Date()),
            "moodEntries": (try? encoder.encode(moodEntries)) ?? Data(),
            "burnoutScores": (try? encoder.encode(burnoutScores)) ?? Data(),
            "healthMetrics": (try? encoder.encode(healthMetrics)) ?? Data()
        ]
        return try? JSONSerialization.data(withJSONObject: exportPayload, options: .prettyPrinted)
    }

    /// Delete all stored data
    func deleteAllData() {
        moodEntries = []
        burnoutScores = []
        healthMetrics = []
        latestScore = nil

        UserDefaults.standard.removeObject(forKey: moodKey)
        UserDefaults.standard.removeObject(forKey: scoresKey)
        UserDefaults.standard.removeObject(forKey: metricsKey)
    }

    // MARK: - Persistence Helpers

    private func persist<T: Encodable>(_ data: T, forKey key: String) {
        if let encoded = try? encoder.encode(data) {
            UserDefaults.standard.set(encoded, forKey: key)
        }
    }

    private func load<T: Decodable>(forKey key: String) -> T? {
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? decoder.decode(T.self, from: data)
    }

    private func loadAll() {
        moodEntries = load(forKey: moodKey) ?? []
        burnoutScores = load(forKey: scoresKey) ?? []
        healthMetrics = load(forKey: metricsKey) ?? []
        latestScore = burnoutScores.first
    }
}
