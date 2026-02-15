import SwiftUI

/// 10-second daily mood check-in screen
struct MoodCheckView: View {
    @EnvironmentObject var dataStore: DataStore
    @State private var selectedMood: MoodLevel?
    @State private var hasCheckedInToday = false
    @State private var showConfirmation = false
    @State private var animateSelection = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 32) {
                Spacer()

                if hasCheckedInToday {
                    checkedInView
                } else {
                    checkInView
                }

                Spacer()

                // Recent mood history
                recentMoodsSection
            }
            .padding()
            .navigationTitle("Mood Check")
            .onAppear {
                checkTodaysEntry()
            }
        }
    }

    // MARK: - Check In View

    private var checkInView: some View {
        VStack(spacing: 24) {
            Text("How are you feeling?")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Tap the emoji that matches your current state")
                .font(.subheadline)
                .foregroundColor(.secondary)

            // Mood selector
            HStack(spacing: 16) {
                ForEach(MoodLevel.allCases.reversed(), id: \.rawValue) { mood in
                    MoodButton(
                        mood: mood,
                        isSelected: selectedMood == mood,
                        action: { selectMood(mood) }
                    )
                }
            }

            if selectedMood != nil {
                Button(action: saveMood) {
                    Text("Save")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                }
                .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
    }

    // MARK: - Checked In View

    private var checkedInView: some View {
        VStack(spacing: 16) {
            if let todayEntry = dataStore.todaysMoodEntry() {
                Text(todayEntry.mood.emoji)
                    .font(.system(size: 80))

                Text("You checked in today")
                    .font(.title3)
                    .fontWeight(.medium)

                Text("Feeling \(todayEntry.mood.label.lowercased())")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                Text(todayEntry.date, style: .time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Recent Moods

    private var recentMoodsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("This Week")
                .font(.headline)

            let recentEntries = dataStore.recentMoodEntries(days: 7)

            if recentEntries.isEmpty {
                Text("No mood entries yet. Start checking in daily!")
                    .font(.caption)
                    .foregroundColor(.secondary)
            } else {
                HStack(spacing: 8) {
                    ForEach(recentEntries) { entry in
                        VStack(spacing: 4) {
                            Text(entry.mood.emoji)
                                .font(.title3)
                            Text(shortDay(entry.date))
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Actions

    private func selectMood(_ mood: MoodLevel) {
        withAnimation(.spring(response: 0.3)) {
            selectedMood = mood
        }
    }

    private func saveMood() {
        guard let mood = selectedMood else { return }
        let entry = MoodEntry(mood: mood)
        dataStore.saveMoodEntry(entry)

        withAnimation {
            hasCheckedInToday = true
            showConfirmation = true
        }
    }

    private func checkTodaysEntry() {
        hasCheckedInToday = dataStore.todaysMoodEntry() != nil
    }

    private func shortDay(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE"
        return formatter.string(from: date)
    }
}

// MARK: - Mood Button Component

struct MoodButton: View {
    let mood: MoodLevel
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Text(mood.emoji)
                    .font(.system(size: isSelected ? 44 : 36))

                Text(mood.label)
                    .font(.caption2)
                    .foregroundColor(isSelected ? .primary : .secondary)
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 4)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.blue.opacity(0.15) : Color.clear)
            )
            .scaleEffect(isSelected ? 1.1 : 1.0)
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    MoodCheckView()
        .environmentObject(DataStore())
}
