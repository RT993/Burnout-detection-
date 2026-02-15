import Foundation
import DeviceActivity
import ManagedSettings
import FamilyControls
import Combine

/// Service for tracking screen time data
/// Note: Full Screen Time API requires Family Controls entitlement.
/// For MVP, we use a combination of DeviceActivity and manual tracking.
final class ScreenTimeService: ObservableObject {
    @Published var isAuthorized = false
    @Published var todayScreenTimeMinutes: Double = 0
    @Published var screenTimeChange: Double = 0 // % change from 7-day baseline

    private let defaults = UserDefaults.standard
    private let baselineKey = "screenTimeBaseline"
    private let historyKey = "screenTimeHistory"

    // MARK: - Authorization

    func requestAuthorization() async -> Bool {
        do {
            try await AuthorizationCenter.shared.requestAuthorization(for: .individual)
            await MainActor.run { self.isAuthorized = true }
            return true
        } catch {
            await MainActor.run { self.isAuthorized = false }
            return false
        }
    }

    // MARK: - Screen Time Tracking

    /// Record today's screen time (called from DeviceActivity monitor or manually)
    func recordScreenTime(minutes: Double) {
        todayScreenTimeMinutes = minutes

        // Store in history
        var history = getScreenTimeHistory()
        let todayKey = dateKey(for: Date())
        history[todayKey] = minutes
        saveScreenTimeHistory(history)

        // Calculate change from baseline
        updateScreenTimeChange()
    }

    /// Calculate the 7-day baseline average screen time
    func calculateBaseline() -> Double {
        let history = getScreenTimeHistory()
        let calendar = Calendar.current

        var total: Double = 0
        var count = 0

        for dayOffset in 1...7 {
            guard let date = calendar.date(byAdding: .day, value: -dayOffset, to: Date()) else {
                continue
            }
            let key = dateKey(for: date)
            if let minutes = history[key] {
                total += minutes
                count += 1
            }
        }

        return count > 0 ? total / Double(count) : 0
    }

    /// Update the % change from baseline
    private func updateScreenTimeChange() {
        let baseline = calculateBaseline()
        guard baseline > 0 else {
            screenTimeChange = 0
            return
        }
        screenTimeChange = ((todayScreenTimeMinutes - baseline) / baseline) * 100
    }

    // MARK: - Persistence Helpers

    private func dateKey(for date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }

    private func getScreenTimeHistory() -> [String: Double] {
        return defaults.dictionary(forKey: historyKey) as? [String: Double] ?? [:]
    }

    private func saveScreenTimeHistory(_ history: [String: Double]) {
        defaults.set(history, forKey: historyKey)
    }

    /// Get screen time for a specific date
    func screenTime(for date: Date) -> Double? {
        let history = getScreenTimeHistory()
        return history[dateKey(for: date)]
    }

    /// Get screen time history for the last N days
    func getHistory(days: Int = 7) -> [(date: Date, minutes: Double)] {
        let history = getScreenTimeHistory()
        let calendar = Calendar.current
        var result: [(date: Date, minutes: Double)] = []

        for dayOffset in 0..<days {
            guard let date = calendar.date(byAdding: .day, value: -dayOffset, to: Date()) else {
                continue
            }
            let key = dateKey(for: date)
            if let minutes = history[key] {
                result.append((date: date, minutes: minutes))
            }
        }

        return result.reversed()
    }
}
