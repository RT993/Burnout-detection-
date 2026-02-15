import SwiftUI

@main
struct BurnoutDetectorApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var healthService = HealthKitService()
    @StateObject private var dataStore = DataStore()
    @StateObject private var notificationService = NotificationService()

    var body: some Scene {
        WindowGroup {
            if appState.hasCompletedOnboarding {
                MainTabView()
                    .environmentObject(appState)
                    .environmentObject(healthService)
                    .environmentObject(dataStore)
                    .environmentObject(notificationService)
            } else {
                OnboardingView()
                    .environmentObject(appState)
                    .environmentObject(healthService)
            }
        }
    }
}
