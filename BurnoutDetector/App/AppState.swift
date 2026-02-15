import SwiftUI
import Combine

final class AppState: ObservableObject {
    @AppStorage("hasCompletedOnboarding") var hasCompletedOnboarding = false
    @AppStorage("notificationsEnabled") var notificationsEnabled = true
    @AppStorage("darkModeEnabled") var darkModeEnabled = false
    @AppStorage("dailyCheckInTime") var dailyCheckInTime: Double = 54000 // 3:00 PM default (seconds since midnight)
    @Published var selectedTab: Tab = .dashboard

    enum Tab: Int, CaseIterable {
        case dashboard = 0
        case mood
        case trends
        case interventions
        case settings
    }
}
