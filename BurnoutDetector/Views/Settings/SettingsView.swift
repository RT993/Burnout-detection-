import SwiftUI

/// Settings screen: permissions, notifications, privacy, data export
struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var healthService: HealthKitService
    @EnvironmentObject var dataStore: DataStore
    @EnvironmentObject var notificationService: NotificationService

    @State private var showDeleteConfirmation = false
    @State private var showExportSheet = false
    @State private var exportURL: URL?

    var body: some View {
        NavigationStack {
            List {
                // Data Permissions
                permissionsSection

                // Notifications
                notificationsSection

                // Appearance
                appearanceSection

                // Privacy & Data
                privacySection

                // About
                aboutSection
            }
            .navigationTitle("Settings")
            .alert("Delete All Data", isPresented: $showDeleteConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Delete", role: .destructive) {
                    dataStore.deleteAllData()
                }
            } message: {
                Text("This will permanently delete all your mood entries, scores, and health data stored in the app. This cannot be undone.")
            }
            .sheet(isPresented: $showExportSheet) {
                if let url = exportURL {
                    ShareSheet(activityItems: [url])
                }
            }
        }
    }

    // MARK: - Permissions

    private var permissionsSection: some View {
        Section("Data Permissions") {
            HStack {
                Label("HealthKit", systemImage: "heart.fill")
                Spacer()
                if healthService.isAuthorized {
                    Text("Connected")
                        .font(.caption)
                        .foregroundColor(.green)
                } else {
                    Button("Connect") {
                        Task { await healthService.requestAuthorization() }
                    }
                    .font(.caption)
                }
            }

            HStack {
                Label("Screen Time", systemImage: "hourglass")
                Spacer()
                Text("Requires setup")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            HStack {
                Label("Calendar", systemImage: "calendar")
                Spacer()
                Text("Optional")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Notifications

    private var notificationsSection: some View {
        Section("Notifications") {
            Toggle(isOn: $appState.notificationsEnabled) {
                Label("Daily Check-In Reminder", systemImage: "bell.fill")
            }
            .onChange(of: appState.notificationsEnabled) { enabled in
                if enabled {
                    notificationService.scheduleDailyMoodCheck()
                } else {
                    notificationService.cancelDailyMoodCheck()
                }
            }

            HStack {
                Label("Check-In Time", systemImage: "clock")
                Spacer()
                Text("3:00 PM")
                    .foregroundColor(.secondary)
            }

            HStack {
                Label("Risk Alerts", systemImage: "exclamationmark.triangle")
                Spacer()
                Text("When score rises")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Appearance

    private var appearanceSection: some View {
        Section("Appearance") {
            Toggle(isOn: $appState.darkModeEnabled) {
                Label("Dark Mode", systemImage: "moon.circle.fill")
            }
        }
    }

    // MARK: - Privacy

    private var privacySection: some View {
        Section("Privacy & Data") {
            Button(action: exportData) {
                Label("Export My Data", systemImage: "square.and.arrow.up")
            }

            Button(role: .destructive, action: { showDeleteConfirmation = true }) {
                Label("Delete All Data", systemImage: "trash")
            }

            HStack {
                Label("Data Storage", systemImage: "lock.shield")
                Spacer()
                Text("On-device only")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - About

    private var aboutSection: some View {
        Section("About") {
            HStack {
                Text("Version")
                Spacer()
                Text("1.0.0 (MVP)")
                    .foregroundColor(.secondary)
            }

            HStack {
                Text("Privacy")
                Spacer()
                Text("All data stays on your device")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Actions

    private func exportData() {
        guard let data = dataStore.exportData() else { return }
        let tempURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("burnout-data-export.json")
        try? data.write(to: tempURL)
        exportURL = tempURL
        showExportSheet = true
    }
}

/// UIKit share sheet wrapper
struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

#Preview {
    SettingsView()
        .environmentObject(AppState())
        .environmentObject(HealthKitService())
        .environmentObject(DataStore())
        .environmentObject(NotificationService())
}
