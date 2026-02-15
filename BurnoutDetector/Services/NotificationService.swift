import Foundation
import UserNotifications
import Combine

/// Smart notification service — only notifies when it matters
final class NotificationService: ObservableObject {
    @Published var isAuthorized = false

    // MARK: - Authorization

    func requestAuthorization() async -> Bool {
        do {
            let granted = try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .sound, .badge])
            await MainActor.run { self.isAuthorized = granted }
            return granted
        } catch {
            return false
        }
    }

    // MARK: - Daily Mood Check Reminder

    func scheduleDailyMoodCheck(at hour: Int = 15, minute: Int = 0) {
        let content = UNMutableNotificationContent()
        content.title = "Quick Check-In"
        content.body = "How are you feeling right now? It takes 10 seconds."
        content.sound = .default
        content.categoryIdentifier = "MOOD_CHECK"

        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = minute

        let trigger = UNCalendarNotificationTrigger(
            dateMatching: dateComponents,
            repeats: true
        )

        let request = UNNotificationRequest(
            identifier: "daily-mood-check",
            content: content,
            trigger: trigger
        )

        UNUserNotificationCenter.current().add(request)
    }

    // MARK: - Risk Alert

    func sendRiskAlert(score: BurnoutScore) {
        guard score.riskLevel != .stable else { return }

        let content = UNMutableNotificationContent()

        switch score.riskLevel {
        case .atRisk:
            content.title = "Burnout Risk Detected"
            content.body = "Your burnout score is \(Int(score.score)). Take a moment to reset."
        case .burnoutLikely:
            content.title = "High Burnout Risk"
            content.body = "Your burnout score is \(Int(score.score)). Please take care of yourself."
        case .stable:
            return
        }

        content.sound = .default
        content.categoryIdentifier = "RISK_ALERT"

        let request = UNNotificationRequest(
            identifier: "risk-alert-\(UUID().uuidString)",
            content: content,
            trigger: nil // Deliver immediately
        )

        UNUserNotificationCenter.current().add(request)
    }

    // MARK: - Intervention Reminder

    func scheduleInterventionReminder(intervention: Intervention, delay: TimeInterval = 300) {
        let content = UNMutableNotificationContent()
        content.title = "Try This: \(intervention.title)"
        content.body = intervention.description
        content.sound = .default
        content.categoryIdentifier = "INTERVENTION"

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: delay,
            repeats: false
        )

        let request = UNNotificationRequest(
            identifier: "intervention-\(intervention.id.uuidString)",
            content: content,
            trigger: trigger
        )

        UNUserNotificationCenter.current().add(request)
    }

    // MARK: - Cancel

    func cancelAllNotifications() {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }

    func cancelDailyMoodCheck() {
        UNUserNotificationCenter.current()
            .removePendingNotificationRequests(withIdentifiers: ["daily-mood-check"])
    }
}
