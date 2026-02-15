import SwiftUI

/// Main tab navigation with 5 tabs
struct MainTabView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        TabView(selection: $appState.selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "gauge.medium")
                }
                .tag(AppState.Tab.dashboard)

            MoodCheckView()
                .tabItem {
                    Label("Mood", systemImage: "face.smiling")
                }
                .tag(AppState.Tab.mood)

            TrendsView()
                .tabItem {
                    Label("Trends", systemImage: "chart.line.uptrend.xyaxis")
                }
                .tag(AppState.Tab.trends)

            InterventionsView()
                .tabItem {
                    Label("Reset", systemImage: "heart.circle")
                }
                .tag(AppState.Tab.interventions)

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(AppState.Tab.settings)
        }
        .tint(.blue)
    }
}

#Preview {
    MainTabView()
        .environmentObject(AppState())
        .environmentObject(HealthKitService())
        .environmentObject(DataStore())
        .environmentObject(NotificationService())
}
